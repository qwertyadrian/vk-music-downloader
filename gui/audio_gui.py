# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'gui/audio.ui'
#
# Created by: PyQt5 UI code generator 5.15.6
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.setEnabled(True)
        MainWindow.resize(877, 581)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/images/logo.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.pause_button = QtWidgets.QPushButton(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pause_button.sizePolicy().hasHeightForWidth())
        self.pause_button.setSizePolicy(sizePolicy)
        self.pause_button.setStyleSheet("border-radius:15px;image:url(:/images/pause_button.png);")
        self.pause_button.setText("")
        self.pause_button.setObjectName("pause_button")
        self.gridLayout.addWidget(self.pause_button, 5, 2, 1, 1)
        self.volumeSlider = QtWidgets.QSlider(self.centralwidget)
        self.volumeSlider.setMaximum(100)
        self.volumeSlider.setSliderPosition(100)
        self.volumeSlider.setOrientation(QtCore.Qt.Horizontal)
        self.volumeSlider.setTickPosition(QtWidgets.QSlider.TicksBothSides)
        self.volumeSlider.setTickInterval(10)
        self.volumeSlider.setObjectName("volumeSlider")
        self.gridLayout.addWidget(self.volumeSlider, 5, 1, 1, 1)
        self.login_text = QtWidgets.QLabel(self.centralwidget)
        self.login_text.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.login_text.setObjectName("login_text")
        self.gridLayout.addWidget(self.login_text, 0, 0, 1, 4)
        self.play_status = QtWidgets.QSlider(self.centralwidget)
        self.play_status.setMaximum(100)
        self.play_status.setOrientation(QtCore.Qt.Horizontal)
        self.play_status.setObjectName("play_status")
        self.gridLayout.addWidget(self.play_status, 6, 0, 1, 7)
        self.saveData = QtWidgets.QCheckBox(self.centralwidget)
        self.saveData.setEnabled(True)
        self.saveData.setObjectName("saveData")
        self.gridLayout.addWidget(self.saveData, 1, 6, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 5, 4, 1, 1)
        self.progress_label = QtWidgets.QLabel(self.centralwidget)
        self.progress_label.setEnabled(False)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.progress_label.sizePolicy().hasHeightForWidth())
        self.progress_label.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.progress_label.setFont(font)
        self.progress_label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.progress_label.setObjectName("progress_label")
        self.gridLayout.addWidget(self.progress_label, 3, 4, 1, 1)
        self.password_text = QtWidgets.QLabel(self.centralwidget)
        self.password_text.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.password_text.setObjectName("password_text")
        self.gridLayout.addWidget(self.password_text, 1, 2, 1, 2)
        self.stop_button = QtWidgets.QPushButton(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.stop_button.sizePolicy().hasHeightForWidth())
        self.stop_button.setSizePolicy(sizePolicy)
        self.stop_button.setStyleSheet("border-radius:15px;image:url(:/images/stop_button.png);")
        self.stop_button.setText("")
        self.stop_button.setObjectName("stop_button")
        self.gridLayout.addWidget(self.stop_button, 5, 3, 1, 1)
        self.user_link = QtWidgets.QLineEdit(self.centralwidget)
        self.user_link.setObjectName("user_link")
        self.gridLayout.addWidget(self.user_link, 2, 4, 1, 2)
        self.sort_tracks = QtWidgets.QToolButton(self.centralwidget)
        self.sort_tracks.setPopupMode(QtWidgets.QToolButton.InstantPopup)
        self.sort_tracks.setToolButtonStyle(QtCore.Qt.ToolButtonTextOnly)
        self.sort_tracks.setObjectName("sort_tracks")
        self.gridLayout.addWidget(self.sort_tracks, 2, 6, 1, 1)
        self.link_text = QtWidgets.QLabel(self.centralwidget)
        self.link_text.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.link_text.setObjectName("link_text")
        self.gridLayout.addWidget(self.link_text, 2, 0, 1, 4)
        self.login = QtWidgets.QLineEdit(self.centralwidget)
        self.login.setObjectName("login")
        self.gridLayout.addWidget(self.login, 0, 4, 1, 2)
        self.btnConfirm = QtWidgets.QPushButton(self.centralwidget)
        self.btnConfirm.setAutoDefault(False)
        self.btnConfirm.setDefault(False)
        self.btnConfirm.setObjectName("btnConfirm")
        self.gridLayout.addWidget(self.btnConfirm, 5, 5, 1, 2)
        self.search = QtWidgets.QLineEdit(self.centralwidget)
        self.search.setObjectName("search")
        self.gridLayout.addWidget(self.search, 5, 0, 1, 1)
        self.password = QtWidgets.QLineEdit(self.centralwidget)
        self.password.setInputMethodHints(QtCore.Qt.ImhHiddenText|QtCore.Qt.ImhNoAutoUppercase|QtCore.Qt.ImhNoPredictiveText|QtCore.Qt.ImhSensitiveData)
        self.password.setInputMask("")
        self.password.setText("")
        self.password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.password.setDragEnabled(False)
        self.password.setObjectName("password")
        self.gridLayout.addWidget(self.password, 1, 4, 1, 2)
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setEnabled(True)
        self.tabWidget.setObjectName("tabWidget")
        self.tracks_tab = QtWidgets.QWidget()
        self.tracks_tab.setObjectName("tracks_tab")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.tracks_tab)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.trackList = QtWidgets.QTreeWidget(self.tracks_tab)
        self.trackList.setEnabled(False)
        self.trackList.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.trackList.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.trackList.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.trackList.setHeaderHidden(True)
        self.trackList.setColumnCount(2)
        self.trackList.setObjectName("trackList")
        self.trackList.header().setVisible(False)
        self.gridLayout_2.addWidget(self.trackList, 0, 0, 1, 1)
        self.tabWidget.addTab(self.tracks_tab, "")
        self.playlists_tab = QtWidgets.QWidget()
        self.playlists_tab.setObjectName("playlists_tab")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.playlists_tab)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.albumsList = QtWidgets.QTreeWidget(self.playlists_tab)
        self.albumsList.setEnabled(False)
        self.albumsList.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.albumsList.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.albumsList.setObjectName("albumsList")
        self.albumsList.header().setVisible(False)
        self.gridLayout_3.addWidget(self.albumsList, 0, 0, 1, 1)
        self.tabWidget.addTab(self.playlists_tab, "")
        self.gridLayout.addWidget(self.tabWidget, 4, 0, 1, 7)
        self.progressBar = QtWidgets.QProgressBar(self.centralwidget)
        self.progressBar.setEnabled(False)
        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(1)
        self.progressBar.setProperty("value", 0)
        self.progressBar.setAlignment(QtCore.Qt.AlignCenter)
        self.progressBar.setTextVisible(True)
        self.progressBar.setInvertedAppearance(False)
        self.progressBar.setObjectName("progressBar")
        self.gridLayout.addWidget(self.progressBar, 3, 5, 1, 2)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menuBar = QtWidgets.QMenuBar(MainWindow)
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 877, 34))
        self.menuBar.setObjectName("menuBar")
        self.music_menu = QtWidgets.QMenu(self.menuBar)
        self.music_menu.setObjectName("music_menu")
        self.help_menu = QtWidgets.QMenu(self.menuBar)
        self.help_menu.setObjectName("help_menu")
        MainWindow.setMenuBar(self.menuBar)
        self.statusBar = QtWidgets.QStatusBar(MainWindow)
        self.statusBar.setObjectName("statusBar")
        MainWindow.setStatusBar(self.statusBar)
        self.saveAll = QtWidgets.QAction(MainWindow)
        self.saveAll.setEnabled(False)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/images/save_all.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.saveAll.setIcon(icon1)
        self.saveAll.setObjectName("saveAll")
        self.saveWithoutLinks = QtWidgets.QAction(MainWindow)
        self.saveWithoutLinks.setEnabled(False)
        self.saveWithoutLinks.setObjectName("saveWithoutLinks")
        self.downloadAllTracks = QtWidgets.QAction(MainWindow)
        self.downloadAllTracks.setEnabled(False)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/images/download_all.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.downloadAllTracks.setIcon(icon2)
        self.downloadAllTracks.setObjectName("downloadAllTracks")
        self.luckyMe = QtWidgets.QAction(MainWindow)
        self.luckyMe.setEnabled(False)
        self.luckyMe.setObjectName("luckyMe")
        self.exit = QtWidgets.QAction(MainWindow)
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(":/images/exit.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.exit.setIcon(icon3)
        self.exit.setObjectName("exit")
        self.helpDialog = QtWidgets.QAction(MainWindow)
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(":/images/help.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.helpDialog.setIcon(icon4)
        self.helpDialog.setObjectName("helpDialog")
        self.aboutDialog = QtWidgets.QAction(MainWindow)
        self.aboutDialog.setObjectName("aboutDialog")
        self.music_menu.addAction(self.saveAll)
        self.music_menu.addAction(self.saveWithoutLinks)
        self.music_menu.addSeparator()
        self.music_menu.addAction(self.downloadAllTracks)
        self.music_menu.addSeparator()
        self.music_menu.addAction(self.luckyMe)
        self.music_menu.addSeparator()
        self.music_menu.addAction(self.exit)
        self.help_menu.addAction(self.helpDialog)
        self.help_menu.addSeparator()
        self.help_menu.addAction(self.aboutDialog)
        self.menuBar.addAction(self.music_menu.menuAction())
        self.menuBar.addAction(self.help_menu.menuAction())
        self.login_text.setBuddy(self.login)
        self.password_text.setBuddy(self.password)
        self.link_text.setBuddy(self.user_link)

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        MainWindow.setTabOrder(self.login, self.password)
        MainWindow.setTabOrder(self.password, self.user_link)
        MainWindow.setTabOrder(self.user_link, self.saveData)
        MainWindow.setTabOrder(self.saveData, self.sort_tracks)
        MainWindow.setTabOrder(self.sort_tracks, self.btnConfirm)
        MainWindow.setTabOrder(self.btnConfirm, self.search)
        MainWindow.setTabOrder(self.search, self.volumeSlider)
        MainWindow.setTabOrder(self.volumeSlider, self.pause_button)
        MainWindow.setTabOrder(self.pause_button, self.stop_button)
        MainWindow.setTabOrder(self.stop_button, self.play_status)
        MainWindow.setTabOrder(self.play_status, self.tabWidget)
        MainWindow.setTabOrder(self.tabWidget, self.trackList)
        MainWindow.setTabOrder(self.trackList, self.albumsList)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "VKMusic Downloader"))
        self.login_text.setText(_translate("MainWindow", "Номер телефона или электронная почта:"))
        self.saveData.setToolTip(_translate("MainWindow", "Сохранить введенные данные?"))
        self.saveData.setText(_translate("MainWindow", "Запомнить"))
        self.progress_label.setText(_translate("MainWindow", "Прогресс скачивания:"))
        self.password_text.setText(_translate("MainWindow", "Пароль:"))
        self.sort_tracks.setText(_translate("MainWindow", "Сортировка"))
        self.link_text.setText(_translate("MainWindow", "Ссылка на профиль (пост, альбом) пользователя (сообщества):"))
        self.btnConfirm.setToolTip(_translate("MainWindow", "Получить список аудиозаписей пользователя"))
        self.btnConfirm.setText(_translate("MainWindow", "Получить аудиозаписи"))
        self.search.setPlaceholderText(_translate("MainWindow", "Поиск..."))
        self.trackList.headerItem().setText(0, _translate("MainWindow", "artist - name"))
        self.trackList.headerItem().setText(1, _translate("MainWindow", "name - artist"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tracks_tab), _translate("MainWindow", "Аудиозаписи"))
        self.albumsList.headerItem().setText(0, _translate("MainWindow", "Плейлист"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.playlists_tab), _translate("MainWindow", "Плейлисты"))
        self.progressBar.setFormat(_translate("MainWindow", "Скачано %v из %m"))
        self.music_menu.setTitle(_translate("MainWindow", "&Музыка"))
        self.help_menu.setTitle(_translate("MainWindow", "&Помощь"))
        self.saveAll.setText(_translate("MainWindow", "&Сохранить"))
        self.saveAll.setStatusTip(_translate("MainWindow", "Сохранить список аудиозаписей в файл со ссылками для их скачивания"))
        self.saveAll.setShortcut(_translate("MainWindow", "Ctrl+S"))
        self.saveWithoutLinks.setText(_translate("MainWindow", "Сохранить &без ссылок"))
        self.saveWithoutLinks.setStatusTip(_translate("MainWindow", "Сохранить список аудиозаписей в файл без ссылок для их скачивания"))
        self.saveWithoutLinks.setShortcut(_translate("MainWindow", "Ctrl+Shift+S"))
        self.downloadAllTracks.setText(_translate("MainWindow", "С&качать всё"))
        self.downloadAllTracks.setStatusTip(_translate("MainWindow", "Скачать все аудиозаписи пользователя"))
        self.downloadAllTracks.setShortcut(_translate("MainWindow", "Ctrl+D"))
        self.luckyMe.setText(_translate("MainWindow", "&Мне повезёт"))
        self.luckyMe.setStatusTip(_translate("MainWindow", "Воспроизвести случайную аудиозапись из списка"))
        self.luckyMe.setShortcut(_translate("MainWindow", "Ctrl+L"))
        self.exit.setText(_translate("MainWindow", "&Выход"))
        self.exit.setStatusTip(_translate("MainWindow", "Выход из VKMusic Downloader"))
        self.exit.setShortcut(_translate("MainWindow", "Ctrl+Q"))
        self.helpDialog.setText(_translate("MainWindow", "&Помощь"))
        self.helpDialog.setStatusTip(_translate("MainWindow", "Помощь по VkMusic Downloader"))
        self.helpDialog.setShortcut(_translate("MainWindow", "Ctrl+H"))
        self.aboutDialog.setText(_translate("MainWindow", "&О программе"))
        self.aboutDialog.setStatusTip(_translate("MainWindow", "Информация о VkMusic Downloader"))
from gui import audio_res
