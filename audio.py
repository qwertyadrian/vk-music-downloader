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
import os.path
import getpass
import codecs
import tempfile
from PyQt5 import QtWidgets
from audio_app import VkAudioApp


def ui():
    app = QtWidgets.QApplication(sys.argv)
    window = VkAudioApp(info, config, cookie)
    window.show()
    app.exec_()


if __name__ == '__main__':
    info = None
    user = ''
    if os.name == 'posix':
        pass
    elif os.name == 'nt':
        user = getpass.getuser()
    home = os.path.join(os.path.expanduser('~' + user), '.vk_downloader')
    if not os.path.exists(os.path.join(os.path.expanduser('~' + user))):
        home = tempfile.TemporaryDirectory()
    config = os.path.join(home, '.config.ini')
    cookie = os.path.join(home, 'vk_cookies.json')
    if os.path.exists(home):
        if os.path.exists(config):
            with open(config, 'rb') as f:
                info_encrypted = f.read()
                info = codecs.decode(info_encrypted, 'hex').decode().split('|')
    else:
        os.mkdir(home)
    ui()
