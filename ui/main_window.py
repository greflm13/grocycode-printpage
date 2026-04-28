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
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QCheckBox, QComboBox,
    QFontComboBox, QFormLayout, QGroupBox, QHBoxLayout,
    QLabel, QLineEdit, QListWidget, QListWidgetItem,
    QMainWindow, QPushButton, QSizePolicy, QSpacerItem,
    QStackedWidget, QToolBar, QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(487, 445)
        self.actionConfig = QAction(MainWindow)
        self.actionConfig.setObjectName(u"actionConfig")
        self.actionConfig.setMenuRole(QAction.MenuRole.PreferencesRole)
        self.actionInfo = QAction(MainWindow)
        self.actionInfo.setObjectName(u"actionInfo")
        self.actionInfo.setMenuRole(QAction.MenuRole.AboutRole)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.mainLayout = QVBoxLayout(self.centralwidget)
        self.mainLayout.setObjectName(u"mainLayout")
        self.typeGroup = QGroupBox(self.centralwidget)
        self.typeGroup.setObjectName(u"typeGroup")
        self.horizontalLayout_2 = QHBoxLayout(self.typeGroup)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label0 = QLabel(self.typeGroup)
        self.label0.setObjectName(u"label0")

        self.horizontalLayout_2.addWidget(self.label0)

        self.typeCombo = QComboBox(self.typeGroup)
        self.typeCombo.addItem("")
        self.typeCombo.addItem("")
        self.typeCombo.setObjectName(u"typeCombo")

        self.horizontalLayout_2.addWidget(self.typeCombo)


        self.mainLayout.addWidget(self.typeGroup)

        self.fontGroup = QGroupBox(self.centralwidget)
        self.fontGroup.setObjectName(u"fontGroup")
        self.verticalLayout = QVBoxLayout(self.fontGroup)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.fontComboBox = QFontComboBox(self.fontGroup)
        self.fontComboBox.setObjectName(u"fontComboBox")
        self.fontComboBox.setCurrentText(u"")

        self.verticalLayout.addWidget(self.fontComboBox)


        self.mainLayout.addWidget(self.fontGroup)

        self.outputGroup = QGroupBox(self.centralwidget)
        self.outputGroup.setObjectName(u"outputGroup")
        self.horizontalLayout = QHBoxLayout(self.outputGroup)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.outputDir = QLineEdit(self.outputGroup)
        self.outputDir.setObjectName(u"outputDir")

        self.horizontalLayout.addWidget(self.outputDir)

        self.outputDirChooser = QPushButton(self.outputGroup)
        self.outputDirChooser.setObjectName(u"outputDirChooser")

        self.horizontalLayout.addWidget(self.outputDirChooser)


        self.mainLayout.addWidget(self.outputGroup)

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

        self.spacerItem = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.vboxLayout.addItem(self.spacerItem)

        self.generateStickersButton = QPushButton(self.stickersPage)
        self.generateStickersButton.setObjectName(u"generateStickersButton")

        self.vboxLayout.addWidget(self.generateStickersButton)

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
        self.toolBar = QToolBar(MainWindow)
        self.toolBar.setObjectName(u"toolBar")
        MainWindow.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.toolBar)

        self.toolBar.addAction(self.actionConfig)
        self.toolBar.addAction(self.actionInfo)

        self.retranslateUi(MainWindow)

        self.flowStack.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"GrocyCode Printpage", None))
        self.actionConfig.setText(QCoreApplication.translate("MainWindow", u"Config", None))
        self.actionInfo.setText(QCoreApplication.translate("MainWindow", u"Info", None))
        self.typeGroup.setTitle(QCoreApplication.translate("MainWindow", u"PDF Type", None))
        self.label0.setText(QCoreApplication.translate("MainWindow", u"Which type of pdf do you want to generate?", None))
        self.typeCombo.setItemText(0, QCoreApplication.translate("MainWindow", u"Stickers", None))
        self.typeCombo.setItemText(1, QCoreApplication.translate("MainWindow", u"List", None))

        self.fontGroup.setTitle(QCoreApplication.translate("MainWindow", u"Font", None))
        self.outputGroup.setTitle(QCoreApplication.translate("MainWindow", u"Output Directory", None))
        self.outputDirChooser.setText(QCoreApplication.translate("MainWindow", u"Browse...", None))
        self.label1.setText(QCoreApplication.translate("MainWindow", u"Product", None))
        self.generateStickersButton.setText(QCoreApplication.translate("MainWindow", u"Generate Stickers PDF", None))
        self.filterCheck.setText(QCoreApplication.translate("MainWindow", u"Filter list?", None))
        self.filterGroup.setTitle(QCoreApplication.translate("MainWindow", u"Filters", None))
        self.label2.setText(QCoreApplication.translate("MainWindow", u"Which filters?", None))
        self.filterValuesGroup.setTitle(QCoreApplication.translate("MainWindow", u"Filter values", None))
        self.label3.setText(QCoreApplication.translate("MainWindow", u"Products", None))
        self.generateListButton.setText(QCoreApplication.translate("MainWindow", u"Generate Codesheet PDF", None))
        self.toolBar.setWindowTitle(QCoreApplication.translate("MainWindow", u"toolBar", None))
    # retranslateUi

