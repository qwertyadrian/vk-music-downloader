# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'gui/help_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.14.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_helpDialog(object):
    def setupUi(self, helpDialog):
        helpDialog.setObjectName("helpDialog")
        helpDialog.resize(611, 341)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(helpDialog.sizePolicy().hasHeightForWidth())
        helpDialog.setSizePolicy(sizePolicy)
        helpDialog.setMinimumSize(QtCore.QSize(611, 341))
        helpDialog.setMaximumSize(QtCore.QSize(611, 341))
        helpDialog.setModal(True)
        self.layoutWidget = QtWidgets.QWidget(helpDialog)
        self.layoutWidget.setGeometry(QtCore.QRect(10, 10, 591, 321))
        self.layoutWidget.setObjectName("layoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.layoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.textBrowser = QtWidgets.QTextBrowser(self.layoutWidget)
        self.textBrowser.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.textBrowser.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.textBrowser.setSource(QtCore.QUrl("qrc:/html/help.html"))
        self.textBrowser.setObjectName("textBrowser")
        self.verticalLayout.addWidget(self.textBrowser)
        self.buttonBox = QtWidgets.QDialogButtonBox(self.layoutWidget)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(helpDialog)
        self.buttonBox.accepted.connect(helpDialog.accept)
        QtCore.QMetaObject.connectSlotsByName(helpDialog)

    def retranslateUi(self, helpDialog):
        _translate = QtCore.QCoreApplication.translate
        helpDialog.setWindowTitle(_translate("helpDialog", "Помощь"))
from gui import audio_res
