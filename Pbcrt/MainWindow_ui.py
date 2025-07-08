# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'MainWindow.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
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
from PySide6.QtWidgets import (QApplication, QFrame, QGridLayout, QGroupBox,
    QHBoxLayout, QHeaderView, QLabel, QLineEdit,
    QMainWindow, QMenu, QMenuBar, QPushButton,
    QSizePolicy, QSpacerItem, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1144, 938)
        self.actionAppConfigSava = QAction(MainWindow)
        self.actionAppConfigSava.setObjectName(u"actionAppConfigSava")
        self.actionAppConfigSavaAs = QAction(MainWindow)
        self.actionAppConfigSavaAs.setObjectName(u"actionAppConfigSavaAs")
        self.imgOutPathConfigAction = QAction(MainWindow)
        self.imgOutPathConfigAction.setObjectName(u"imgOutPathConfigAction")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayout_3 = QGridLayout(self.centralwidget)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.gBoxImages = QGroupBox(self.centralwidget)
        self.gBoxImages.setObjectName(u"gBoxImages")
        self.gridLayout = QGridLayout(self.gBoxImages)
        self.gridLayout.setObjectName(u"gridLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.qLabelSrcImage = QLabel(self.gBoxImages)
        self.qLabelSrcImage.setObjectName(u"qLabelSrcImage")
        self.qLabelSrcImage.setMinimumSize(QSize(30, 20))
        self.qLabelSrcImage.setFrameShape(QFrame.Shape.Box)
        self.qLabelSrcImage.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.qLabelSrcImage.setMargin(0)

        self.horizontalLayout.addWidget(self.qLabelSrcImage)

        self.qLabelResImage = QLabel(self.gBoxImages)
        self.qLabelResImage.setObjectName(u"qLabelResImage")
        self.qLabelResImage.setMinimumSize(QSize(30, 20))
        self.qLabelResImage.setFrameShape(QFrame.Shape.Box)
        self.qLabelResImage.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout.addWidget(self.qLabelResImage)

        self.horizontalLayout.setStretch(0, 1)
        self.horizontalLayout.setStretch(1, 1)

        self.gridLayout.addLayout(self.horizontalLayout, 0, 0, 1, 1)


        self.horizontalLayout_6.addWidget(self.gBoxImages)

        self.horizontalLayout_6.setStretch(0, 6)

        self.verticalLayout_3.addLayout(self.horizontalLayout_6)

        self.horizontalLayout_8 = QHBoxLayout()
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.qTableYoloRes = QTableWidget(self.centralwidget)
        self.qTableYoloRes.setObjectName(u"qTableYoloRes")

        self.horizontalLayout_8.addWidget(self.qTableYoloRes)

        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.groupBox = QGroupBox(self.centralwidget)
        self.groupBox.setObjectName(u"groupBox")
        self.gridLayout_4 = QGridLayout(self.groupBox)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label_4 = QLabel(self.groupBox)
        self.label_4.setObjectName(u"label_4")

        self.horizontalLayout_2.addWidget(self.label_4)

        self.qLineEditLocalIpv4 = QLineEdit(self.groupBox)
        self.qLineEditLocalIpv4.setObjectName(u"qLineEditLocalIpv4")

        self.horizontalLayout_2.addWidget(self.qLineEditLocalIpv4)

        self.horizontalLayout_2.setStretch(0, 2)
        self.horizontalLayout_2.setStretch(1, 7)

        self.gridLayout_4.addLayout(self.horizontalLayout_2, 0, 0, 1, 1)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.label_5 = QLabel(self.groupBox)
        self.label_5.setObjectName(u"label_5")

        self.horizontalLayout_3.addWidget(self.label_5)

        self.qLineEditLocalPort = QLineEdit(self.groupBox)
        self.qLineEditLocalPort.setObjectName(u"qLineEditLocalPort")

        self.horizontalLayout_3.addWidget(self.qLineEditLocalPort)

        self.horizontalLayout_3.setStretch(0, 2)
        self.horizontalLayout_3.setStretch(1, 7)

        self.gridLayout_4.addLayout(self.horizontalLayout_3, 1, 0, 1, 1)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.label_6 = QLabel(self.groupBox)
        self.label_6.setObjectName(u"label_6")

        self.horizontalLayout_4.addWidget(self.label_6)

        self.qLineEditRemoteIpv4 = QLineEdit(self.groupBox)
        self.qLineEditRemoteIpv4.setObjectName(u"qLineEditRemoteIpv4")

        self.horizontalLayout_4.addWidget(self.qLineEditRemoteIpv4)

        self.horizontalLayout_4.setStretch(0, 2)
        self.horizontalLayout_4.setStretch(1, 7)

        self.gridLayout_4.addLayout(self.horizontalLayout_4, 2, 0, 1, 1)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.label_7 = QLabel(self.groupBox)
        self.label_7.setObjectName(u"label_7")

        self.horizontalLayout_5.addWidget(self.label_7)

        self.qLineEditRemotePort = QLineEdit(self.groupBox)
        self.qLineEditRemotePort.setObjectName(u"qLineEditRemotePort")

        self.horizontalLayout_5.addWidget(self.qLineEditRemotePort)

        self.horizontalLayout_5.setStretch(0, 2)
        self.horizontalLayout_5.setStretch(1, 7)

        self.gridLayout_4.addLayout(self.horizontalLayout_5, 3, 0, 1, 1)

        self.horizontalLayout_7 = QHBoxLayout()
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_7.addItem(self.horizontalSpacer)

        self.qButtonDeleteTableRow = QPushButton(self.groupBox)
        self.qButtonDeleteTableRow.setObjectName(u"qButtonDeleteTableRow")

        self.horizontalLayout_7.addWidget(self.qButtonDeleteTableRow)

        self.qButtonUdpNetConn = QPushButton(self.groupBox)
        self.qButtonUdpNetConn.setObjectName(u"qButtonUdpNetConn")
        self.qButtonUdpNetConn.setMinimumSize(QSize(0, 0))

        self.horizontalLayout_7.addWidget(self.qButtonUdpNetConn)

        self.qButtonGetImage = QPushButton(self.groupBox)
        self.qButtonGetImage.setObjectName(u"qButtonGetImage")

        self.horizontalLayout_7.addWidget(self.qButtonGetImage)


        self.gridLayout_4.addLayout(self.horizontalLayout_7, 4, 0, 1, 1)


        self.verticalLayout_2.addWidget(self.groupBox)

        self.verticalLayout_2.setStretch(0, 10)

        self.horizontalLayout_8.addLayout(self.verticalLayout_2)

        self.horizontalLayout_8.setStretch(0, 6)
        self.horizontalLayout_8.setStretch(1, 2)

        self.verticalLayout_3.addLayout(self.horizontalLayout_8)

        self.verticalLayout_3.setStretch(0, 4)
        self.verticalLayout_3.setStretch(1, 1)

        self.gridLayout_3.addLayout(self.verticalLayout_3, 0, 0, 1, 1)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menuBar = QMenuBar(MainWindow)
        self.menuBar.setObjectName(u"menuBar")
        self.menuBar.setGeometry(QRect(0, 0, 1144, 21))
        self.appSettingMenu = QMenu(self.menuBar)
        self.appSettingMenu.setObjectName(u"appSettingMenu")
        MainWindow.setMenuBar(self.menuBar)

        self.menuBar.addAction(self.appSettingMenu.menuAction())
        self.appSettingMenu.addAction(self.imgOutPathConfigAction)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.actionAppConfigSava.setText(QCoreApplication.translate("MainWindow", u"\u4fdd\u5b58", None))
        self.actionAppConfigSavaAs.setText(QCoreApplication.translate("MainWindow", u"\u53e6\u5b58\u4e3a", None))
        self.imgOutPathConfigAction.setText(QCoreApplication.translate("MainWindow", u"\u9009\u62e9\u8f93\u51fa\u8def\u5f84", None))
        self.gBoxImages.setTitle(QCoreApplication.translate("MainWindow", u"\u56fe\u50cf\u4fe1\u606f", None))
        self.qLabelSrcImage.setText(QCoreApplication.translate("MainWindow", u"\u539f\u59cb\u56fe\u50cf\u663e\u793a", None))
        self.qLabelResImage.setText(QCoreApplication.translate("MainWindow", u"\u5904\u7406\u56fe\u50cf\u663e\u793a", None))
        self.groupBox.setTitle(QCoreApplication.translate("MainWindow", u"Network\u4fe1\u606f", None))
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"\u672c\u5730IPV4", None))
        self.qLineEditLocalIpv4.setText(QCoreApplication.translate("MainWindow", u"192.168.200.100", None))
        self.label_5.setText(QCoreApplication.translate("MainWindow", u"\u672c\u5730\u7aef\u53e3", None))
        self.qLineEditLocalPort.setText(QCoreApplication.translate("MainWindow", u"12021", None))
        self.label_6.setText(QCoreApplication.translate("MainWindow", u"\u8bbe\u5907IPV4", None))
        self.qLineEditRemoteIpv4.setText(QCoreApplication.translate("MainWindow", u"192.168.200.200", None))
        self.label_7.setText(QCoreApplication.translate("MainWindow", u"\u8bbe\u5907\u7aef\u53e3", None))
        self.qLineEditRemotePort.setText(QCoreApplication.translate("MainWindow", u"12020", None))
        self.qButtonDeleteTableRow.setText(QCoreApplication.translate("MainWindow", u"\u5220\u9664\u8bb0\u5f55", None))
        self.qButtonUdpNetConn.setText(QCoreApplication.translate("MainWindow", u"\u8bbe\u5907\u8fde\u63a5", None))
        self.qButtonGetImage.setText(QCoreApplication.translate("MainWindow", u"\u83b7\u53d6\u56fe\u50cf", None))
        self.appSettingMenu.setTitle(QCoreApplication.translate("MainWindow", u"\u8bbe\u7f6e", None))
    # retranslateUi

