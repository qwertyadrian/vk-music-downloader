# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'gui/help_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.12.1
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
        self.textBrowser.setHtml(_translate("helpDialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Noto Sans\'; font-size:10pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Управление воспроизведением: </p>\n"
"<ul style=\"margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; -qt-list-indent: 1;\"><li style=\" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Стрелка вверх/вниз - громкость </li>\n"
"<li style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Стрелка влево/вправо - перемотка </li>\n"
"<li style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Пробел - пауза/возобновление </li>\n"
"<li style=\" margin-top:0px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Alt - стоп </li></ul>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Все доступные сочетания клавиш указаны в меню «Музыка»<br /><span style=\" font-weight:600; color:#ff0000;\">Внимание!</span> Во время воспроизведения блокируется интерфейс программы, за исключением меню в левом верхнем углу.<br /><br />Все файлы программы хранятся в папке .vk_downloader, которая находится в папке пользователя, от имени которого запущена программа.<br /><br />Для множественного выделения аудиозаписей зажмите левую кнопку мыши и тащите её вниз (вверх). Для «точечного» выделения нажимайте левую кнопку мыши с зажатой клавишей Ctrl. Для сброса выделения нажмите Delete</p></body></html>"))


from gui import audio_res
