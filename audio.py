#!/usr/bin/env python3
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
import os.path
import sys
import tempfile

from keyrings.cryptfile.cryptfile import CryptFileKeyring
from PyQt5 import QtWidgets

from audio_app import VkAudioApp


def ui():
    app = QtWidgets.QApplication(sys.argv)
    window = VkAudioApp(info, cookie, keyring)
    window.show()
    app.exec_()


if __name__ == "__main__":
    keyring = CryptFileKeyring()
    keyring.keyring_key = os.getlogin()
    home = os.path.join(os.path.expanduser("~"), ".vk_downloader")
    if not os.path.exists(os.path.dirname(home)):
        home = tempfile.TemporaryDirectory()
    cookie = os.path.join(home, "vk_cookies.json")
    data = keyring.get_password("vk_music_downloader", os.getlogin())
    if isinstance(data, str):
        info = data.split("|")
    else:
        info = None
    if not os.path.exists(home):
        os.mkdir(home)
    ui()
