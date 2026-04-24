# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main.ui'
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
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QCheckBox, QComboBox,
    QFormLayout, QGroupBox, QHBoxLayout, QLabel,
    QListWidget, QListWidgetItem, QMainWindow, QPushButton,
    QSizePolicy, QSpacerItem, QStackedWidget, QVBoxLayout,
    QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(368, 385)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.mainLayout = QVBoxLayout(self.centralwidget)
        self.mainLayout.setObjectName(u"mainLayout")
        self.typeGroup = QGroupBox(self.centralwidget)
        self.typeGroup.setObjectName(u"typeGroup")
        self.hboxLayout = QHBoxLayout(self.typeGroup)
        self.hboxLayout.setObjectName(u"hboxLayout")
        self.label = QLabel(self.typeGroup)
        self.label.setObjectName(u"label")

        self.hboxLayout.addWidget(self.label)

        self.typeCombo = QComboBox(self.typeGroup)
        self.typeCombo.addItem("")
        self.typeCombo.addItem("")
        self.typeCombo.setObjectName(u"typeCombo")

        self.hboxLayout.addWidget(self.typeCombo)


        self.mainLayout.addWidget(self.typeGroup)

        self.flowStack = QStackedWidget(self.centralwidget)
        self.flowStack.setObjectName(u"flowStack")
        self.stickersPage = QWidget()
        self.stickersPage.setObjectName(u"stickersPage")
        self.vboxLayout = QVBoxLayout(self.stickersPage)
        self.vboxLayout.setObjectName(u"vboxLayout")
        self.label1 = QLabel(self.stickersPage)
        self.label1.setObjectName(u"label1")

        self.vboxLayout.addWidget(self.label1)

        self.productCombo = QComboBox(self.stickersPage)
        self.productCombo.setObjectName(u"productCombo")
        self.productCombo.setEditable(True)

        self.vboxLayout.addWidget(self.productCombo)

        self.generateStickersButton = QPushButton(self.stickersPage)
        self.generateStickersButton.setObjectName(u"generateStickersButton")

        self.vboxLayout.addWidget(self.generateStickersButton)

        self.spacerItem = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.vboxLayout.addItem(self.spacerItem)

        self.flowStack.addWidget(self.stickersPage)
        self.listPage = QWidget()
        self.listPage.setObjectName(u"listPage")
        self.vboxLayout1 = QVBoxLayout(self.listPage)
        self.vboxLayout1.setObjectName(u"vboxLayout1")
        self.filterCheck = QCheckBox(self.listPage)
        self.filterCheck.setObjectName(u"filterCheck")

        self.vboxLayout1.addWidget(self.filterCheck)

        self.filterGroup = QGroupBox(self.listPage)
        self.filterGroup.setObjectName(u"filterGroup")
        self.filterGroup.setVisible(False)
        self.vboxLayout2 = QVBoxLayout(self.filterGroup)
        self.vboxLayout2.setObjectName(u"vboxLayout2")
        self.label2 = QLabel(self.filterGroup)
        self.label2.setObjectName(u"label2")

        self.vboxLayout2.addWidget(self.label2)

        self.filterList = QListWidget(self.filterGroup)
        self.filterList.setObjectName(u"filterList")
        self.filterList.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)

        self.vboxLayout2.addWidget(self.filterList)

        self.filterValuesGroup = QGroupBox(self.filterGroup)
        self.filterValuesGroup.setObjectName(u"filterValuesGroup")
        self.filterValuesLayout = QFormLayout(self.filterValuesGroup)
        self.filterValuesLayout.setObjectName(u"filterValuesLayout")

        self.vboxLayout2.addWidget(self.filterValuesGroup)


        self.vboxLayout1.addWidget(self.filterGroup)

        self.label3 = QLabel(self.listPage)
        self.label3.setObjectName(u"label3")

        self.vboxLayout1.addWidget(self.label3)

        self.productList = QListWidget(self.listPage)
        self.productList.setObjectName(u"productList")
        self.productList.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)

        self.vboxLayout1.addWidget(self.productList)

        self.generateListButton = QPushButton(self.listPage)
        self.generateListButton.setObjectName(u"generateListButton")

        self.vboxLayout1.addWidget(self.generateListButton)

        self.flowStack.addWidget(self.listPage)

        self.mainLayout.addWidget(self.flowStack)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        self.flowStack.setCurrentIndex(1)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"PDF Generator", None))
        self.typeGroup.setTitle(QCoreApplication.translate("MainWindow", u"PDF Type", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"Which type of pdf do you want to generate?", None))
        self.typeCombo.setItemText(0, QCoreApplication.translate("MainWindow", u"stickers", None))
        self.typeCombo.setItemText(1, QCoreApplication.translate("MainWindow", u"list", None))

        self.label1.setText(QCoreApplication.translate("MainWindow", u"Product", None))
        self.generateStickersButton.setText(QCoreApplication.translate("MainWindow", u"Generate Stickers PDF", None))
        self.filterCheck.setText(QCoreApplication.translate("MainWindow", u"Filter list?", None))
        self.filterGroup.setTitle(QCoreApplication.translate("MainWindow", u"Filters", None))
        self.label2.setText(QCoreApplication.translate("MainWindow", u"Which filters?", None))
        self.filterValuesGroup.setTitle(QCoreApplication.translate("MainWindow", u"Filter values", None))
        self.label3.setText(QCoreApplication.translate("MainWindow", u"Products", None))
        self.generateListButton.setText(QCoreApplication.translate("MainWindow", u"Generate Codesheet PDF", None))
    # retranslateUi

