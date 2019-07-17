# -*- coding: utf-8 -*-

#  Copyright (C) 2019 Adrian Polyakov
#
#  This file is part of VkMusic Downloader
#
#  VkMusic Downloader is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program. If not, see http://www.gnu.org/licenses/
import codecs
import os.path
from random import choice

from PyQt5 import QtWidgets
from PyQt5 import Qt
from PyQt5.QtCore import QSizeF, QUrl, Qt, QTime, pyqtSlot, QFile
from PyQt5.QtGui import QIcon
from PyQt5.QtMultimedia import *
from PyQt5.QtMultimediaWidgets import QGraphicsVideoItem

from gui import audio_gui, audio_res_rc
from audio_threads import DownloadAudio, GetAudioListThread


# noinspection PyCallByClass,PyTypeChecker,PyArgumentList
class VkAudioApp(QtWidgets.QMainWindow, audio_gui.Ui_MainWindow):
    def __init__(self, info, config, cookie):
        super().__init__()
        self.setupUi(self)
        self.statusBar()

        self.__title__ = self.windowTitle()

        self.config = config
        self.start_dir = os.getcwd()
        self.clipboard = QtWidgets.qApp.clipboard()
        try:
            self.system_tray = Qt.QSystemTrayIcon(QIcon(':/images/logo.ico'), self)
            self.system_tray.messageClicked.connect(self._maximize_window)
            self.system_tray.activated.connect(self._maximize_window)
            self.system_tray.show()
        except AttributeError:
            self.system_tray = None

        self.btnConfirm.clicked.connect(self.get_audio_list)
        self.search.textChanged.connect(self.search_tracks)

        self.volumeSlider.sliderMoved.connect(self.change_volume)
        self.volumeSlider.valueChanged.connect(self.change_volume)

        self.play_status.sliderMoved.connect(self.change_position)

        self.pause_button.clicked.connect(self._pause)
        self.stop_button.clicked.connect(self._stop)

        self.saveAll = self._create_action(':/images/save_all.png', '&Сохранить',
                                           'Сохранить список аудиозаписей в файл со ссылками для их скачивания',
                                           'Ctrl+S', False, self.save_all)

        self.saveWithoutLinks = self._create_action(':/images/save_without_links.png', '&Сохранить без ссылок',
                                                    'Сохранить список аудиозаписей в файл без ссылок для их скачивания',
                                                    'Ctrl+Shift+S', False, self.save_without_links)

        self.download = self._create_action(':/images/download.png', '&Скачать',
                                            'Скачать выбранные ауиозаписи или всё, если ничего не выбрано', False,
                                            callback=self.download_audio_dialog)

        self.luckyMe = self._create_action(':/images/lucky_me.png', '&Мне повёзет',
                                           'Воспроизвести случайную аудиозапись из списка', 'Ctrl+L', False,
                                           self.play_track)

        self.helpDialog = self._create_action(':/images/help.png', '&Помощь', 'Помощь по программе', 'Ctrl+H',
                                              callback=self._help)

        self.aboutDialog = self._create_action(':/images/about.png', '&О программе',
                                               'Показать информацию о VkMusic Downloader', callback=self._about)

        self.copyTrackLink = self._create_action(':/images/copy.png', '&Копировать ссылку для скачивания',
                                                 'Копировать прямую ссылку на файл аудиозаписи',
                                                 callback=self.copy_track_link)

        self.playTrack = self._create_action(':/images/play.png', '&Воспроизвести', 'Воспроизвести вудиозапись',
                                             callback=self.play_track)

        self.downloadAllTracks = self._create_action(':/images/download_all.png', '&Скачать всё',
                                                     'Скачать все аудиозаписи пользователя', 'Ctrl+D', False,
                                                     self.download_all_tracks)

        self.exit = self._create_action(':/images/exit.png', '&Выход', 'Выйти из VkMusic Downloader', 'Ctrl+Q',
                                        callback=QtWidgets.qApp.exit)
        # Generating Menu Bar
        menu_bar = self.menuBar()
        music_menu = menu_bar.addMenu('&Музыка')
        music_menu.addAction(self.saveAll)
        music_menu.addAction(self.saveWithoutLinks)
        music_menu.addSeparator()
        music_menu.addAction(self.downloadAllTracks)
        music_menu.addSeparator()
        music_menu.addAction(self.luckyMe)
        music_menu.addSeparator()
        music_menu.addAction(self.exit)

        help_menu = menu_bar.addMenu('&Помощь')
        help_menu.addAction(self.helpDialog)
        help_menu.addSeparator()
        help_menu.addAction(self.aboutDialog)

        self.context_menu = QtWidgets.QMenu(self)
        self.context_menu.addAction(self.playTrack)
        self.context_menu.addAction(self.download)
        self.context_menu.addSeparator()
        self.context_menu.addAction(self.copyTrackLink)

        self.trackList.itemDoubleClicked.connect(self.play_track)
        self.trackList.itemExpanded.connect(self.on_item_expanded)
        self.trackList.customContextMenuRequested.connect(self._show_context_menu)

        self.get_audio_thread = GetAudioListThread(cookie, self)
        self.get_audio_thread.signal.connect(self.audio_list_received)
        self.get_audio_thread.str_signal.connect(self.auth_handler)

        self.download_audio_thread = DownloadAudio()
        self.download_audio_thread.signal.connect(self.download_finished)
        self.download_audio_thread.int_signal.connect(lambda x: self.progressBar.setValue(x))

        video_item = QGraphicsVideoItem()
        self.current_volume = 100
        self.time = QTime(0, 0, 0, 0)
        video_item.setSize(QSizeF(1, 1))
        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.mediaPlayer.setVideoOutput(video_item)
        self.mediaPlayer.stateChanged.connect(lambda x: [self.toggle_buttons(True), self.toggle_fields(True)])
        self.mediaPlayer.positionChanged.connect(self._position_changed)

        self.pause_button.setStyleSheet("border-radius:15px;image:url(:/images/pause_button.png);")
        self.stop_button.setStyleSheet("border-radius:15px;image:url(:/images/stop_button.png);")

        if info:
            self.login.setText(info[0])
            self.password.setText(info[1])
            self.user_link.setText(info[2])

        if ('\\Temp\\' or '/tmp/') in (cookie or config):
            message = 'Не удалось создать папку для хранения настроек приложения по пути\n{}\n\n' \
                      'Была создана временная папка. После закрытия приложения она будет удалена. ' \
                      'В следствии этого, сохранение введенных данных работать не будет'.format(os.path.dirname(cookie))
            QtWidgets.QMessageBox.warning(self, 'Предупреждение', message)

        help_file = QFile(":/html/help.html")
        help_file.open(QFile.ReadOnly)
        self.help_message = help_file.readAll().data().decode()
        help_file.close()
        del help_file

        about_file = QFile(":/html/about.html")
        about_file.open(QFile.ReadOnly)
        self.about_message = about_file.readAll().data().decode()
        about_file.close()
        del about_file

        self.hidden_tracks = []
        self.selected = None
        self.tracks = None
        self.string = None
        self.albums = None
        self.key = None

    @pyqtSlot()
    def get_audio_list(self):
        self.hidden_tracks.clear()
        if self.saveData.isChecked():
            with open(self.config, 'wb') as d:
                data = self.login.text() + '|' + self.password.text() + '|' + self.user_link.text()
                data_encrypted = codecs.encode(bytes(data, 'utf-8'), 'hex')
                d.write(data_encrypted)
        self.get_audio_thread.login = self.login.text()
        self.get_audio_thread.password = self.password.text()
        self.get_audio_thread.user_link = self.user_link.text()
        self.get_audio_thread.statusInfo = self.statusInfo
        self.toggle_buttons(False)
        self.btnConfirm.setEnabled(False)
        self.trackList.clear()
        self.statusInfo.setText('Процесс получение аудиозаписей начался.\n')
        self.get_audio_thread.start()

    @pyqtSlot('PyQt_PyObject')
    def audio_list_received(self, result):
        if result and isinstance(result, tuple):
            self.tracks, self.string, self.albums = result
            self.statusInfo.setText('Список аудиозаписей получен.'
                                    ' Зажмите Ctrl для множественного выбора'
                                    '\n{}, {} шт.'.format(self.string, len(self.tracks)))
            if self.system_tray:
                self.system_tray.showMessage(self.__title__, 'Список аудиозаписей получен')
            self.trackList.setEnabled(True)
            self.toggle_buttons(True)
            self.btnConfirm.setEnabled(True)
            for track in self.tracks:
                self.trackList.addTopLevelItem(
                    QtWidgets.QTreeWidgetItem(self.trackList, ['%(artist)s — %(title)s' % track, '%(link)s' % track])
                )
            for album in self.albums:
                root = QtWidgets.QTreeWidgetItem(self.trackList, [album['title']])
                root.setChildIndicatorPolicy(QtWidgets.QTreeWidgetItem.ShowIndicator)
                root.setFlags(Qt.ItemIsEnabled)
                self.trackList.addTopLevelItem(root)

        elif isinstance(result, str):
            if self.system_tray:
                self.system_tray.showMessage(self.__title__, 'Во время получения аудиозаписей произошла ошибка',
                                             Qt.QSystemTrayIcon.Critical)
            self.btnConfirm.setEnabled(True)
            self.statusInfo.setText('<html><head/><body><p><span style=" color:#ff0000;">Ошибка: {}'
                                    '</span></p></body></html>'.format(result))

    @pyqtSlot()
    def save_all(self):
        os.chdir(self.start_dir)
        directory = QtWidgets.QFileDialog.getSaveFileName(self, 'Сохранить всё', self.string, 'Text files (*.txt)')[0]
        if directory and self.tracks and self.string:
            if not directory.endswith('.txt'):
                directory += '.txt'
            with open(directory, 'w', encoding='utf-8') as d:
                print('{}, {} шт.\n'.format(self.string, len(self.tracks)), file=d)
                for track in self.tracks:
                    print('%(artist)s - %(title)s: %(link)s\n' % track, file=d)
            self.statusInfo.setText('Список аудиозаписей сохранен в файл {}'.format(directory))

    @pyqtSlot()
    def save_without_links(self):
        os.chdir(self.start_dir)
        directory = QtWidgets.QFileDialog.getSaveFileName(self, 'Сохранить без ссылок', self.string,
                                                          'Text files (*.txt)')[0]
        if directory and self.tracks and self.string:
            if not directory.endswith('.txt'):
                directory += '.txt'
            with open(directory, 'w', encoding='utf-8') as d:
                print('{}, {} шт.\n'.format(self.string, len(self.tracks)), file=d)
                for track in self.tracks:
                    print('%(artist)s - %(title)s' % track, file=d)
            self.statusInfo.setText(
                'Список аудиозаписей (без ссылок на скачивание) сохранен в файл {}'.format(directory))

    @pyqtSlot()
    def download_audio_dialog(self):
        os.chdir(self.start_dir)
        selected = self.trackList.selectedItems()
        selected_tracks = self._get_selected_tracks(selected)
        directory = QtWidgets.QFileDialog.getExistingDirectory(self, "Выберите папку")
        if directory:
            self.download_audio_thread.statusInfo = self.statusInfo
            if selected_tracks:
                self.download_audio_thread.tracks = selected_tracks
                length = len(selected_tracks)
            else:
                self.download_audio_thread.tracks = self.tracks
                self.download_audio_thread.albums = self.albums
                length = self._get_tracks_count()
            self.download_audio_thread.directory = directory
            self.statusInfo.setText('Процесс скачивания аудиозаписей начался.')
            self.progress_label.setEnabled(True)
            self.progressBar.setEnabled(True)
            self.progressBar.setMaximum(length)
            self.downloadAllTracks.setEnabled(False)
            self.download_audio_thread.start()

    @pyqtSlot()
    def download_all_tracks(self):
        self.trackList.clearSelection()
        self.download_audio_dialog()

    @pyqtSlot('PyQt_PyObject')
    def download_finished(self, result):
        self.toggle_buttons(True)
        if isinstance(result, str):
            self.statusInfo.setText(result)
            if self.system_tray:
                self.system_tray.showMessage(self.__title__, 'Скачивание аудиозаписей завершено')
        else:
            if self.system_tray:
                self.system_tray.showMessage(self.__title__, 'Во время скачивания аудиозаписей произошла ошибка',
                                             Qt.QSystemTrayIcon.Critical)
            self.statusInfo.setText('<html><body><p><span style=" color:#ff0000;">При скачивании'
                                    ' произошла ошибка: {}'
                                    '</span></p></body></html>'.format(result))
        self.download_audio_thread.albums = []
        self.download_audio_thread.tracks = None

    @pyqtSlot()
    def play_track(self):
        self.selected = self.trackList.selectedItems()
        selected_tracks = self._get_selected_tracks(self.selected)
        if selected_tracks:
            pass
        else:
            # Play random track :)
            track = choice(self.tracks)
            selected_tracks.append(track)
            self.selected.append(self.trackList.findItems('%(artist)s — %(title)s' % track, Qt.MatchContains)[0])
        local = QUrl(selected_tracks[0]['link'])
        media = QMediaContent(local)
        self.mediaPlayer.setMedia(media)
        self.mediaPlayer.play()
        self.toggle_fields(False)
        self.trackList.clearSelection()

    @pyqtSlot(str)
    def search_tracks(self, query=None):
        for i in self.hidden_tracks:
            i.setHidden(False)
        self.hidden_tracks.clear()
        result = [i.text(0) for i in self.trackList.findItems(query, Qt.MatchContains)]
        for i in range(self.trackList.topLevelItemCount()):
            if self.trackList.topLevelItem(i).text(0) in result:
                pass
            else:
                self.hidden_tracks.append(self.trackList.topLevelItem(i))
                self.trackList.topLevelItem(i).setHidden(True)

    @pyqtSlot()
    def copy_track_link(self):
        selected = self.trackList.selectedItems()
        selected_tracks = self._get_selected_tracks(selected)
        if selected_tracks:
            self.clipboard.setText(selected_tracks[0]['link'])

    @pyqtSlot(int)
    def change_volume(self, level):
        self.current_volume = level
        self.mediaPlayer.setVolume(self.current_volume)
        self.statusBar().showMessage('Текущая громкость: {}'.format(self.current_volume))

    @pyqtSlot(int)
    def change_position(self, pos):
        self.mediaPlayer.setPosition(pos)

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Delete:
            self.trackList.clearSelection()
        if e.key() == Qt.Key_Space:
            self._pause()

    @pyqtSlot('QTreeWidgetItem*')
    def on_item_expanded(self, item):
        if item.childCount():
            return
        for album in self.albums:
            if album['title'] == item.text(0):
                for track in album['tracks']:
                    QtWidgets.QTreeWidgetItem(item, ['%(artist)s — %(title)s' % track])

    def toggle_buttons(self, state: bool):
        self.saveAll.setEnabled(state)
        self.saveWithoutLinks.setEnabled(state)
        if not self.download_audio_thread.isRunning():
            self.downloadAllTracks.setEnabled(state)
        self.luckyMe.setEnabled(state)

    def toggle_fields(self, state: bool):
        self.login.setEnabled(state)
        self.password.setEnabled(state)
        self.user_link.setEnabled(state)
        self.trackList.setEnabled(state)
        self.saveData.setEnabled(state)
        self.search.setEnabled(state)
        self.btnConfirm.setEnabled(state)

    @pyqtSlot(str)
    def auth_handler(self, result):
        self.key = None
        num, ok = QtWidgets.QInputDialog.getText(self, 'Двухфакторная аутентификация', result)
        if ok:
            self.key = num

    @pyqtSlot()
    def _help(self):
        QtWidgets.QMessageBox.information(self, 'Помощь', self.help_message)

    @pyqtSlot()
    def _about(self):
        QtWidgets.QMessageBox.information(self, 'О программе', self.about_message)

    def _create_action(self, icon_path, text, status_tip=None, shortcut=None, set_enabled=True, callback=None):
        action = QtWidgets.QAction(QIcon(icon_path), text, self)
        if status_tip:
            action.setStatusTip(status_tip)
        if shortcut:
            action.setShortcut(shortcut)
        action.setEnabled(set_enabled)
        action.triggered.connect(callback)
        return action

    def _get_tracks_count(self):
        length = len(self.tracks)
        for album in self.albums:
            length += len(album['tracks'])
        return length

    def _get_selected_tracks(self, selected):
        selected_tracks = []
        for element in selected:
            for track in self.tracks:
                if element.text(0) in '%(artist)s — %(title)s' % track:
                    selected_tracks.append(track)
                    break
        for element in selected:
            for album in self.albums:
                for track in album['tracks']:
                    if element.text(0) in '%(artist)s — %(title)s' % track:
                        selected_tracks.append(track)
                        break
        return selected_tracks

    @pyqtSlot()
    def _pause(self):
        if self.mediaPlayer.state() == 1:
            self.mediaPlayer.pause()
            self.toggle_fields(False)
            if not self.download_audio_thread.isRunning():
                self.downloadAllTracks.setEnabled(True)
            self.pause_button.setStyleSheet("border-radius:15px;image:url(:/images/play_button.png);")
        elif self.mediaPlayer.state() == 2:
            self.mediaPlayer.play()
            self.toggle_fields(False)
            if not self.download_audio_thread.isRunning():
                self.downloadAllTracks.setEnabled(True)
            self.pause_button.setStyleSheet("border-radius:15px;image:url(:/images/pause_button.png);")

    @pyqtSlot()
    def _stop(self):
        if self.mediaPlayer.state():
            self.toggle_fields(True)
            self.toggle_buttons(True)
        self.mediaPlayer.stop()

    @pyqtSlot('qint64')
    def _position_changed(self, x):
        if self.selected:
            self.statusBar().showMessage('Воспроизводится {}: {} / {} Громкость: {}'.format(
                self.selected[0].text(0),
                self.time.addMSecs(x).toString(Qt.DefaultLocaleLongDate),
                self.time.addMSecs(self.mediaPlayer.duration()).toString(Qt.DefaultLocaleLongDate),
                self.current_volume))
            self.play_status.setValue(x)
            self.play_status.setMaximum(self.mediaPlayer.duration())
        else:
            pass

    @pyqtSlot('QPoint')
    def _show_context_menu(self, point):
        if self.download_audio_thread.isRunning():
            self.download.setEnabled(False)
        self.context_menu.exec(self.trackList.mapToGlobal(point))

    @pyqtSlot()
    def _maximize_window(self):
        self.raise_()
        self.activateWindow()
        self.showMaximized()
        self.showNormal()
