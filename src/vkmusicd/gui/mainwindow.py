# -*- coding: utf-8 -*-

#  Copyright (C) 2018-2022 Adrian Polyakov
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
import json
import os
import pathlib
from random import choice

from keyring.errors import PasswordDeleteError
from PyQt5 import Qt
from PyQt5.QtCore import QReadWriteLock, Qt, QTime, QUrl, pyqtSlot
from PyQt5.QtGui import QIcon, QImage, QKeySequence, QPixmap
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtWidgets import (QAction, QDialog, QFileDialog, QInputDialog, QMainWindow, QMenu, QMessageBox, QShortcut,
                             QSystemTrayIcon, QTreeWidgetItem, qApp)

from vkmusicd.utilites.audio_threads import DownloadAudio, GetAudioListThread

from .about import Ui_aboutDialog
from .captcha import Ui_CaptchaRequest
from .help import Ui_helpDialog
from .mainwindow_ui import Ui_MainWindow


# noinspection PyCallByClass,PyTypeChecker,PyArgumentList
class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, info, cookie, keyring):
        super().__init__()
        self.setupUi(self)

        self.lock = QReadWriteLock()

        self.help = HelpDialog(self)
        self.about = AboutDialog(self)
        self.captchaDialog = CaptchaDialog(self)

        self.__title__ = self.windowTitle()

        self.keyring = keyring

        self.clipboard = qApp.clipboard()
        try:
            self.system_tray = QSystemTrayIcon(QIcon(":/images/logo.ico"), self)
            self.system_tray.messageClicked.connect(self.show)
            self.system_tray.activated.connect(self.show)
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

        self.saveAll.triggered.connect(self.save_all)
        self.saveWithoutLinks.triggered.connect(self.save_without_links)
        self.downloadAllTracks.triggered.connect(self.download_all_tracks)
        self.luckyMe.triggered.connect(self.play_track)
        self.helpDialog.triggered.connect(self.help.show)
        self.aboutDialog.triggered.connect(self.about.show)
        self.captchaDialog.accepted.connect(self.captchaDialog.close)
        self.exit.triggered.connect(qApp.exit)

        self.copyTrackLink = self._create_action(
            "&Копировать ссылку для скачивания",
            ":/images/copy.png",
            "Копировать прямую ссылку на файл аудиозаписи",
            callback=self.copy_track_link,
        )

        self.playTrack = self._create_action(
            "&Воспроизвести",
            ":/images/play.png",
            "Воспроизвести вудиозапись",
            callback=self.play_track,
        )

        self.download = self._create_action(
            "&Скачать",
            ":/images/download.png",
            "Скачать выбранные ауиозаписи или всё, если ничего не выбрано",
            False,
            callback=self.download_audio_dialog,
        )

        self.sort_by_name = self._create_action("По названию", callback=self._sort_by_name)
        self.sort_by_artist = self._create_action("По имени исполнителя", callback=self._sort_by_artist)
        self.sort_tracks.addActions([self.sort_by_name, self.sort_by_artist])
        # Инициализация контекстного меню
        self.context_menu = QMenu(self)
        self.context_menu.addActions([self.playTrack, self.download])
        self.context_menu.addSeparator()
        self.context_menu.addAction(self.copyTrackLink)
        # Инициализация контекстного меню для системного трея
        self.system_tray_menu = QMenu(self)
        self.system_tray_menu.addAction(self.exit)
        self.system_tray.setContextMenu(self.system_tray_menu)
        # Конец инициализации контекстного меню

        self.trackList.itemDoubleClicked.connect(self.play_track)
        self.trackList.customContextMenuRequested.connect(self._show_context_menu)
        self.albumsList.itemExpanded.connect(self.on_item_expanded)

        self.albumsList.customContextMenuRequested.connect(self._show_context_menu)
        self.albumsList.itemDoubleClicked.connect(self.play_track)

        self.get_audio_thread = GetAudioListThread(cookie)
        self.get_audio_thread.signal.connect(self.audio_list_received)
        self.get_audio_thread.str_signal.connect(self.auth_handler)
        self.get_audio_thread.image_signal.connect(self.captcha_handler)

        self.download_audio_thread = DownloadAudio()
        self.download_audio_thread.signal.connect(self.download_finished)
        self.download_audio_thread.int_signal.connect(lambda x: self.progressBar.setValue(x))

        # Инициализация аудиоплеера
        self.current_volume = 100
        self.time = QTime(0, 0)
        self.mediaPlayer = QMediaPlayer(self)
        self.mediaPlayer.stateChanged.connect(lambda: (self.toggle_buttons(True), self.toggle_fields(True)))
        self.mediaPlayer.positionChanged.connect(self._position_changed)

        self.shortcut = QShortcut(QKeySequence("Ctrl+J"), self)
        self.shortcut.activated.connect(self._dump)
        self.shortcut = QShortcut(QKeySequence("Ctrl+K"), self)
        self.shortcut.activated.connect(self._load)

        self.statusBar.showMessage("Готов к работе")

        if info:
            self.login.setText(info[0])
            self.password.setText(info[1])
            self.user_link.setText(info[2])

        if cookie.match("*\\Temp\\*") or cookie.match("/tmp/*"):
            message = (
                "Не удалось создать папку для хранения куки приложения по пути\n{}\n\n"
                "Была создана временная папка. После закрытия приложения она будет удалена. "
                "В следствии этого, при авторизации, если включено, "
                "после перезапуска приложения будет повторно запрошен "
                "код подтверждения входа".format(cookie)
            )
            QMessageBox.warning(self, "Предупреждение", message)

        self.hidden_tracks = []
        self.selected = None
        self.tracks = None
        self.string = None
        self.albums = None

    @pyqtSlot()
    def get_audio_list(self):
        self.hidden_tracks.clear()
        if self.saveData.isChecked():
            data = self.login.text() + "|" + self.password.text() + "|" + self.user_link.text()
            self.keyring.set_password("vk_music_downloader", os.getlogin(), data)
        else:
            try:
                self.keyring.delete_password("vk_music_downloader", os.getlogin())
            except PasswordDeleteError:
                pass
        self.get_audio_thread.login = self.login.text()
        self.get_audio_thread.password = self.password.text()
        self.get_audio_thread.user_link = self.user_link.text()
        self.get_audio_thread.statusBar = self.statusBar
        self.get_audio_thread.saveData = self.saveData.isChecked()
        self.toggle_buttons(False)
        self.btnConfirm.setEnabled(False)
        self.trackList.clear()
        self.albumsList.clear()
        self.statusBar.showMessage("Процесс получение аудиозаписей начался.\n")
        self.get_audio_thread.start()

    @pyqtSlot("PyQt_PyObject")
    def audio_list_received(self, result):
        if result and isinstance(result, tuple):
            self.tracks, self.string, self.albums = result
            self.statusBar.showMessage(
                "Список аудиозаписей получен."
                " Зажмите Ctrl для множественного выбора."
                "\n{}, {} шт.".format(self.string, len(self.tracks))
            )
            if self.system_tray:
                self.system_tray.showMessage(self.__title__, "Список аудиозаписей получен")
            self.trackList.setEnabled(True)
            self.albumsList.setEnabled(True)
            self.toggle_buttons(True)
            self.btnConfirm.setEnabled(True)
            for track in self.tracks:
                self.trackList.addTopLevelItem(
                    QTreeWidgetItem(
                        self.trackList,
                        [
                            "{artist} - {title}".format(**track),
                            "{title} - {artist}".format(**track),
                        ],
                    )
                )
            for album in self.albums:
                root = QTreeWidgetItem(self.albumsList, [album["title"]])
                root.setChildIndicatorPolicy(QTreeWidgetItem.ShowIndicator)
                root.setFlags(Qt.ItemIsEnabled)
                self.albumsList.addTopLevelItem(root)
            self.trackList.hideColumn(1)

        elif isinstance(result, str):
            if self.system_tray:
                self.system_tray.showMessage(
                    self.__title__,
                    "Во время получения аудиозаписей произошла ошибка",
                    QSystemTrayIcon.Critical,
                )
            self.btnConfirm.setEnabled(True)
            self.statusBar.showMessage("Ошибка: {}".format(result))

    @pyqtSlot()
    def save_all(self):
        directory = QFileDialog.getSaveFileName(self, "Сохранить всё", self.string, "Text files (*.txt)")[0]
        if directory and self.tracks and self.string:
            if not directory.endswith(".txt"):
                directory += ".txt"
            self._save_audio_list(directory)
            self.statusBar.showMessage("Список аудиозаписей сохранен в файл {}".format(directory))

    @pyqtSlot()
    def save_without_links(self):
        directory = QFileDialog.getSaveFileName(
            self, "Сохранить без ссылок", self.string, "Text files (*.txt)"
        )[0]
        if directory and self.tracks and self.string:
            if not directory.endswith(".txt"):
                directory += ".txt"
            self._save_audio_list(directory, save_links=False)
            self.statusBar.showMessage(
                "Список аудиозаписей (без ссылок на скачивание) сохранен в файл {}".format(directory)
            )

    @pyqtSlot()
    def download_audio_dialog(self):
        selected = self.trackList.selectedItems() + self.albumsList.selectedItems()
        selected_tracks = self._get_selected_tracks(selected)
        directory = QFileDialog.getExistingDirectory(self, "Выберите папку")
        if directory:
            self.download_audio_thread.statusBar = self.statusBar
            if selected_tracks:
                self.download_audio_thread.tracks = selected_tracks
                length = len(selected_tracks)
            else:
                self.download_audio_thread.tracks = self.tracks
                self.download_audio_thread.albums = self.albums
                length = self._get_tracks_count()
            self.download_audio_thread.directory = pathlib.Path(directory)
            self.statusBar.showMessage("Процесс скачивания аудиозаписей начался.")
            self.progress_label.setEnabled(True)
            self.progressBar.setEnabled(True)
            self.progressBar.setMaximum(length)
            self.downloadAllTracks.setEnabled(False)
            self.download_audio_thread.start()

    @pyqtSlot()
    def download_all_tracks(self):
        self.trackList.clearSelection()
        self.albumsList.clearSelection()
        self.download_audio_dialog()

    @pyqtSlot("PyQt_PyObject")
    def download_finished(self, result):
        self.toggle_buttons(True)
        if isinstance(result, str):
            self.statusBar.showMessage(result)
            if self.system_tray:
                self.system_tray.showMessage(self.__title__, "Скачивание аудиозаписей завершено")
        else:
            if self.system_tray:
                self.system_tray.showMessage(
                    self.__title__,
                    "Во время скачивания аудиозаписей произошла ошибка",
                    QSystemTrayIcon.Critical,
                )
            self.statusBar.showMessage("При скачивании произошла ошибка: {}".format(result))
        self.download_audio_thread.albums = []
        self.download_audio_thread.tracks = None

    @pyqtSlot()
    def play_track(self):
        self.selected = self.trackList.selectedItems() or self.albumsList.selectedItems()
        selected_tracks = self._get_selected_tracks(self.selected)
        if not selected_tracks:
            # Play random track :)
            track = choice(self.tracks)
            selected_tracks.append(track)
            self.selected.append(self.trackList.findItems("{artist} - {title}".format(**track), Qt.MatchContains)[0])
        local = QUrl(selected_tracks[0]["url"])
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
        result = [i.text(0) for i in self.trackList.findItems(query, Qt.MatchContains)] + [
            i.text(0) for i in self.albumsList.findItems(query, Qt.MatchContains)
        ]
        for i in range(self.trackList.topLevelItemCount()):
            if not self.trackList.topLevelItem(i).text(0) in result:
                self.hidden_tracks.append(self.trackList.topLevelItem(i))
                self.trackList.topLevelItem(i).setHidden(True)
        for i in range(self.albumsList.topLevelItemCount()):
            if not self.albumsList.topLevelItem(i).text(0) in result:
                self.hidden_tracks.append(self.albumsList.topLevelItem(i))
                self.albumsList.topLevelItem(i).setHidden(True)

    @pyqtSlot()
    def copy_track_link(self):
        selected = self.trackList.selectedItems() or self.albumsList.selectedItems()
        selected_tracks = self._get_selected_tracks(selected)
        if selected_tracks:
            self.clipboard.setText(selected_tracks[0]["url"])

    @pyqtSlot(int)
    def change_volume(self, level):
        self.current_volume = level
        self.mediaPlayer.setVolume(self.current_volume)
        self.statusBar.showMessage("Текущая громкость: {}".format(self.current_volume))

    @pyqtSlot(int)
    def change_position(self, pos):
        self.mediaPlayer.setPosition(pos)

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Delete:
            self.trackList.clearSelection()
            self.albumsList.clearSelection()
        if e.key() == Qt.Key_Space:
            self._pause()

    def closeEvent(self, e):
        if self.system_tray:
            e.ignore()
            self.hide()
            self.system_tray.showMessage(
                self.__title__,
                "Программа была свернута в трей",
                QSystemTrayIcon.Information
            )

    @pyqtSlot("QTreeWidgetItem*")
    def on_item_expanded(self, item):
        if item.childCount():
            return
        for album in self.albums:
            if album["title"] == item.text(0):
                for track in album["tracks"]:
                    QTreeWidgetItem(item, ["{artist} - {title}".format(**track)])

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
        self.albumsList.setEnabled(state)
        self.saveData.setEnabled(state)
        self.search.setEnabled(state)
        self.btnConfirm.setEnabled(state)

    @pyqtSlot(str)
    def auth_handler(self, result):
        self.lock.lockForWrite()
        self.get_audio_thread.key = None
        num, ok = QInputDialog.getText(self, "Двухфакторная аутентификация", result)
        if ok:
            self.get_audio_thread.key = num
        self.lock.unlock()

    @pyqtSlot(QImage)
    def captcha_handler(self, image):
        self.lock.lockForWrite()
        self.get_audio_thread.key = None
        self.captchaDialog.imageLabel.setPixmap(QPixmap(image))
        self.captchaDialog.exec_()
        self.get_audio_thread.key = self.captchaDialog.captchaKey.text()
        self.captchaDialog.captchaKey.clear()
        self.lock.unlock()

    def _create_action(
        self,
        text,
        icon_path=None,
        status_tip=None,
        shortcut=None,
        set_enabled=True,
        callback=None,
    ):
        if icon_path:
            action = QAction(QIcon(icon_path), text, self)
        else:
            action = QAction(text, self)
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
            length += len(album["tracks"])
        return length

    def _get_selected_tracks(self, selected):
        selected_tracks = []
        for element in selected:
            if element.treeWidget().objectName() == "trackList":
                for track in self.tracks:
                    if element.text(0) in "{artist} - {title}".format(**track):
                        selected_tracks.append(track)
                        break
            else:
                for album in self.albums:
                    if element.parent().text(0) == album["title"]:
                        for track in album["tracks"]:
                            if element.text(0) in "{artist} - {title}".format(**track):
                                selected_tracks.append(track)
                                break
        return selected_tracks

    def _save_audio_list(self, output, save_links=True):
        with open(output, "w", encoding="utf-8") as f:
            f.write("{}, {} шт.".format(self.string, len(self.tracks)))
            if self.albums:
                f.write(" {} альбомов\n\n".format(len(self.albums)))
            else:
                f.write("\n")
            for track in self.tracks:
                if save_links:
                    f.write("{artist} - {title}: {url}\n\n".format(**track))
                else:
                    f.write("{artist} - {title}\n".format(**track))
            for album in self.albums:
                f.write("\nАльбом {title}:\n\n".format(**album))
                for track in album["tracks"]:
                    if save_links:
                        f.write("    {artist} - {title}: {url}\n\n".format(**track))
                    else:
                        f.write("    {artist} - {title}\n".format(**track))

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

    @pyqtSlot("qint64")
    def _position_changed(self, x):
        if self.selected:
            self.statusBar.showMessage(
                "Воспроизводится {}: {} / {} Громкость: {}".format(
                    self.selected[0].text(0),
                    self.time.addMSecs(x).toString("mm:ss"),
                    self.time.addMSecs(self.mediaPlayer.duration()).toString("mm:ss"),
                    self.current_volume,
                )
            )
            self.play_status.setValue(x)
            self.play_status.setMaximum(self.mediaPlayer.duration())

    @pyqtSlot("QPoint")
    def _show_context_menu(self, point):
        if self.download_audio_thread.isRunning():
            self.download.setEnabled(False)
        self.context_menu.exec(self.trackList.mapToGlobal(point))

    def _sort_by_artist(self):
        self.trackList.hideColumn(1)
        self.trackList.showColumn(0)
        self.trackList.sortItems(0, Qt.AscendingOrder)

    def _sort_by_name(self):
        self.trackList.hideColumn(0)
        self.trackList.showColumn(1)
        self.trackList.sortItems(1, Qt.AscendingOrder)

    @pyqtSlot()
    def _dump(self):
        result = {}
        if self.string:
            result["string"] = self.string
        if self.tracks:
            result["tracks"] = self.tracks.copy()
        if self.albums:
            result["albums"] = self.albums.copy()
        with open("dump.json", "w") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

    @pyqtSlot()
    def _load(self):
        try:
            with open("dump.json") as f:
                result = json.load(f)
        except FileNotFoundError:
            return
        else:
            self.audio_list_received((result["tracks"], result["string"], result["albums"]))


class HelpDialog(QDialog, Ui_helpDialog):
    def __init__(self, *args):
        super(HelpDialog, self).__init__(*args)
        self.setupUi(self)


class AboutDialog(QDialog, Ui_aboutDialog):
    def __init__(self, *args):
        super(AboutDialog, self).__init__(*args)
        self.setupUi(self)


class CaptchaDialog(QDialog, Ui_CaptchaRequest):
    def __init__(self, *args):
        super(CaptchaDialog, self).__init__(*args)
        self.setupUi(self)
