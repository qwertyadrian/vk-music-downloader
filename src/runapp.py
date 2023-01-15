#!/usr/bin/env python3
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
import os
import sys
import tempfile

from pathlib import Path

from keyrings.cryptfile.cryptfile import CryptFileKeyring
from PyQt5 import QtWidgets

from vkmusicd.gui.mainwindow import MainWindow


if __name__ == "__main__":
    keyring = CryptFileKeyring()
    keyring.keyring_key = os.getlogin()
    home = Path.home() / ".vk_downloader"
    try:
        home.mkdir(exist_ok=True)
    except (PermissionError, FileNotFoundError):
        home = tempfile.TemporaryDirectory()
    cookie = home / "vk_cookies.json"
    data = keyring.get_password("vk_music_downloader", os.getlogin())
    if isinstance(data, str):
        info = data.split("|")
    else:
        info = None
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow(info, cookie, keyring)
    window.show()
    sys.exit(app.exec())
