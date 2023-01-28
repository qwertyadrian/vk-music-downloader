# -*- coding: utf-8 -*-

#  Copyright (C) 2018-2023 Adrian Polyakov
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
import shutil
from re import findall, sub
from tempfile import TemporaryDirectory, TemporaryFile

from mutagen.id3 import APIC, ID3, TIT2, TPE1, error
from mutagen.mp3 import MP3
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QImage
from vk_api import VkApi, exceptions
from vk_api.audio import VkAudio
from wget import download

from .converter import m3u8_to_mp3

MAX_FILENAME_LENGTH = 255


class GetAudioListThread(QThread):
    signal = pyqtSignal("PyQt_PyObject")
    str_signal = pyqtSignal(str)
    image_signal = pyqtSignal("QImage")

    def __init__(self, cookie):
        QThread.__init__(self)
        self.login = ""
        self.password = ""
        self.user_link = ""
        self.statusBar = None
        self.save_password = False
        self.authorized = False
        self.cookie = cookie
        self.key = None

    def __del__(self):
        self.wait()

    def _user_auth(self):
        if self.login:
            self.session = VkApi(
                login=self.login,
                password=self.password,
                auth_handler=self.auth_handler,
                captcha_handler=self.captcha_handler,
                config_filename=self.cookie,
                app_id=2685278,
                client_secret="lxhD8OD7dMsqtXIm5IUY",
            )
            self.statusBar.showMessage("Авторизация.")
            self.session.auth(token_only=True)
        else:
            raise exceptions.LoginRequired
            # self.statusBar.showMessage("Логин не указан, использование пароля в качестве токена")
            # self.session = VkApi(token=self.password, captcha_handler=self.captcha_handler)
        self.vk_audio = VkAudio(self.session)
        self.authorized = True

    def _get_audio(self):
        albums = []
        # Try to get post audio list
        post = self.get_group_and_post_id(self.user_link)
        album = self.get_album_id(self.user_link)
        if isinstance(post, tuple):
            owner_id, post_id = post
            self.statusBar.showMessage("Получение списка аудиозаписей поста.")
            string = "Аудиозаписи поста"
            tracks = self.vk_audio.get_post_audio(owner_id, post_id)
            audios = ",".join(["{owner_id}_{id}".format(**i) for i in tracks])
            tracks = self.session.method(method="audio.getById", values={"audios": audios})
        elif isinstance(album, tuple):
            owner_id, album_id, *_ = album
            self.statusBar.showMessage("Получение списка аудиозаписей альбома.")
            string = "Аудиозаписи альбома"
            tracks = self._get_tracks(owner_id, album_id)
        else:
            user_id = self.get_user_id(self.user_link)
            # Try to get user or group audio list
            # noinspection PyBroadException
            try:
                owner_id = self.session.method("users.get", dict(user_ids=user_id))[0]
                self.statusBar.showMessage(
                    "Получение списка аудиозаписей пользователя: {first_name} {last_name}".format(**owner_id)
                )
                string = "Музыка пользователя {first_name} {last_name}".format(**owner_id)
            except Exception:
                group_id = self.session.method("groups.getById", dict(group_id=user_id))[0]
                self.statusBar.showMessage("Получение списка аудиозаписей сообщества: {name}".format(**group_id))
                string = "Музыка сообщества {}".format(group_id["name"])
                albums = self._get_albums(-group_id["id"])
                tracks = self._get_tracks(-group_id["id"])
            else:
                albums = self._get_albums(owner_id["id"])
                tracks = self._get_tracks(owner_id["id"])
        for album in albums:
            try:
                album["tracks"] = self.vk_audio.get(
                    owner_id=album["owner_id"],
                    album_id=album["id"],
                    access_hash=album["access_hash"],
                )
            except:
                album["tracks"] = self._get_tracks(owner_id["id"], album["id"])
        return tracks, string, albums

    def _get_tracks(self, owner_id, album_id=None, access_hash=None):
        try:
            tracks = self.vk_audio.get(owner_id, album_id, access_hash)
        except:
            values = {"owner_id": owner_id}
            if album_id:
                values.update({"album_id": album_id})
            res = self.session.method(
                method="audio.get",
                values=values,
            )
            count = res["count"]
            offset = 0
            tracks = []
            while count != 0:
                audios = ",".join(["{owner_id}_{id}".format(**i) for i in res["items"]])
                tracks.extend(self.session.method(method="audio.getById", values={"audios": audios}))
                offset += 200 if count >= 200 else count % 200
                count -= 200 if count >= 200 else count % 200
                values.update({"offset": offset})
                res = self.session.method(
                    method="audio.get",
                    values=values,
                )
        return tracks

    def _get_albums(self, owner_id):
        try:
            albums = self.vk_audio.get_albums(owner_id["id"])
        except:
            res = self.session.method(
                method="audio.getPlaylists",
                values={"owner_id": owner_id},
            )
            count = res["count"]
            offset = 0
            albums = []
            while count != 0:
                albums.extend(res["items"])
                offset += 10 if count >= 10 else count % 10
                count -= 10 if count >= 10 else count % 10
                res = self.session.method(
                    method="audio.getPlaylists",
                    values={"owner_id": owner_id, "offset": offset},
                )
        return albums

    def auth_handler(self):
        """
        При двухфакторной аутентификации вызывается эта функция.
        :return: key, remember_device
        """
        self.str_signal.emit("Введите код авторизации:")
        while not self.key:
            pass
        return self.key, self.save_password

    def captcha_handler(self, captcha):
        url = captcha.get_url()
        file = TemporaryFile()
        res = self.session.http.get(url, stream=True)
        res.raw.decode_content = True
        shutil.copyfileobj(res.raw, file)
        file.seek(0)
        image = QImage()
        image.loadFromData(file.read())
        self.image_signal.emit(image)
        while not self.key:
            pass
        return captcha.try_again(self.key)

    def run(self):
        try:
            if not self.authorized:
                self._user_auth()
            result = self._get_audio()
            self.signal.emit(result)
        except exceptions.BadPassword:
            self.signal.emit("Неверный логин или пароль.")
        except exceptions.LoginRequired:
            self.signal.emit("Требуется логин.")
        except exceptions.PasswordRequired:
            self.signal.emit("Требуется пароль.")
        except (IndexError, AttributeError):
            self.signal.emit("Невозможно получить список аудиозаписей. Проверьте, открыты ли они у пользователя.")
        except exceptions.ApiError as e:
            if "113" in str(e):
                self.signal.emit("Неверная ссылка на профиль пользователя (неверный ID пользователя).")
            elif "100" in str(e):
                self.signal.emit("Неверная ссылка на профиль пользователя (сообщества).")
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
        link = link.replace("%2F", "/")
        result = findall(r"playlist/(.*)_(.*)_(.*)\?", link)
        if not result:
            result = findall(r"playlist/(.*)_(.*)_(.*)", link)
        if not result:
            result = findall(r"audio_playlist(.*)_(.*)&access_hash=(.*)", link)
        if not result:
            result = findall(r"audio_playlist(.*)_(.*)/(.*)", link)
        if not result:
            result = findall(r"audio_playlist(.*)_(.*)", link)
        return result[0] if result else None


class DownloadAudio(QThread):
    signal = pyqtSignal("PyQt_PyObject")
    int_signal = pyqtSignal(int)

    def __init__(self):
        QThread.__init__(self)
        self.statusBar = None
        self.progressBar = None
        self.tracks = None
        self.albums = []
        self.directory = None

    def __del__(self):
        self.wait()

    def _download_audio(self):
        n = 0
        for track in self.tracks:
            self._download(track)
            n += 1
            self.change_progress(n)
        for album in self.albums:
            self.directory /= album["title"]
            self.directory.mkdir(exist_ok=True)
            for track in album["tracks"]:
                self._download(track)
                n += 1
                self.change_progress(n)
            self.directory = self.directory.parent
        return "Скачивание завершено"

    def _download(self, track):
        name = "{artist} - {title}".format(**track)
        name = sub(r"[^a-zA-Z '#0-9.а-яА-Я()-]", "", name)[: MAX_FILENAME_LENGTH - 16] + ".mp3"
        self.statusBar.showMessage("Скачивается {}".format(name))
        out = self.directory / name
        m3u8_to_mp3(track['url'], name=str(out))
        # download(track["url"], out=str(out), bar=None)
        with TemporaryDirectory() as tempdir:
            if track.get("album"):
                for key in track["album"]["thumb"]:
                    if key.startswith("photo"):
                        track_cover = download(
                            track["album"]["thumb"][key].replace("impf/", ""),
                            tempdir,
                            bar=None,
                        )
            else:
                track_cover = None
            self.add_audio_tags(
                out,
                title=track["title"],
                artist=track["artist"],
                track_cover=track_cover,
            )

    def run(self):
        try:
            result = self._download_audio()
            self.signal.emit(result)
        except Exception as e:
            self.signal.emit(e)

    def change_progress(self, n):
        self.int_signal.emit(n)

    @staticmethod
    def add_audio_tags(filename, artist, title, track_cover):
        audio = MP3(filename, ID3=ID3)
        # add ID3 tag if it doesn't exist
        try:
            audio.add_tags()
        except error as e:
            if str(e) != "an ID3 tag already exists":
                return False
        audio.clear()

        if track_cover:
            audio.tags.add(
                APIC(
                    encoding=3,  # 3 is for utf-8
                    mime="image/png",  # image/jpeg or image/png
                    type=3,  # 3 is for the cover image
                    desc=u"Cover",
                    data=open(track_cover, "rb").read(),
                )
            )

        audio.tags.add(TIT2(encoding=3, text=title))
        audio.tags.add(TPE1(encoding=3, text=artist))

        audio.save()
        return True
