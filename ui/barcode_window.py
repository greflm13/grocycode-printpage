# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'barcode.ui'
##
## Created by: Qt User Interface Compiler version 6.11.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QAbstractButton, QApplication, QDialog, QDialogButtonBox,
    QGridLayout, QHeaderView, QListWidget, QListWidgetItem,
    QPushButton, QSizePolicy, QTableView, QWidget)

class Ui_BarcodeAmountRemover(object):
    def setupUi(self, BarcodeAmountRemover):
        if not BarcodeAmountRemover.objectName():
            BarcodeAmountRemover.setObjectName(u"BarcodeAmountRemover")
        BarcodeAmountRemover.resize(585, 428)
        self.gridLayout = QGridLayout(BarcodeAmountRemover)
        self.gridLayout.setObjectName(u"gridLayout")
        self.tableView = QTableView(BarcodeAmountRemover)
        self.tableView.setObjectName(u"tableView")

        self.gridLayout.addWidget(self.tableView, 1, 1, 1, 1)

        self.getBarcodesButton = QPushButton(BarcodeAmountRemover)
        self.getBarcodesButton.setObjectName(u"getBarcodesButton")

        self.gridLayout.addWidget(self.getBarcodesButton, 0, 1, 1, 1)

        self.removeAmountButton = QPushButton(BarcodeAmountRemover)
        self.removeAmountButton.setObjectName(u"removeAmountButton")

        self.gridLayout.addWidget(self.removeAmountButton, 2, 1, 1, 1)

        self.buttonBox = QDialogButtonBox(BarcodeAmountRemover)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Close)

        self.gridLayout.addWidget(self.buttonBox, 4, 1, 1, 1)

        self.messageList = QListWidget(BarcodeAmountRemover)
        self.messageList.setObjectName(u"messageList")
        self.messageList.setEnabled(True)

        self.gridLayout.addWidget(self.messageList, 3, 1, 1, 1)


        self.retranslateUi(BarcodeAmountRemover)
        self.buttonBox.accepted.connect(BarcodeAmountRemover.accept)
        self.buttonBox.rejected.connect(BarcodeAmountRemover.reject)

        QMetaObject.connectSlotsByName(BarcodeAmountRemover)
    # setupUi

    def retranslateUi(self, BarcodeAmountRemover):
        BarcodeAmountRemover.setWindowTitle(QCoreApplication.translate("BarcodeAmountRemover", u"Barcode amount remover", None))
        self.getBarcodesButton.setText(QCoreApplication.translate("BarcodeAmountRemover", u"Get Barcodes", None))
        self.removeAmountButton.setText(QCoreApplication.translate("BarcodeAmountRemover", u"Remove amounts from Barcodes", None))
    # retranslateUi

