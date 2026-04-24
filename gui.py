#!/usr/bin/env python

import os
import sys
import urllib.parse
import requests

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMainWindow, QMessageBox, QListWidgetItem, QApplication, QComboBox, QFormLayout

from grocycode import create_codepage
from codesheet import create_codesheet
from modules.main_window import Ui_MainWindow
from modules.utils import check_or_load_login, get_bool_matrix, MAPPINGS

SCRIPTDIR = os.path.dirname(os.path.realpath(__file__)).removesuffix(__package__ if __package__ else "")
OUTDIR = os.path.join(SCRIPTDIR, "output")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # --- UI setup ---
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # --- Login / API init (same as main()) ---
        os.makedirs(OUTDIR, exist_ok=True)
        self.api_key, self.url = check_or_load_login()
        self.headers = {
            "accept": "application/json",
            "GROCY-API-KEY": self.api_key,
        }

        # --- Load products (same as main()) ---
        res = requests.get(
            self.url + "/api/objects/products",
            headers=self.headers,
        )
        self.products = sorted(res.json(), key=lambda x: x["name"])

        # --- UI population ---
        self._init_type_selection()
        self._init_stickers_page()
        self._init_list_page()

        # default view
        self.ui.flowStack.setCurrentIndex(0)

    # ------------------------------------------------------------------
    # TYPE SELECTION (questionary.select in main())
    # ------------------------------------------------------------------
    def _init_type_selection(self):
        self.ui.typeCombo.currentTextChanged.connect(self._on_type_changed)

    def _on_type_changed(self, text: str):
        if text == "stickers":
            self.ui.flowStack.setCurrentWidget(self.ui.stickersPage)
        elif text == "list":
            self.ui.flowStack.setCurrentWidget(self.ui.listPage)

    # ------------------------------------------------------------------
    # STICKERS FLOW (stickers())
    # ------------------------------------------------------------------
    def _init_stickers_page(self):
        combo = self.ui.productCombo
        combo.setEditable(True)
        combo.addItems([p["name"] for p in self.products])
        combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)

        self.ui.generateStickersButton.clicked.connect(self._generate_stickers)

    def _generate_stickers(self):
        product_name = self.ui.productCombo.currentText()
        if not product_name:
            return

        res = requests.get(
            f"{self.url}/api/objects/products",
            params={"query[]": f"name={product_name}"},
            headers=self.headers,
        )

        try:
            product_id = res.json()[0]["id"]
        except (IndexError, KeyError):
            QMessageBox.critical(
                self,
                "Error",
                f"Product not found: {product_name}",
            )
            return

        matrix = get_bool_matrix(product_id)
        create_codepage(
            matrix,
            os.path.join(OUTDIR, product_name + ".pdf"),
            product_name,
        )

        QMessageBox.information(
            self,
            "Done",
            "Stickers PDF generated successfully.",
        )

    # ------------------------------------------------------------------
    # LIST FLOW (lost())
    # ------------------------------------------------------------------
    def _init_list_page(self):
        # filter confirm
        self.ui.filterCheck.toggled.connect(self.ui.filterGroup.setVisible)

        # which filters?
        for key in MAPPINGS.keys():
            QListWidgetItem(key, self.ui.filterList)

        self.ui.filterList.itemSelectionChanged.connect(self._update_filter_value_inputs)

        self.ui.generateListButton.clicked.connect(self._generate_list)

        # data cache
        self.filtered_products = []

    def _update_filter_value_inputs(self):
        layout = self.ui.filterValuesLayout

        # clear previous inputs
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for item in self.ui.filterList.selectedItems():
            filt = item.text()

            res = requests.get(
                f"{self.url}/api/objects/{MAPPINGS[filt]}",
                headers=self.headers,
            )

            objects = sorted(res.json(), key=lambda x: x["name"])

            combo = self._create_combo(objects)
            layout.addRow(f"{filt}:", combo)

        # reload products after redefining filters
        self._reload_products()

    def _create_combo(self, objects):
        from PySide6.QtWidgets import QComboBox

        combo = QComboBox()
        for obj in objects:
            combo.addItem(obj["name"], obj["id"])
        combo.currentIndexChanged.connect(self._reload_products)
        return combo

    def _reload_products(self):
        queries = []
        layout = self.ui.filterValuesLayout

        for row in range(layout.rowCount()):
            label_item = layout.itemAt(row, QFormLayout.ItemRole.LabelRole)
            field_item = layout.itemAt(row, QFormLayout.ItemRole.FieldRole)

            # CRITICAL guard (Qt emits early)
            if not label_item or not field_item:
                continue

            label = label_item.widget().text().replace(":", "")

            combo = field_item.widget()
            value = combo.currentData()

            # ignore incomplete selections
            if value is None:
                return

            queries.append(f"{label}={value}")

        # No filters → behave exactly like Questionary
        if not queries:
            self.filtered_products = self.products
            self._populate_product_list()
            return

        res = requests.get(
            f"{self.url}/api/objects/products",
            params=[("query[]", q) for q in queries],
            headers=self.headers,
        )

        data = res.json()

        # CRITICAL validation (Grocy may return dict/string)
        if not isinstance(data, list):
            self.filtered_products = []
            self._populate_product_list()
            return

        self.filtered_products = sorted(data, key=lambda x: x.get("name", ""))

        self._populate_product_list()

    def _populate_product_list(self):
        self.ui.productList.clear()

        for idx, prod in enumerate(self.filtered_products):
            item = QListWidgetItem(prod["name"])
            item.setData(Qt.UserRole, idx)
            self.ui.productList.addItem(item)

    def _generate_list(self):
        selected = []

        for item in self.ui.productList.selectedItems():
            idx = item.data(Qt.UserRole)
            selected.append(self.filtered_products[idx])

        if not selected:
            return

        create_codesheet(
            selected,
            os.path.join(OUTDIR, "codesheet.pdf"),
        )

        QMessageBox.information(
            self,
            "Done",
            "Codesheet PDF generated successfully.",
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
