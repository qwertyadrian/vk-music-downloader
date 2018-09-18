# -*- coding: utf-8 -*-
"""  
  Copyright (C) 2018 Adrian Polyakov
  
  This file is part of VkMusic Downloader

  VkMusic Downloader is free software: you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.
  
  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.
  
  You should have received a copy of the GNU General Public License
  along with this program. If not, see http://www.gnu.org/licenses/
"""
# Form implementation generated from reading ui file 'audio.ui'
#
# Created by: PyQt5 UI code generator 5.7
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets
import os.path
import sys

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.setEnabled(True)
        MainWindow.resize(780, 480)
        MainWindow.setMinimumSize(QtCore.QSize(780, 480))
        MainWindow.setMaximumSize(QtCore.QSize(780, 480))
        icon = QtGui.QIcon()
        logo = resource_path("logo.png")
        icon.addPixmap(QtGui.QPixmap(logo), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.login = QtWidgets.QLineEdit(self.centralwidget)
        self.login.setGeometry(QtCore.QRect(340, 10, 181, 31))
        self.login.setObjectName("login")
        self.login_text = QtWidgets.QLabel(self.centralwidget)
        self.login_text.setGeometry(QtCore.QRect(10, 10, 331, 31))
        font = QtGui.QFont()
        font.setPointSize(13)
        self.login_text.setFont(font)
        self.login_text.setObjectName("login_text")
        self.password_text = QtWidgets.QLabel(self.centralwidget)
        self.password_text.setGeometry(QtCore.QRect(270, 50, 61, 31))
        font = QtGui.QFont()
        font.setPointSize(13)
        self.password_text.setFont(font)
        self.password_text.setObjectName("password_text")
        self.password = QtWidgets.QLineEdit(self.centralwidget)
        self.password.setGeometry(QtCore.QRect(340, 50, 181, 31))
        self.password.setInputMethodHints(QtCore.Qt.ImhHiddenText|QtCore.Qt.ImhNoAutoUppercase|QtCore.Qt.ImhNoPredictiveText|QtCore.Qt.ImhSensitiveData)
        self.password.setInputMask("")
        self.password.setText("")
        self.password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.password.setDragEnabled(False)
        self.password.setObjectName("password")
        self.link_text = QtWidgets.QLabel(self.centralwidget)
        self.link_text.setGeometry(QtCore.QRect(60, 90, 281, 31))
        font = QtGui.QFont()
        font.setPointSize(13)
        self.link_text.setFont(font)
        self.link_text.setObjectName("link_text")
        self.user_link = QtWidgets.QLineEdit(self.centralwidget)
        self.user_link.setGeometry(QtCore.QRect(340, 90, 181, 31))
        self.user_link.setObjectName("user_link")
        self.btnConfirm = QtWidgets.QPushButton(self.centralwidget)
        self.btnConfirm.setGeometry(QtCore.QRect(590, 440, 181, 29))
        self.btnConfirm.setAutoDefault(False)
        self.btnConfirm.setDefault(False)
        self.btnConfirm.setObjectName("btnConfirm")
        self.status_label = QtWidgets.QLabel(self.centralwidget)
        self.status_label.setGeometry(QtCore.QRect(10, 120, 68, 61))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.status_label.setFont(font)
        self.status_label.setObjectName("status_label")
        self.saveData = QtWidgets.QCheckBox(self.centralwidget)
        self.saveData.setEnabled(True)
        self.saveData.setGeometry(QtCore.QRect(530, 90, 251, 27))
        self.saveData.setObjectName("saveData")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(10, 410, 331, 21))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.saveAll = QtWidgets.QPushButton(self.centralwidget)
        self.saveAll.setEnabled(False)
        self.saveAll.setGeometry(QtCore.QRect(10, 440, 91, 29))
        self.saveAll.setObjectName("saveAll")
        self.saveWithoutLinks = QtWidgets.QPushButton(self.centralwidget)
        self.saveWithoutLinks.setEnabled(False)
        self.saveWithoutLinks.setGeometry(QtCore.QRect(110, 440, 171, 29))
        self.saveWithoutLinks.setObjectName("saveWithoutLinks")
        self.downloadAll = QtWidgets.QPushButton(self.centralwidget)
        self.downloadAll.setEnabled(False)
        self.downloadAll.setGeometry(QtCore.QRect(450, 440, 91, 29))
        self.downloadAll.setObjectName("downloadAll")
        self.statusInfo = QtWidgets.QLabel(self.centralwidget)
        self.statusInfo.setGeometry(QtCore.QRect(70, 130, 701, 41))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.statusInfo.setFont(font)
        self.statusInfo.setWordWrap(True)
        self.statusInfo.setObjectName("statusInfo")
        self.label_4 = QtWidgets.QLabel(self.centralwidget)
        self.label_4.setEnabled(True)
        self.label_4.setGeometry(QtCore.QRect(10, 180, 161, 16))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.label_4.setFont(font)
        self.label_4.setObjectName("label_4")
        self.downloadSelected = QtWidgets.QPushButton(self.centralwidget)
        self.downloadSelected.setEnabled(False)
        self.downloadSelected.setGeometry(QtCore.QRect(290, 440, 151, 29))
        self.downloadSelected.setObjectName("downloadSelected")
        self.progressBar = QtWidgets.QProgressBar(self.centralwidget)
        self.progressBar.setEnabled(False)
        self.progressBar.setGeometry(QtCore.QRect(610, 172, 161, 21))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.progressBar.setFont(font)
        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(1)
        self.progressBar.setProperty("value", 0)
        self.progressBar.setAlignment(QtCore.Qt.AlignCenter)
        self.progressBar.setTextVisible(True)
        self.progressBar.setInvertedAppearance(False)
        self.progressBar.setObjectName("progressBar")
        self.progress_label = QtWidgets.QLabel(self.centralwidget)
        self.progress_label.setEnabled(False)
        self.progress_label.setGeometry(QtCore.QRect(470, 170, 141, 20))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.progress_label.setFont(font)
        self.progress_label.setObjectName("progress_label")
        self.trackList = QtWidgets.QListWidget(self.centralwidget)
        self.trackList.setEnabled(False)
        self.trackList.setGeometry(QtCore.QRect(10, 200, 761, 211))
        self.trackList.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.trackList.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        self.trackList.setObjectName("trackList")
        self.enableSorting = QtWidgets.QCheckBox(self.centralwidget)
        self.enableSorting.setGeometry(QtCore.QRect(530, 46, 171, 41))
        self.enableSorting.setStatusTip("")
        self.enableSorting.setTristate(False)
        self.enableSorting.setObjectName("enableSorting")
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "VKMusic Downloader"))
        self.login_text.setText(_translate("MainWindow", "Номер телефона или электронная почта:"))
        self.password_text.setText(_translate("MainWindow", "Пароль:"))
        self.link_text.setText(_translate("MainWindow", "Ссылка на профиль пользователя:"))
        self.btnConfirm.setToolTip(_translate("MainWindow", "Получить список аудиозаписей пользователя"))
        self.btnConfirm.setText(_translate("MainWindow", "Получить аудиозаписи"))
        self.status_label.setText(_translate("MainWindow", "Статус:"))
        self.saveData.setToolTip(_translate("MainWindow", "Сохранить введенные данные?"))
        self.saveData.setText(_translate("MainWindow", "Запомнить"))
        self.label_2.setText(_translate("MainWindow", "Что сделать с полученным списком аудиозаписей:"))
        self.saveAll.setToolTip(_translate("MainWindow", "Сохранить список аудиозаписей в файл со ссылками для их скачивания"))
        self.saveAll.setText(_translate("MainWindow", "Сохранить"))
        self.saveWithoutLinks.setToolTip(_translate("MainWindow", "Сохранить список аудиозаписей в файл без ссылок для их скачивания"))
        self.saveWithoutLinks.setText(_translate("MainWindow", "Сохранить без ссылок"))
        self.downloadAll.setToolTip(_translate("MainWindow", "Скачать все аудиозаписи из списка выше"))
        self.downloadAll.setText(_translate("MainWindow", "Скачать всё"))
        self.statusInfo.setText(_translate("MainWindow", "Готов к работе."))
        self.label_4.setText(_translate("MainWindow", "Список аудиозаписей:"))
        self.downloadSelected.setToolTip(_translate("MainWindow", "Скачать выбранные ауиозаписи из списка выше"))
        self.downloadSelected.setText(_translate("MainWindow", "Скачать выбранные"))
        self.progressBar.setFormat(_translate("MainWindow", "Скачано %v из %m"))
        self.progress_label.setText(_translate("MainWindow", "Прогресс скачивания:"))
        self.enableSorting.setToolTip(_translate("MainWindow", "Сортировать спсиок в алфавитном порядке?"))
        self.enableSorting.setText(_translate("MainWindow", "Сортировать список"))

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath('.')
    return os.path.join(base_path, relative_path)
    