# -*- coding: utf-8 -*-

#  Copyright (C) 2018-2020 Adrian Polyakov
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
from re import sub, findall
from collections import Counter

from PyQt5.QtCore import QThread, pyqtSignal
from vk_api import VkApi, exceptions
from vk_api.audio import VkAudio, scrap_data
from wget import download


class GetAudioListThread(QThread):
    signal = pyqtSignal('PyQt_PyObject')
    str_signal = pyqtSignal(str)

    def __init__(self, cookie, window):
        QThread.__init__(self)
        self.login = ''
        self.password = ''
        self.user_link = ''
        self.statusInfo = None
        self.save_password = False
        self.authorized = False
        self.cookie = cookie
        self.window = window

    def __del__(self):
        self.wait()

    def _user_auth(self):
        self.session = VkApi(login=self.login, password=self.password, auth_handler=self.auth_handler,
                             config_filename=self.cookie)
        self.statusInfo.setText('Авторизация.')
        self.session.auth()
        self.session.http.cookies.update(dict(remixmdevice='1920/1080/1/!!-!!!!'))
        self.vk_audio = VkAudio(self.session)
        self.authorized = True

    def _get_audio(self):
        tracks = []
        albums = []
        string = str()
        # Try to get post audio list
        post = self.get_group_and_post_id(self.user_link)
        album = self.get_album_id(self.user_link)
        if isinstance(post, tuple):
            owner_id, post_id = post
            link = 'https://m.vk.com/wall{}_{}'.format(owner_id, post_id)
            self.statusInfo.setText('Получение списка аудиозаписей поста.')
            string = 'Аудиозаписи поста'
            response = self.session.http.get(link)
            tracks = scrap_data(response.text, self.vk_audio.user_id, filter_root_el={'class': 'audios_list'})
        elif isinstance(album, tuple):
            owner_id, album_id, access_hash = album
            self.statusInfo.setText('Получение списка аудиозаписей альбома.')
            string = 'Аудиозаписи альбома'
            tracks = self.vk_audio.get(owner_id, album_id, access_hash)
        else:
            user_id = self.get_user_id(self.user_link)
            # Try to get user or group audio list
            # noinspection PyBroadException
            try:
                owner_id = self.session.method('users.get', dict(user_ids=user_id))[0]
                self.statusInfo.setText(
                    'Получение списка аудиозаписей пользователя: {} {}'.format(owner_id['first_name'],
                                                                               owner_id['last_name']))
                string = 'Музыка пользователя: {} {}'.format(owner_id['first_name'],
                                                             owner_id['last_name'])
            except Exception:
                group_id = self.session.method('groups.getById', dict(group_id=user_id))[0]
                self.statusInfo.setText('Получение списка аудиозаписей сообщества: {}'.format(group_id['name']))
                string = 'Музыка сообщества: {}'.format(group_id['name'])
                albums = self.vk_audio.get_albums(-group_id['id'])
                tracks = self.vk_audio.get(-group_id['id'])
            else:
                albums = self.vk_audio.get_albums(owner_id['id'])
                tracks = self.vk_audio.get(owner_id['id'])
        for album in albums:
            album['tracks'] = self.vk_audio.get(owner_id=album['owner_id'], album_id=album['id'],
                                                access_hash=album['access_hash'])
        # Removing duplicates
        names = []
        for track in tracks:
            names.append((track['artist'], track['title']))
        stats = Counter(names)

        for i, n in stats.most_common():
            if n >= 2:
                for track in tracks:
                    if track['artist'] == i[0] and track['title'] == i[1]:
                        tracks.remove(track)
                        break
        # Sorting tracks
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
        return self.window.key, self.save_password

    def run(self):
        try:
            if not self.authorized:
                self._user_auth()
            result = self._get_audio()
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

    @staticmethod
    def get_user_id(link):
        result = findall(r"(https?://m?\.?vk\.com/)?(.*)$", link)[0][1]
        return result if result else None

    @staticmethod
    def get_group_and_post_id(link):
        result = findall(r"wall(.*?)_(.*?)$", link)
        return result[0] if result else None

    @staticmethod
    def get_album_id(link):
        link = link.replace('%2F', '/')
        result = findall(r"album/(.*)_(.*)_(.*)\?", link)
        if not result:
            result = findall(r"album/(.*)_(.*)_(.*)", link)
        if not result:
            result = findall(r"audio_playlist(.*)_(.*)&access_hash=(.*)", link)
        if not result:
            result = findall(r"audio_playlist(.*)_(.*)/(.*)", link)
        return result[0] if result else None


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
        download(track['url'], out=name, bar=None)

    def run(self):
        try:
            result = self._download_audio()
            self.signal.emit(result)
        except Exception as e:
            self.signal.emit(e)

    def change_progress(self, n):
        self.int_signal.emit(n)
