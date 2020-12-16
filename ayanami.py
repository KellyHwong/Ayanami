#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : Dec-14-20 21:44
# @Author  : Kelly Hwong (dianhuangkan@gmail.com)

import os
import requests
import re
from bs4 import BeautifulSoup
import json
from urllib.parse import unquote
from utils.dir_utils import makedir_exist_ok


class Ayanami(object):
    """docstring for Ayanami"""

    def __init__(self, page_url):
        self.headers = {
            "DNT": "1",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36"
        }

        self.page_url = page_url
        # configs
        self.chapterPath = "benzi"
        self.download_processes_num = 4

        self.page_html = None
        self.voice_tables = None
        self.voice_metas = None

    def _get_page_html(self):
        page_html = requests.get(self.page_url, headers=self.headers).content
        page_html = page_html.decode("utf-8")
        self.page_html = page_html

    def store_page_html(self):
        with open("debug_ayanami.html", "w", encoding="utf-8") as f:
            f.write(self.page_html)

    def _get_voice_tables(self):
        assert self.page_html is not None
        soup = BeautifulSoup(self.page_html, "lxml")
        wikitables = soup.find_all("table", {"class": "wikitable"})
        voice_tables = []
        for i, table in enumerate(wikitables):
            tds = table.find("tr").find_all("td")
            if len(tds) == 3 and tds[-1].find("div", {"data-bind": re.compile(r".*")}):
                voice_tables.append(table)

        self.voice_tables = voice_tables

    def _get_voice_metas(self):
        self.voice_metas = []
        for table in self.voice_tables:
            trs = table.find_all("tr")
            for tr in trs:
                tds = tr.find_all("td")
                div_data = tds[-1].find("div",
                                        {"data-bind": re.compile(r".*")})
                if div_data:
                    data_bind = div_data["data-bind"]
                    voice_meta = json.loads(data_bind)
                    self.voice_metas.append(voice_meta)

    def _download_voice(self, voice_meta, folder):
        """_download_voice
        # Arguments:
            voice_meta voice meta data contained in the div_data
        """
        playlist = voice_meta["component"]["params"]["playlist"]
        assert len(playlist) == 1
        file_url = playlist[0]["audioFileUrl"]
        navigation_url = playlist[0]["navigationUrl"]
        file_name = unquote(navigation_url.split(":")[1])
        if not os.path.isdir(folder):
            makedir_exist_ok(folder)
        file_path = os.path.join(folder, file_name)
        data = requests.get(file_url).content
        with open(file_path, "wb") as f:
            f.write(data)
        print(f"Downloaded to {file_path}.")

    def _download_voices(self):
        print(
            f"{self.__class__} has {len(self.voice_metas)} voices. Now downloading...")
        for voice_meta in self.voice_metas:
            self._download_voice(voice_meta)
        print("Download complete!")

    def test(self):
        self._get_page_html()
        self.store_page_html()
        self._get_voice_tables()
        self._get_voice_metas()
        self._download_voices()


def ayanami_main():
    from character_urls import ayanami_url
    ayanami = Ayanami(ayanami_url)
    ayanami.test()


def main():
    ayanami_main()


if __name__ == "__main__":
    main()
