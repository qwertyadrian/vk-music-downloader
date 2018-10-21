#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" 
  Copyright (C) 2018 Adrian Polyakov

  This file is part of VkMusic Downloader
  
  VkMusic Downloader free software: you can redistribute it and/or modify
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
import sys
import os
import os.path
import getpass
import codecs
from PyQt5 import QtWidgets
from PyQt5.QtCore import QThread, pyqtSignal, QSizeF, QUrl, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QGraphicsVideoItem
import audio_gui
from vk_api import VkApi, exceptions
from vk_api.audio_url_decoder import decode_audio_url
from vk_api.audio import VkAudio
from bs4 import BeautifulSoup
from wget import download
from re import sub
from datetime import timedelta


class GetAudioListThread(QThread):
    signal = pyqtSignal('PyQt_PyObject')
    str_signal = pyqtSignal(str)

    def __init__(self):
        QThread.__init__(self)
        self.login = ''
        self.password = ''
        self.user_link = ''
        self.statusInfo = None

    def __del__(self):
        self.wait()

    def _get_user_audio(self, user_login, user_password, userlink):
        url = 'https://m.vk.com/audios{}'
        session = VkApi(login=user_login, password=user_password, auth_handler=self.auth_handler,
                        config_filename=cookie)
        self.statusInfo.setText('Авторизация.')
        session.auth()
        api_vk = session.get_api()
        vk_audio = VkAudio(session)
        session.http.cookies.update(dict(remixmdevice='1920/1080/1/!!-!!!!'))
        user_id = userlink.replace('https://vk.com/', '').replace('https://m.vk.com/', '')
        me = api_vk.users.get()[0]
        if not user_id:
            user_id = None
        # noinspection PyBroadException
        try:
            id = api_vk.users.get(user_ids=user_id)[0]
            url = url.format(id['id'])
            self.statusInfo.setText('Получение списка аудиозаписей пользователя: {} {}'.format(id['first_name'],
                                                                                               id['last_name']))
        except Exception:
            id = None
        if not id:
            group_id = api_vk.groups.getById(group_id=user_id)[0]
            url = url.format(-int(group_id['id']))
            self.statusInfo.setText('Получение списка аудиозаписей сообщества: {}'.format(group_id['name']))
        tracks, string = self._get_audio(session, url, me)
        albums = vk_audio.get_albums(id['id'])
        # a[:a.find('/audio?act=audio_playlist')] + a[a.rfind('/audio?act=audio_playlist'):]
        for album in albums:
            a = album['url']
            album['url'] = a[:a.find('/audio?act=audio_playlist')] + a[a.rfind('/audio?act=audio_playlist'):]
            album['tracks'], tmp = self._get_audio(session, album['url'], me)
        tracks.sort(key=lambda d: d['artist'])
        return tracks, string, albums

    @staticmethod
    def _get_audio(session, url, me):
        tracks = []
        offset = 0
        while True:
            response = session.http.get(url, params={'offset': offset}, allow_redirects=False)
            soup = BeautifulSoup(response.text, 'html.parser')
            temp = []
            for audio in soup.find_all('div', {'class': 'audio_item'}):
                # noinspection PyBroadException
                try:
                    artist = audio.select_one('.ai_artist').text
                    title = audio.select_one('.ai_title').text
                    duration = int(audio.select_one('.ai_dur')['data-dur'])
                    link = audio.select_one('.ai_body').input['value']
                except Exception:
                    continue
                if 'audio_api_unavailable' in link:
                    link = decode_audio_url(link, me['id'])
                temp.append({'artist': artist.lstrip(), 'title': title, 'duration': duration, 'link': link})
            if len(temp) < 6:
                tracks = temp.copy()
            else:
                tracks += temp[:-6]
            try:
                if int(soup.find_all('div', {'class': 'audioPage__count'})[0].string.split()[0]) <= offset:
                    break
                offset += 50
            except IndexError:
                break
        return tracks, soup.title.string

    def auth_handler(self):
        """
        При двухфакторной аутентификации вызывается эта функция.
        :return: key, remember_device
        """
        self.str_signal.emit('Введите код авторизации:')
        while not window.key:
            pass
        return window.key, True

    def run(self):
        try:
            result = self._get_user_audio(self.login, self.password, self.user_link)
            self.signal.emit(result)
        except exceptions.BadPassword:
            self.signal.emit('Неверный логин или пароль.')
        except exceptions.LoginRequired:
            self.signal.emit('Требуется логин.')
        except exceptions.PasswordRequired:
            self.signal.emit('Требуется пароль.')
        except IndexError:
            self.signal.emit('Невозможно получить список аудиозаписей. Проверьте, открыты ли они у пользователя.')
        except exceptions.ApiError as e:
            if '113' in str(e):
                self.signal.emit('Неверная ссылка на профиль пользователя (неверный ID пользователя).')
            elif '100' in str(e):
                self.signal.emit('Неверная ссылка на профиль пользователя (сообщества).')
            else:
                self.signal.emit(str(e))
        except Exception as e:
            print(type(e))
            self.signal.emit(str(e))


class DownloadAudio(QThread):
    signal = pyqtSignal('PyQt_PyObject')
    int_signal = pyqtSignal(int)

    def __init__(self):
        QThread.__init__(self)
        self.statusInfo = None
        self.progressBar = None
        self.tracks = None
        self.directory = None

    def __del__(self):
        self.wait()

    def _download_audio(self, track_list, directory):
        os.chdir(directory)
        n = 0
        for track in track_list:
            name = '%(artist)s - %(title)s.mp3' % track
            name = sub(r"[/\"?:|<>*]", '', name)
            if len(name) > 127:
                name = name[:126]
            self.statusInfo.setText('Скачивается {}'.format(name))
            download(track['link'], out=name, bar=None)
            n += 1
            self.change_progress(n)
        return 'Скачивание завершено'

    def run(self):
        try:
            result = self._download_audio(self.tracks, self.directory)
            self.signal.emit(result)
        except Exception as e:
            self.signal.emit(e)

    def change_progress(self, n):
        self.int_signal.emit(n)


# noinspection PyArgumentList,PyCallByClass
class VkAudioApp(QtWidgets.QMainWindow, audio_gui.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.statusBar()

        self.btnConfirm.clicked.connect(self.start)

        self.saveAll = QtWidgets.QAction(QIcon('save_all.png'), '&Сохранить', self)
        self.saveAll.setStatusTip('Сохранить список аудиозаписей в файл со ссылками для их скачивания')
        self.saveAll.setShortcut('Ctrl+S')
        self.saveAll.setEnabled(False)
        self.saveAll.triggered.connect(self.save_all)

        self.saveWithoutLinks = QtWidgets.QAction(QIcon('save_without_links.png'), '&Сохранить без ссылок', self)
        self.saveWithoutLinks.setStatusTip('Сохранить список аудиозаписей в файл без ссылок для их скачивания')
        self.saveWithoutLinks.setShortcut('Ctrl+Shift+S')
        self.saveWithoutLinks.setEnabled(False)
        self.saveWithoutLinks.triggered.connect(self.save_without_links)

        self.downloadAll = QtWidgets.QAction(QIcon('download_all.png'), '&Скачать всё', self)
        self.downloadAll.setStatusTip('Скачать все аудиозаписи из списка ниже')
        self.downloadAll.setShortcut('Ctrl+D')
        self.downloadAll.setEnabled(False)
        self.downloadAll.triggered.connect(self.download_all)

        self.downloadSelected = QtWidgets.QAction(QIcon('download_selected.png'), '&Скачать выбранное', self)
        self.downloadSelected.setStatusTip('Скачать выбранные ауиозаписи из списка ниже')
        self.downloadSelected.setShortcut('Ctrl+Shift+D')
        self.downloadSelected.setEnabled(False)
        self.downloadSelected.triggered.connect(self.download_selected)

        menu_bar = self.menuBar()
        music_menu = menu_bar.addMenu('&Музыка')
        music_menu.addAction(self.saveAll)
        music_menu.addAction(self.saveWithoutLinks)
        music_menu.addAction(self.downloadAll)
        music_menu.addAction(self.downloadSelected)

        self.trackList.itemDoubleClicked.connect(self.play_track)
        self.trackList.itemExpanded.connect(self.on_item_expanded)

        self.get_audio = GetAudioListThread()
        self.get_audio.signal.connect(self.finished)
        self.get_audio.str_signal.connect(self.auth_handler)

        self.download_audio = DownloadAudio()
        self.download_audio.signal.connect(self.done)
        self.download_audio.int_signal.connect(lambda x: self.progressBar.setValue(x))

        video_item = QGraphicsVideoItem()
        self.current_volume = 100
        video_item.setSize(QSizeF(1, 1))
        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.mediaPlayer.setVideoOutput(video_item)
        self.mediaPlayer.stateChanged.connect(lambda x: [self.toggle_buttons(True), self.toggle_fields(True)])
        self.mediaPlayer\
            .positionChanged.connect(lambda x:
                                     self.statusBar().showMessage('Воспроизводится {}: {} / {} Громкость: {}'.format(
                                         self.selected[0].text(0), timedelta(milliseconds=x),
                                         timedelta(milliseconds=self.mediaPlayer.duration()), self.current_volume)))
        
        if info:
            self.login.setText(info[0])
            self.password.setText(info[1])
            self.user_link.setText(info[2])

        # TODO Реализовать автообновление программы

        self.selected = None
        self.tracks = None
        self.string = None
        self.albums = None
        self.key = None

    def auth_handler(self, result):
        self.key = None
        num, ok = QtWidgets.QInputDialog.getText(self, 'Двухфакторная аутентификация', result)
        if ok:
            self.key = num

    def start(self):
        if self.saveData.isChecked():
            with open(config, 'wb') as d:
                data = self.login.text() + '|' + self.password.text() + '|' + self.user_link.text()
                data_crypted = codecs.encode(bytes(data, 'utf-8'), 'hex')
                d.write(data_crypted)
        self.get_audio.login = self.login.text()
        self.get_audio.password = self.password.text()
        self.get_audio.user_link = self.user_link.text()
        self.get_audio.statusInfo = self.statusInfo
        self.toggle_buttons(False)
        self.trackList.clear()
        self.statusInfo.setText('Процесс получение аудиозаписей начался.\n')
        self.get_audio.start()
        
    def finished(self, result):
        if result and isinstance(result, tuple):
            self.tracks = result[0]
            self.string = result[1]
            self.albums = result[2]
            self.statusInfo.setText('Список аудиозаписей получен.'
                                    ' Зажмите Ctrl для множественного выбора'
                                    '\n{}, {} шт.'.format(self.string, len(self.tracks)))
            # row = 0
            self.trackList.setEnabled(True)
            self.toggle_buttons(True)
            for track in self.tracks:
                self.trackList.addTopLevelItem(QtWidgets.QTreeWidgetItem(self.trackList,
                                                                         ['%(artist)s — %(title)s' % track]))
            for album in self.albums:
                root = QtWidgets.QTreeWidgetItem(self.trackList, [album['title']])
                root.setChildIndicatorPolicy(QtWidgets.QTreeWidgetItem.ShowIndicator)
                root.setFlags(Qt.ItemIsEnabled)
                self.trackList.addTopLevelItem(root)
                # TODO Изучить работу с таблицами в PyQt5
                # self.trackList.setRowCount(len(self.tracks))
                # self.trackList.setItem(row, 0, QtWidgets.QTableWidgetItem(track['artist']))
                # self.trackList.setItem(row, 1, QtWidgets.QTableWidgetItem(track['title']))
                # row += 1
            # self.trackList.resizeColumnsToContents()
        elif isinstance(result, str):
            self.btnConfirm.setEnabled(True)
            self.statusInfo.setText('<html><head/><body><p><span style=" color:#ff0000;">Ошибка: {}'
                                    '</span></p></body></html>'.format(result))
    
    def save_all(self):
        directory = QtWidgets.QFileDialog.getSaveFileName(self, 'Сохранить как', filter='Text files (*.txt)')[0]
        if not directory.endswith('.txt'):
            directory += '.txt'
        if directory and self.tracks and self.string:
            with open(directory, 'w', encoding='utf-8') as d:
                print('{}, {} шт.\n'.format(self.string, len(self.tracks)), file=d)
                for track in self.tracks:
                    print('%(artist)s - %(title)s: %(link)s\n' % track, file=d)
            self.statusInfo.setText('Список аудиозаписей сохранен в файл {}'.format(directory))
    
    def save_without_links(self):
        directory = QtWidgets.QFileDialog.getSaveFileName(self, 'Сохранить как', filter='Text files (*.txt)')[0]
        if not directory.endswith('.txt'):
            directory += '.txt'
        if directory and self.tracks and self.string:
            with open(directory, 'w', encoding='utf-8') as d:
                print('{}, {} шт.\n'.format(self.string, len(self.tracks)), file=d)
                for track in self.tracks:
                    print('%(artist)s - %(title)s' % track, file=d)
            self.statusInfo.setText('Список аудиозаписей (без ссылок на скачивание) сохранен в файл {}'
                                    .format(directory))

    def download_all(self):
        directory = QtWidgets.QFileDialog.getExistingDirectory(self, "Выберите папку")
        if directory:
            self.download_audio.statusInfo = self.statusInfo
            self.download_audio.tracks = self.tracks
            self.download_audio.directory = directory
            self.statusInfo.setText('Процесс скачивания аудиозаписей начался.')
            self.progress_label.setEnabled(True)
            self.progressBar.setEnabled(True)
            self.progressBar.setMaximum(len(self.tracks))
            self.toggle_buttons(False)
            self.download_audio.start()

    def download_selected(self):
        directory = None
        selected = self.trackList.selectedItems()
        selected_tracks = []
        for element in selected:
            for track in self.tracks:
                if element.text(0) in '%(artist)s — %(title)s' % track:
                    selected_tracks.append(track)
                    break
        if selected_tracks:
            directory = QtWidgets.QFileDialog.getExistingDirectory(self, "Выберите папку")
        if directory:
            self.download_audio.statusInfo = self.statusInfo
            self.download_audio.tracks = selected_tracks
            self.download_audio.directory = directory
            self.statusInfo.setText('Процесс скачивания аудиозаписей начался.')
            self.progress_label.setEnabled(True)
            self.progressBar.setEnabled(True)
            self.progressBar.setMaximum(len(selected_tracks))
            self.toggle_buttons(False)
            self.download_audio.start()
        else:
            self.statusInfo.setText('<html><head/><body><p><span style=" color:#ff0000;">'
                                    'Ничего не выбрано для скачивания или было отменено диалоговое с выбором папки'
                                    '</span></p></body></html>')
            
    def done(self, result):
        self.toggle_buttons(True)
        if isinstance(result, str):
            self.statusInfo.setText(result)
        else:
            self.statusInfo.setText('<html><head/><body><p><span style=" color:#ff0000;">При скачивании'
                                    ' произошла ошибка: {}'
                                    '</span></p></body></html>'.format(result))

    def play_track(self):
        self.selected = self.trackList.selectedItems()
        selected_tracks = []
        for track in self.tracks:
            if self.selected[0].text(0) in '%(artist)s — %(title)s' % track:
                selected_tracks.append(track)
                break
        if not selected_tracks:
            for album in self.albums:
                for track in album['tracks']:
                    if self.selected[0].text(0) in '%(artist)s — %(title)s' % track:
                        selected_tracks.append(track)
                        break
        local = QUrl(selected_tracks[0]['link'])
        media = QMediaContent(local)
        self.mediaPlayer.setMedia(media)
        self.mediaPlayer.play()
        self.toggle_fields(False)
        self.toggle_buttons(False)
        self.downloadSelected.setEnabled(True)

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Alt:
            self.mediaPlayer.stop()
            self.toggle_fields(True)
            self.toggle_buttons(True)
        elif e.key() == Qt.Key_Up:
            if self.current_volume < 100:
                self.current_volume += 2
                self.mediaPlayer.setVolume(self.current_volume)
            self.statusBar().showMessage('Текущая громкость: {}'.format(self.current_volume))
        elif e.key() == Qt.Key_Down:
            if self.current_volume > 0:
                self.current_volume -= 2
                self.mediaPlayer.setVolume(self.current_volume)
            self.statusBar().showMessage('Текущая громкость: {}'.format(self.current_volume))
        elif e.key() == Qt.Key_Space:
            if self.mediaPlayer.state() == 1:
                self.mediaPlayer.pause()
                self.toggle_fields(False)
                self.toggle_buttons(False)
                self.downloadSelected.setEnabled(True)
            elif self.mediaPlayer.state() == 2:
                self.mediaPlayer.play()
                self.toggle_fields(False)
                self.toggle_buttons(False)
                self.downloadSelected.setEnabled(True)
        elif e.key() == Qt.Key_Left:
            self.mediaPlayer.setPosition(self.mediaPlayer.position() - 2000)
        elif e.key() == Qt.Key_Right:
            self.mediaPlayer.setPosition(self.mediaPlayer.position() + 2000)

    def on_item_expanded(self, item):
        if item.childCount():
            return
        for album in self.albums:
            if album['title'] == item.text(0):
                for track in album['tracks']:
                    QtWidgets.QTreeWidgetItem(item, ['%(artist)s — %(title)s' % track])

    def toggle_buttons(self, state: bool):
        self.downloadAll.setEnabled(state)
        self.saveAll.setEnabled(state)
        self.saveWithoutLinks.setEnabled(state)
        self.downloadSelected.setEnabled(state)
        self.btnConfirm.setEnabled(state)

    def toggle_fields(self, state: bool):
        self.login.setEnabled(state)
        self.password.setEnabled(state)
        self.user_link.setEnabled(state)
        self.trackList.setEnabled(state)
        self.saveData.setEnabled(state)


def ui():
    global window
    app = QtWidgets.QApplication(sys.argv)
    window = VkAudioApp()
    window.show()
    app.exec_()


if __name__ == '__main__':
    info = None
    user = ''
    if os.name == 'posix':
        user = ''
    elif os.name == 'nt':
        user = getpass.getuser()
    home = os.path.join(os.path.expanduser('~' + user), '.vk_downloader')
    config = os.path.join(home, '.config.ini')
    cookie = os.path.join(home, 'vk_cookies.json')
    if os.path.exists(home):
        if os.path.exists(config):
            with open(config, 'rb') as f:
                info_crypted = f.read()
                info = codecs.decode(info_crypted, 'hex').decode().split('|')
    else:
        os.mkdir(home)
    ui()
