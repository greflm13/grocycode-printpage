# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'config.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QCheckBox, QDialog,
    QDialogButtonBox, QGridLayout, QLabel, QLineEdit,
    QSizePolicy, QSpacerItem, QWidget)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(400, 139)
        self.gridLayout_2 = QGridLayout(Dialog)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_2.addItem(self.verticalSpacer, 5, 1, 1, 1)

        self.apiKeyInput = QLineEdit(Dialog)
        self.apiKeyInput.setObjectName(u"apiKeyInput")
        self.apiKeyInput.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self.gridLayout_2.addWidget(self.apiKeyInput, 2, 1, 1, 1)

        self.label = QLabel(Dialog)
        self.label.setObjectName(u"label")

        self.gridLayout_2.addWidget(self.label, 0, 0, 1, 1)

        self.label_2 = QLabel(Dialog)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout_2.addWidget(self.label_2, 2, 0, 1, 1)

        self.showKey = QCheckBox(Dialog)
        self.showKey.setObjectName(u"showKey")

        self.gridLayout_2.addWidget(self.showKey, 2, 2, 1, 1)

        self.buttonBox = QDialogButtonBox(Dialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Ok)

        self.gridLayout_2.addWidget(self.buttonBox, 8, 0, 1, 3)

        self.urlInput = QLineEdit(Dialog)
        self.urlInput.setObjectName(u"urlInput")

        self.gridLayout_2.addWidget(self.urlInput, 0, 1, 1, 2)

        self.saveLogin = QCheckBox(Dialog)
        self.saveLogin.setObjectName(u"saveLogin")

        self.gridLayout_2.addWidget(self.saveLogin, 4, 1, 1, 2)

        QWidget.setTabOrder(self.urlInput, self.apiKeyInput)
        QWidget.setTabOrder(self.apiKeyInput, self.saveLogin)

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Config", None))
        self.label.setText(QCoreApplication.translate("Dialog", u"Grocy URL", None))
        self.label_2.setText(QCoreApplication.translate("Dialog", u"API Key", None))
        self.showKey.setText(QCoreApplication.translate("Dialog", u"Show?", None))
        self.urlInput.setPlaceholderText(QCoreApplication.translate("Dialog", u"https://grocy.example.com", None))
        self.saveLogin.setText(QCoreApplication.translate("Dialog", u"Save credentials", None))
    # retranslateUi

