#!/usr/bin/env python

import os
import sys
import json
import hashlib

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PySide6.QtCore import (
    Qt,
    QUrl,
    QObject,
    QByteArray,
    QEventLoop,
    QRegularExpression,
    QAbstractTableModel,
)
from PySide6.QtWidgets import (
    QComboBox,
    QCompleter,
    QDialog,
    QFileDialog,
    QFormLayout,
    QLineEdit,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
)
from PySide6.QtGui import QIcon, QDesktopServices, QRegularExpressionValidator
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply

import ui.resources_rc  # noqa: F401
from grocycode import create_codepage
from codesheet import create_codesheet
from ui.main_window import Ui_MainWindow
from ui.config_window import Ui_Dialog
from ui.barcode_window import Ui_BarcodeAmountRemover
from modules.utils import (
    check_or_load_gui_login,
    index_by_key,
    save_login,
    get_bool_matrix,
    find_system_font_file,
    get_version,
    MAPPINGS,
    BASE_URL_RE,
)

SCRIPTDIR = os.path.dirname(os.path.realpath(__file__)).removesuffix(__package__ if __package__ else "")
APP_ICON = QIcon(":/assets/icon.svg")


class BarcodeTableModel(QAbstractTableModel):
    def __init__(self, barcodes, parent=None):
        super().__init__(parent)
        self.barcodes = barcodes
        self.columns = [
            "id",
            "product_id",
            "barcode",
            "qu_id",
            "amount",
            "shopping_location_id",
            "last_price",
            "row_created_timestamp",
            "note",
        ]

    def rowCount(self, parent=None):
        return len(self.barcodes)

    def columnCount(self, parent=None):
        return len(self.columns)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None

        if role == Qt.DisplayRole:
            value = self.barcodes[index.row()].get(self.columns[index.column()], "")
            return str(value)

        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self.columns[section]
            return section + 1
        return None


class ApiClient(QObject):
    def __init__(self, base_url: str, headers: dict, parent=None):
        super().__init__(parent)
        self.base_url = base_url.rstrip("/")
        self.headers = headers
        self.net = QNetworkAccessManager(self)

    def get(self, path: str, *, query=None, callback=None):
        url = QUrl(self.base_url + path)

        if query:
            if isinstance(query.get("query[]"), list):
                url.setQuery("&".join(f"query[]={q}" for q in query["query[]"]))
            else:
                url.setQuery("&".join(f"{k}={v}" for k, v in query.items()))

        request = QNetworkRequest(url)
        request.setHeader(QNetworkRequest.ContentTypeHeader, "application/json")

        for k, v in self.headers.items():
            request.setRawHeader(k.encode(), v.encode())

        reply = self.net.get(request)

        def finished():
            if reply.error() != QNetworkReply.NetworkError.NoError:
                QMessageBox.critical(
                    None,
                    self.tr("Network error"),
                    f"{reply.errorString()}",
                )
                reply.deleteLater()
                return

            status = reply.attribute(QNetworkRequest.HttpStatusCodeAttribute)
            if status is not None and int(status) >= 400:
                QMessageBox.critical(
                    None,
                    self.tr("HTTP error"),
                    f"Server returned HTTP {status}",
                )
                reply.deleteLater()
                return

            try:
                data = json.loads(bytes(reply.readAll()))
            except json.JSONDecodeError:
                QMessageBox.critical(
                    None,
                    self.tr("Error"),
                    "Invalid JSON response from server",
                )
                reply.deleteLater()
                return

            if callback:
                callback(data)

            reply.deleteLater()

        reply.finished.connect(finished)

    def put(self, path: str, *, payload=None, callback=None):
        url = QUrl(self.base_url + path)

        request = QNetworkRequest(url)
        request.setHeader(QNetworkRequest.ContentTypeHeader, "application/json")
        request.setRawHeader(b"accept", b"application/json")

        for k, v in self.headers.items():
            request.setRawHeader(k.encode(), v.encode())

        body = QByteArray()
        if payload is not None:
            body = QByteArray(json.dumps(payload).encode("utf-8"))

        reply = self.net.put(request, body)

        def finished():
            if reply.error() != QNetworkReply.NetworkError.NoError:
                QMessageBox.critical(
                    None,
                    self.tr("Network error"),
                    reply.errorString(),
                )
                reply.deleteLater()
                return

            status = reply.attribute(QNetworkRequest.HttpStatusCodeAttribute)
            if status is not None and int(status) >= 400:
                QMessageBox.critical(
                    None,
                    self.tr("HTTP error"),
                    f"Server returned HTTP {status}",
                )
                reply.deleteLater()
                return

            raw = bytes(reply.readAll()).strip()
            if raw:
                try:
                    data = json.loads(raw)
                except json.JSONDecodeError:
                    QMessageBox.critical(
                        None,
                        self.tr("Error"),
                        "Invalid JSON response from server",
                    )
                    reply.deleteLater()
                    return
            else:
                data = None

            if callback:
                callback(data)

            reply.deleteLater()

        reply.finished.connect(finished)


class BarcodeAmountRemover(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.ui = Ui_BarcodeAmountRemover()
        self.ui.setupUi(self)
        self.setWindowIcon(APP_ICON)
        self.api_key, self.url = check_or_load_gui_login()

        if not self.api_key or not self.url:
            if not self._show_login_dialog():
                QMessageBox.critical(self, self.tr("Error"), self.tr("API key and server URL are required."))
                sys.exit(1)

        self.headers = {
            "GROCY-API-KEY": self.api_key,
        }

        self.api = ApiClient(self.url, self.headers, self)

        self.ui.getBarcodesButton.clicked.connect(self._get_barcodes)
        self.ui.removeAmountButton.clicked.connect(self._remove_amount)
        self.ui.messageList.hide()

    def _get_barcodes(self):
        self.api.get(
            "/api/objects/product_barcodes",
            callback=lambda data: self._on_barcodes_loaded(data),
        )
        self.api.get(
            "/api/objects/products",
            callback=lambda data: self._on_products_loaded(data),
        )

    def _on_barcodes_loaded(self, data):
        self.barcodes = data

        model = BarcodeTableModel(self.barcodes)
        self.ui.tableView.setModel(model)
        self.ui.tableView.resizeColumnsToContents()

    def _on_products_loaded(self, data):
        self.products = data

    def _remove_amount(self):
        products = index_by_key(self.products, "id")
        self.ui.messageList.clear()
        self.ui.messageList.show()

        for barcode in self.barcodes:
            if barcode["amount"] is not None:
                self.ui.messageList.addItem(
                    f'removing barcode amount "{barcode["amount"]}" from product "{products[barcode["product_id"]]["name"]}" barcode {barcode["barcode"]}'
                )
                self.api.put(
                    f"/api/objects/product_barcodes/{barcode['id']}",
                    payload={
                        "id": barcode["id"],
                        "product_id": barcode["product_id"],
                        "barcode": barcode["barcode"],
                        "qu_id": barcode["qu_id"],
                        "amount": None,
                        "shopping_location_id": barcode["shopping_location_id"],
                        "last_price": barcode["last_price"],
                        "note": barcode["note"],
                    },
                )


class LoginDialog(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.setWindowIcon(APP_ICON)

        self.ui.showKey.stateChanged.connect(self._toggle_key_visibility)
        self.ui.apiKeyInput.setEchoMode(QLineEdit.Password)
        self.ui.urlInput.setValidator(QRegularExpressionValidator(QRegularExpression(BASE_URL_RE.pattern)))

    def _toggle_key_visibility(self) -> None:
        visible = self.ui.showKey.isChecked()
        if visible:
            self.ui.apiKeyInput.setEchoMode(QLineEdit.Normal)
        else:
            self.ui.apiKeyInput.setEchoMode(QLineEdit.Password)

    def get_values(self) -> tuple[str, str, bool]:
        return (
            self.ui.apiKeyInput.text().strip(),
            self.ui.urlInput.text().strip().rstrip("/"),
            self.ui.saveLogin.isChecked(),
        )


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowIcon(APP_ICON)

        self.api_key, self.url = check_or_load_gui_login()

        if not self.api_key or not self.url:
            if not self._show_login_dialog():
                QMessageBox.critical(self, self.tr("Error"), self.tr("API key and server URL are required."))
                sys.exit(1)

        self.headers = {
            "GROCY-API-KEY": self.api_key,
        }

        self.api = ApiClient(self.url, self.headers, self)

        self.api.get(
            "/api/objects/products",
            callback=lambda data: self._on_products_loaded(data),
        )

        self.ui.fontComboBox.currentFontChanged.connect(self._change_font)
        self.ui.actionConfig.triggered.connect(self._show_login_dialog)
        self.ui.actionInfo.triggered.connect(self._show_info_dialog)
        self.ui.actionBarcode.triggered.connect(self._show_barcode_amount_remover)

        self._change_font()
        self._init_type_selection()
        self._init_output_directory()
        self.ui.flowStack.setCurrentIndex(0)

    def _on_products_loaded(self, data):
        self.products = sorted(data, key=lambda x: x["name"])
        self._init_stickers_page()
        self._init_list_page()
        self._reload_products()

    def _on_filter_objects_loaded(self, filt, data):
        objects = sorted(data, key=lambda x: x["name"])
        combo = self._create_combo(objects)
        self.ui.filterValuesLayout.addRow(f"{filt}:", combo)
        self._reload_products()

    def _on_filtered_products_loaded(self, data):
        self.filtered_products = sorted(data, key=lambda x: x.get("name", ""))
        self._populate_product_list()

    def _on_sticker_product_loaded(self, product_name, data):
        try:
            product_id = data[0]["id"]
        except (IndexError, KeyError):
            QMessageBox.critical(self, self.tr("Error"), self.tr(f"Product not found: {product_name}"))
            return

        outdir = self._outdir()
        matrix = get_bool_matrix(product_id)
        create_codepage(matrix, os.path.join(outdir, product_name + ".pdf"), product_name, self.currentFont)
        self._show_pdf_done_dialog(os.path.join(outdir, product_name + ".pdf"), "Stickers PDF generated successfully.")
        self.ui.generateStickersButton.setDisabled(False)

    def _show_barcode_amount_remover(self) -> None:
        dialog = BarcodeAmountRemover(self)
        dialog.exec()

    def _show_login_dialog(self) -> bool:
        curr_api_key, curr_url = check_or_load_gui_login()

        while True:
            dialog = LoginDialog(self)
            dialog.ui.apiKeyInput.setText(curr_api_key)
            dialog.ui.urlInput.setText(curr_url)

            if not dialog.exec():
                return False

            api_key, url, save = dialog.get_values()
            curr_api_key, curr_url = api_key, url

            if not api_key or not url:
                QMessageBox.warning(
                    self,
                    self.tr("Invalid input"),
                    self.tr("Both API key and server URL are required."),
                )
                continue

            mgr = QNetworkAccessManager(self)
            req = QNetworkRequest(QUrl(url + "/api/system/info"))
            req.setHeader(QNetworkRequest.ContentTypeHeader, "application/json")
            req.setRawHeader(b"GROCY-API-KEY", api_key.encode())

            reply = mgr.get(req)
            loop = QEventLoop()
            reply.finished.connect(loop.quit)
            loop.exec()

            if reply.error() != QNetworkReply.NetworkError.NoError:
                QMessageBox.critical(
                    self,
                    self.tr("Connection failed"),
                    reply.errorString(),
                )
                reply.deleteLater()
                continue

            status = reply.attribute(QNetworkRequest.HttpStatusCodeAttribute)
            if status is not None and int(status) != 200:
                QMessageBox.critical(
                    self,
                    self.tr("Connection failed"),
                    self.tr(f"Server returned HTTP {status}"),
                )
                reply.deleteLater()
                continue

            reply.deleteLater()

            self.api_key, self.url = api_key, url
            if save:
                save_login(api_key, url)

            return True

    def _show_info_dialog(self) -> None:
        QMessageBox.about(
            self,
            self.tr("About GrocyCode Printpage"),
            self.tr(f"""
            <b>GrocyCode Printpage</b><br>
            Version: {get_version()}<br><br>
            Generates sticker and codesheet PDFs for Grocy.
            """),
        )

    def _change_font(self) -> None:
        font = self.ui.fontComboBox.currentFont()

        family = font.family()
        weight = font.weight()
        italic = font.italic()


        font_path = find_system_font_file(family, weight, italic)

        key = f"{font_path}".encode()
        font_id = hashlib.md5(key).hexdigest()[:8]
        self.currentFont = font_id

        if font_id not in pdfmetrics.getRegisteredFontNames():
            pdfmetrics.registerFont(TTFont(font_id, font_path))

    def _init_output_directory(self) -> None:
        default_output = os.path.join(os.getcwd(), "output")

        self.ui.outputDir.setText(default_output)

        self.ui.outputDirChooser.clicked.connect(self._select_output_directory)

    def _select_output_directory(self) -> None:
        directory = QFileDialog.getExistingDirectory(self, "Select Output Directory", self.ui.outputDir.text())
        if directory:
            self.ui.outputDir.setText(directory)

    def _outdir(self) -> str:
        directory = self.ui.outputDir.text()
        os.makedirs(directory, exist_ok=True)
        return directory

    def _init_type_selection(self) -> None:
        self.ui.typeCombo.currentTextChanged.connect(self._on_type_changed)

    def _on_type_changed(self, text: str) -> None:
        if text == "Stickers":
            self.ui.flowStack.setCurrentWidget(self.ui.stickersPage)
        elif text == "List":
            self.ui.flowStack.setCurrentWidget(self.ui.listPage)

    def _init_stickers_page(self) -> None:
        combo = self.ui.productCombo
        combo.setEditable(True)
        items = [p["name"] for p in self.products]
        combo.addItems(items)
        combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        completer = QCompleter(items, self)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        combo.setCompleter(completer)
        combo.setEditText("")

        self.ui.generateStickersButton.clicked.connect(self._generate_stickers)

    def _init_list_page(self) -> None:
        self.ui.filterCheck.toggled.connect(self.ui.filterGroup.setVisible)
        for key in MAPPINGS:
            QListWidgetItem(key, self.ui.filterList)

        self.ui.filterList.itemSelectionChanged.connect(self._update_filter_value_inputs)
        self.ui.generateListButton.clicked.connect(self._generate_list)
        self.filtered_products = []

    def _update_filter_value_inputs(self) -> None:
        layout = self.ui.filterValuesLayout

        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for item in self.ui.filterList.selectedItems():
            filt = item.text()
            self.api.get(
                f"/api/objects/{MAPPINGS[filt][0]}",
                callback=lambda data, f=filt: self._on_filter_objects_loaded(f, data),
            )

    def _create_combo(self, objects) -> QComboBox:
        combo = QComboBox()
        for obj in objects:
            combo.addItem(obj["name"], obj["id"])
        combo.setEditable(True)
        completer = QCompleter([obj["name"] for obj in objects])
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        combo.setCompleter(completer)
        combo.setEditText("")
        combo.currentIndexChanged.connect(self._reload_products)
        return combo

    def _reload_products(self) -> None:
        queries = []
        layout = self.ui.filterValuesLayout

        for row in range(layout.rowCount()):
            label_item = layout.itemAt(row, QFormLayout.ItemRole.LabelRole)
            field_item = layout.itemAt(row, QFormLayout.ItemRole.FieldRole)

            if not label_item or not field_item:
                continue

            label = label_item.widget().text().replace(":", "")

            combo = field_item.widget()
            value = combo.currentData()

            if value is None:
                return

            queries.append(f"{MAPPINGS[label][1]}={value}")

        if not queries:
            self.filtered_products = self.products
            self._populate_product_list()
            return

        self.api.get(
            "/api/objects/products",
            query={"query[]": queries},
            callback=lambda data: self._on_filtered_products_loaded(data),
        )

    def _populate_product_list(self) -> None:
        self.ui.productList.clear()

        for idx, prod in enumerate(self.filtered_products):
            item = QListWidgetItem(prod["name"])
            item.setData(Qt.UserRole, idx)
            self.ui.productList.addItem(item)

    def _generate_stickers(self) -> None:
        self.ui.generateStickersButton.setDisabled(True)
        product_name = self.ui.productCombo.currentText()
        if not product_name:
            QMessageBox.warning(
                self, self.tr("Product missing"), self.tr("Please select product to generate stickers for.")
            )
            self.ui.generateStickersButton.setDisabled(False)
            return

        self.api.get(
            "/api/objects/products",
            query={"query[]": f"name={product_name}"},
            callback=lambda data, n=product_name: self._on_sticker_product_loaded(n, data),
        )

    def _generate_list(self) -> None:
        self.ui.generateListButton.setDisabled(True)
        selected = []

        for item in self.ui.productList.selectedItems():
            idx = item.data(Qt.UserRole)
            selected.append(self.filtered_products[idx])

        if not selected:
            QMessageBox.warning(
                self, self.tr("Product(s) missing"), self.tr("Please select product(s) to generate list for.")
            )
            self.ui.generateListButton.setDisabled(False)
            return

        outdir = self._outdir()
        create_codesheet(selected, os.path.join(outdir, "codesheet.pdf"), self.currentFont)
        self._show_pdf_done_dialog(os.path.join(outdir, "codesheet.pdf"), "Codesheet PDF generated successfully.")
        self.ui.generateListButton.setDisabled(False)

    def _show_pdf_done_dialog(self, pdf_path: str, title: str):
        msg = QMessageBox(self)
        msg.setWindowTitle(self.tr("Done"))
        msg.setText(title)
        msg.setIcon(QMessageBox.Icon.Information)

        open_button = msg.addButton(self.tr("Open PDF"), QMessageBox.ButtonRole.AcceptRole)
        msg.addButton(self.tr("Close"), QMessageBox.ButtonRole.RejectRole)

        msg.exec()

        if msg.clickedButton() == open_button:
            QDesktopServices.openUrl(QUrl.fromLocalFile(pdf_path))
