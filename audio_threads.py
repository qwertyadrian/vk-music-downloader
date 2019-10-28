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
import os
import os.path
import subprocess
from re import sub

from PyQt5.QtCore import QThread, pyqtSignal
from vk_api import VkApi, exceptions
from vk_api.audio import VkAudio


class GetAudioListThread(QThread):
    signal = pyqtSignal('PyQt_PyObject')
    str_signal = pyqtSignal(str)

    def __init__(self, cookie, window):
        QThread.__init__(self)
        self.login = ''
        self.password = ''
        self.user_link = ''
        self.statusInfo = None
        self.cookie = cookie
        self.window = window

    def __del__(self):
        self.wait()

    def _get_user_audio(self, user_login, user_password, userlink):
        string = ''
        session = VkApi(login=user_login, password=user_password, auth_handler=self.auth_handler,
                        config_filename=self.cookie)
        self.statusInfo.setText('Авторизация.')
        session.auth()
        api_vk = session.get_api()
        vk_audio = VkAudio(session)
        session.http.cookies.update(dict(remixmdevice='1920/1080/1/!!-!!!!'))
        user_id = userlink.replace('https://vk.com/', '').replace('https://m.vk.com/', '')
        if not user_id:
            user_id = None
        # noinspection PyBroadException
        try:
            id = api_vk.users.get(user_ids=user_id)[0]
            self.statusInfo.setText('Получение списка аудиозаписей пользователя: {} {}'.format(id['first_name'],
                                                                                               id['last_name']))
            string = 'Музыка пользователя: {} {}'.format(id['first_name'], id['last_name'])
        except Exception:
            id = None
        if not id:
            group_id = api_vk.groups.getById(group_id=user_id)[0]
            self.statusInfo.setText('Получение списка аудиозаписей сообщества: {}'.format(group_id['name']))
            string = 'Музыка сообщества: {}'.format(group_id['name'])
            albums = vk_audio.get_albums(-group_id['id'])
            tracks = vk_audio.get(-group_id['id'])
        else:
            albums = vk_audio.get_albums(id['id'])
            tracks = vk_audio.get(id['id'])
        for album in albums:
            album['tracks'] = vk_audio.get(owner_id=album['owner_id'],
                                           album_id=album['id'],
                                           access_hash=album['access_hash'])
        tracks.sort(key=lambda d: d['artist'])
        return tracks, string, albums

    def auth_handler(self):
        """
        При двухфакторной аутентификации вызывается эта функция.
        :return: key, remember_device
        """
        self.str_signal.emit('Введите код авторизации:')
        while not self.window.key:
            pass
        return self.window.key, True

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
        except (IndexError, AttributeError):
            self.signal.emit('Невозможно получить список аудиозаписей. Проверьте, открыты ли они у пользователя.')
        except exceptions.ApiError as e:
            if '113' in str(e):
                self.signal.emit('Неверная ссылка на профиль пользователя (неверный ID пользователя).')
            elif '100' in str(e):
                self.signal.emit('Неверная ссылка на профиль пользователя (сообщества).')
            else:
                self.signal.emit(str(e))
        except Exception as e:
            self.signal.emit(str(type(e)) + str(e))


class DownloadAudio(QThread):
    signal = pyqtSignal('PyQt_PyObject')
    int_signal = pyqtSignal(int)

    def __init__(self):
        QThread.__init__(self)
        self.statusInfo = None
        self.progressBar = None
        self.tracks = None
        self.albums = []
        self.directory = None

    def __del__(self):
        self.wait()

    def _download_audio(self):
        os.chdir(self.directory)
        n = 0
        for track in self.tracks:
            self._download(track)
            n += 1
            self.change_progress(n)
        for album in self.albums:
            path = './' + album['title']
            os.mkdir(path)
            os.chdir(path)
            for track in album['tracks']:
                self._download(track)
                n += 1
                self.change_progress(n)
            os.chdir('../')
        return 'Скачивание завершено'

    def _download(self, track):
        name = '%(artist)s - %(title)s.mp3' % track
        name = sub(r"[/\"?:|<>*\n\r\xa0]", '', name).strip().replace('\t', ' ')
        if len(name) > 127:
            name = name[:126]
        self.statusInfo.setText('Скачивается {}'.format(name))
        subprocess.call(['ffmpeg', '-i', track['url'], '-c', 'copy', name])

    def run(self):
        try:
            result = self._download_audio()
            self.signal.emit(result)
        except Exception as e:
            self.signal.emit(e)

    def change_progress(self, n):
        self.int_signal.emit(n)
