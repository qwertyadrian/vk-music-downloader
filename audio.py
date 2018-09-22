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
from PyQt5.QtCore import QThread, pyqtSignal
import audio_gui
from vk_api import VkApi, exceptions
from vk_api.audio_url_decoder import decode_audio_url
from bs4 import BeautifulSoup
from wget import download
from re import sub


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
        tracks = []
        offset = 0
        url = 'https://m.vk.com/audios{}'
        session = VkApi(login=user_login, password=user_password, auth_handler=self.auth_handler,
                        config_filename=cookie)
        self.statusInfo.setText('Авторизация.')
        session.auth()
        api_vk = session.get_api()
        session.http.cookies.update(dict(remixmdevice='1920/1080/1/!!-!!!!'))
        user_id = userlink.replace('https://vk.com/', '').replace('https://m.vk.com/', '')
        me = api_vk.users.get()[0]
        if not user_id:
            user_id = None
        try:
            id = api_vk.users.get(user_ids=user_id)[0]
            url = url.format(id['id'])
            self.statusInfo.setText('Получение списка аудиозаписей пользователя: {} {}'.format(id['first_name'],
                                                                                                id['last_name']))
        except:
            id = None
        if not id:
            group_id = api_vk.groups.getById(group_id=user_id)[0]
            url = url.format(-int(group_id['id']))
            self.statusInfo.setText('Получение списка аудиозаписей сообщества: {}'.format(group_id['name']))
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
                temp.append({'artist': artist, 'title': title, 'duration': duration, 'link': link})
            tracks += temp[:-6]
            if int(soup.find_all('div', {'class': 'audioPage__count'})[0].string.split()[0]) <= offset:
                break
            offset += 50
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
        os.chdir('../')
        return 'Скачивание завершено'
    
    def run(self):
        result = self._download_audio(self.tracks, self.directory)
        self.signal.emit(result)

    def change_progress(self, n):
        self.int_signal.emit(n)
    

# noinspection PyArgumentList,PyCallByClass
class VkAudioApp(QtWidgets.QMainWindow, audio_gui.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        
        self.btnConfirm.clicked.connect(self.start)
        self.saveAll.clicked.connect(self.save_all)
        self.saveWithoutLinks.clicked.connect(self.save_without_links)
        self.downloadAll.clicked.connect(self.download_all)
        self.downloadSelected.clicked.connect(self.download_selected)
        
        self.get_audio = GetAudioListThread()
        self.get_audio.signal.connect(self.finished)
        self.get_audio.str_signal.connect(self.auth_handler)
        
        self.download_audio = DownloadAudio()
        self.download_audio.signal.connect(self.done)
        self.download_audio.int_signal.connect(self.change_progress)
        
        if info:
            self.login.setText(info[0])
            self.password.setText(info[1])
            self.user_link.setText(info[2])
        
        self.tracks = None
        self.string = None
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
        if self.enableSorting.isChecked():
            self.trackList.setSortingEnabled(True)
        else:
            self.trackList.setSortingEnabled(False)
        self.get_audio.login = self.login.text()
        self.get_audio.password = self.password.text()
        self.get_audio.user_link = self.user_link.text()
        self.get_audio.statusInfo = self.statusInfo
        self.btnConfirm.setEnabled(False)
        self.downloadAll.setEnabled(False)
        self.saveAll.setEnabled(False)
        self.saveWithoutLinks.setEnabled(False)
        self.downloadSelected.setEnabled(False)
        self.trackList.clear()
        self.statusInfo.setText('Процесс получение аудиозаписей начался.\n')
        self.get_audio.start()
        
    def finished(self, result):
        if result and isinstance(result, tuple):
            self.tracks = result[0]
            self.string = result[1]
            self.btnConfirm.setEnabled(True)
            self.statusInfo.setText('Список аудиозаписей получен.\n{}, {} шт.'.format(self.string, len(self.tracks)))
            #row = 0
            self.saveAll.setEnabled(True)
            self.saveWithoutLinks.setEnabled(True)
            self.downloadSelected.setEnabled(True)
            self.downloadAll.setEnabled(True)
            self.trackList.setEnabled(True)
            self.btnConfirm.setEnabled(True)
            for track in self.tracks:
                self.trackList.addItem('%(artist)s — %(title)s' % track)
                #self.trackList.setRowCount(len(self.tracks))
                #self.trackList.setItem(row, 0, QtWidgets.QTableWidgetItem(track['artist']))
                #self.trackList.setItem(row, 1, QtWidgets.QTableWidgetItem(track['title']))
                #row += 1
            #self.trackList.resizeColumnsToContents()
        elif isinstance(result, str):
            self.btnConfirm.setEnabled(True)
            self.statusInfo.setText('\nОшибка: ' + result)
    
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
            self.downloadAll.setEnabled(False)
            self.saveAll.setEnabled(False)
            self.saveWithoutLinks.setEnabled(False)
            self.downloadSelected.setEnabled(False)
            self.btnConfirm.setEnabled(False)
            self.download_audio.start()

    def download_selected(self):
        selected = self.trackList.selectedItems()
        selected_tracks = []
        for element in selected:
            for track in self.tracks:
                if element.text() in '%(artist)s — %(title)s' % track:
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
            self.downloadAll.setEnabled(False)
            self.saveAll.setEnabled(False)
            self.saveWithoutLinks.setEnabled(False)
            self.downloadSelected.setEnabled(False)
            self.btnConfirm.setEnabled(False)
            self.download_audio.start()
            
    
    def done(self, result):
        self.downloadAll.setEnabled(True)
        self.saveAll.setEnabled(True)
        self.saveWithoutLinks.setEnabled(True)
        self.downloadSelected.setEnabled(True)
        self.btnConfirm.setEnabled(True)
        self.statusInfo.setText(result)

    def change_progress(self, result):
        self.progressBar.setValue(result)
        

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
