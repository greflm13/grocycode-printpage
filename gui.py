#!/usr/bin/env python

import os
import sys

import requests

from PySide6.QtCore import Qt, QUrl, QRegularExpression
from PySide6.QtWidgets import (
    QApplication,
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

from grocycode import create_codepage
from codesheet import create_codesheet
from modules.main_window import Ui_MainWindow
from modules.config_window import Ui_Dialog
from modules.utils import check_or_load_gui_login, save_login, get_bool_matrix, MAPPINGS, BASE_URL_RE, __version__

SCRIPTDIR = os.path.dirname(os.path.realpath(__file__)).removesuffix(__package__ if __package__ else "")
APP_ICON = QIcon(os.path.join(SCRIPTDIR, "assets", "icon.svg"))


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
                QMessageBox.critical(self, "Error", "API key and server URL are required.")
                sys.exit(1)

        self.headers = {
            "accept": "application/json",
            "GROCY-API-KEY": self.api_key,
        }

        res = requests.get(
            self.url + "/api/objects/products",
            headers=self.headers,
        )
        self.products = sorted(res.json(), key=lambda x: x["name"])

        self.ui.actionConfig.triggered.connect(self._show_login_dialog)
        self.ui.actionInfo.triggered.connect(self._show_info_dialog)

        self._init_type_selection()
        self._init_stickers_page()
        self._init_list_page()
        self._init_output_directory()

        self.ui.flowStack.setCurrentIndex(0)

    def _show_info_dialog(self) -> None:
        QMessageBox.about(
            self,
            "About GrocyCode Printpage",
            f"""
            <b>GrocyCode Printpage</b><br>
            Version: {__version__}<br><br>
            Generates sticker and codesheet PDFs for Grocy.
            """,
        )

    def _show_login_dialog(self) -> bool:
        curr_api_key, curr_url = check_or_load_gui_login()
        while True:
            dialog = LoginDialog(self)
            dialog.ui.apiKeyInput.setText(curr_api_key)
            dialog.ui.urlInput.setText(curr_url)

            if not dialog.exec():
                return False

            api_key, url, save = dialog.get_values()
            curr_api_key = api_key
            curr_url = url

            if not api_key or not url:
                QMessageBox.warning(self, "Invalid input", "Both API key and server URL are required.")
                continue

            try:
                res = requests.get(url + "/api/system/info", headers={"GROCY-API-KEY": api_key}, timeout=5)
                if res.status_code != 200:
                    QMessageBox.critical(self, "Connection failed", "API key is invalid.")
                    continue
            except requests.RequestException:
                QMessageBox.critical(self, "Connection failed", "URL is invalid.")
                continue

            self.api_key = api_key
            self.url = url

            if save:
                save_login(api_key, url)

            return True

    def _init_output_directory(self) -> None:
        default_output = os.path.join(os.getcwd(), "output")
        os.makedirs(default_output, exist_ok=True)

        self.ui.outputDir.setText(default_output)

        self.ui.outputDirChooser.clicked.connect(self._select_output_directory)

    def _select_output_directory(self) -> None:
        current = self.ui.outputDir.text()

        directory = QFileDialog.getExistingDirectory(self, "Select Output Directory", current)
        if not directory:
            return

        self.ui.outputDir.setText(directory)
        os.makedirs(directory, exist_ok=True)

    def _outdir(self) -> str:
        return self.ui.outputDir.text()

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

        for key in MAPPINGS.keys():
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

            res = requests.get(f"{self.url}/api/objects/{MAPPINGS[filt][0]}", headers=self.headers)

            objects = sorted(res.json(), key=lambda x: x["name"])

            combo = self._create_combo(objects)
            layout.addRow(f"{filt}:", combo)

        self._reload_products()

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

        res = requests.get(
            f"{self.url}/api/objects/products", params=[("query[]", q) for q in queries], headers=self.headers
        )

        data = res.json()

        if not isinstance(data, list):
            self.filtered_products = []
            self._populate_product_list()
            return

        self.filtered_products = sorted(data, key=lambda x: x.get("name", ""))

        self._populate_product_list()

    def _populate_product_list(self) -> None:
        self.ui.productList.clear()

        for idx, prod in enumerate(self.filtered_products):
            item = QListWidgetItem(prod["name"])
            item.setData(Qt.UserRole, idx)
            self.ui.productList.addItem(item)

    def _generate_stickers(self) -> None:
        product_name = self.ui.productCombo.currentText()
        if not product_name:
            return

        res = requests.get(
            f"{self.url}/api/objects/products", params={"query[]": f"name={product_name}"}, headers=self.headers
        )

        try:
            product_id = res.json()[0]["id"]
        except (IndexError, KeyError):
            QMessageBox.critical(self, "Error", f"Product not found: {product_name}")
            return

        outdir = self._outdir()
        matrix = get_bool_matrix(product_id)
        create_codepage(matrix, os.path.join(outdir, product_name + ".pdf"), product_name)
        self._show_pdf_done_dialog(os.path.join(outdir, "codesheet.pdf"), "Stickers PDF generated successfully.")

    def _generate_list(self) -> None:
        selected = []

        for item in self.ui.productList.selectedItems():
            idx = item.data(Qt.UserRole)
            selected.append(self.filtered_products[idx])

        if not selected:
            return

        outdir = self._outdir()
        create_codesheet(selected, os.path.join(outdir, "codesheet.pdf"))
        self._show_pdf_done_dialog(os.path.join(outdir, "codesheet.pdf"), "Codesheet PDF generated successfully.")

    def _show_pdf_done_dialog(self, pdf_path: str, title: str):
        msg = QMessageBox(self)
        msg.setWindowTitle("Done")
        msg.setText(title)
        msg.setIcon(QMessageBox.Icon.Information)

        open_button = msg.addButton("Open PDF", QMessageBox.ButtonRole.AcceptRole)
        msg.addButton("Close", QMessageBox.ButtonRole.RejectRole)

        msg.exec()

        if msg.clickedButton() == open_button:
            QDesktopServices.openUrl(QUrl.fromLocalFile(pdf_path))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationVersion(__version__)
    app.setWindowIcon(APP_ICON)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
