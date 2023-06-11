import binascii
import m3u8
import os

from tempfile import NamedTemporaryFile
from moviepy.audio.io.AudioFileClip import AudioFileClip
from Crypto.Cipher import AES
from urllib.request import urlopen


def get_key(data):
    for i in range(data.media_sequence):
        try:
            key_uri = data.keys[i].uri
            host_uri = "/".join(key_uri.split("/")[:-1])
            return host_uri
        except Exception:
            continue


def read_keys(path):
    data_response = urlopen(path)
    content = data_response.read()

    return content


def get_ts(url):
    data = m3u8.load(url)
    key_link = get_key(data)
    ts_content = b""
    key = None

    for i, segment in enumerate(data.segments):
        decrypt_func = lambda x: x
        if segment.key.method == "AES-128":
            if not key:
                key_uri = segment.key.uri
                key = read_keys(key_uri)
            ind = i + data.media_sequence
            iv = binascii.a2b_hex('%032x' % ind)
            cipher = AES.new(key, AES.MODE_CBC, iv=iv)
            decrypt_func = cipher.decrypt

        ts_url = f'{key_link}/{segment.uri}'
        coded_data = read_keys(ts_url)
        ts_content += decrypt_func(coded_data)
    return ts_content


def m3u8_to_mp3(url, name):
    ts_content = get_ts(url)
    if ts_content is None:
        raise TypeError("Empty mp3 content to save.")

    tmp_file = NamedTemporaryFile(delete=False, suffix=".mp3")
    tmp_file.write(ts_content)
    tmp_file.close()

    audioclip = AudioFileClip(tmp_file.name)
    audioclip.write_audiofile(name, bitrate="3000k")
    audioclip.close()
    os.unlink(tmp_file.name)
