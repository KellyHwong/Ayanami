#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : Dec-14-20 21:44
# @Author  : Kelly Hwong (dianhuangkan@gmail.com)

import os
import csv
import requests
import re
from bs4 import BeautifulSoup
import json
from urllib.parse import urlparse, unquote
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
        self.num_download_processes = 4

        self.page_html = None
        self.voice_tables = None
        self.voice_metas = []

    def _get_page_html(self):
        page_html = requests.get(self.page_url, headers=self.headers).content
        page_html = page_html.decode("utf-8")
        self.page_html = page_html

    def store_page_html(self):
        with open("./ayanami/debug_ayanami.html", "w", encoding="utf-8") as f:
            f.write(self.page_html)

    def _get_voice_tables(self):
        assert self.page_html is not None
        soup = BeautifulSoup(self.page_html, "lxml")
        wikitables = soup.find_all("table", {"class": "wikitable"})
        voice_tables = []
        for table in wikitables:
            tds = table.find("tr").find_all("td")
            if len(tds) == 3 and tds[-1].find("div", {"data-bind": re.compile(r".*")}):
                voice_tables.append(table)

        self.voice_tables = voice_tables

    def _get_voice_metas(self):
        for table in self.voice_tables:
            trs = table.find_all("tr")

            scenario, dialogue, rowspan = "", "", 0
            for i, _ in enumerate(trs):
                tr = trs[i]

                tds = tr.find_all("td")
                if len(tds) == 3:
                    scenario = tds[0].text
                td_rowspan = tr.find("td",
                                     {"rowspan": re.compile(r".*")})
                if td_rowspan:
                    rowspan = int(td_rowspan["rowspan"])

                if rowspan > 0:
                    dialogue = tds[0].text
                    div_data = tds[1].find("div",
                                           {"data-bind": re.compile(r".*")})
                    rowspan -= 1
                else:  # there is no td with "rowspan" attribute
                    dialogue = tds[1].text
                    div_data = tds[2].find("div",
                                           {"data-bind": re.compile(r".*")})

                if div_data:  # if here is a play voice button
                    data_bind = div_data["data-bind"]
                    voice_meta = json.loads(data_bind)
                    playlist = voice_meta["component"]["params"]["playlist"]
                    assert len(playlist) == 1
                    url = playlist[0]["audioFileUrl"]
                    filename = os.path.basename((unquote(urlparse(url).path)))
                    self.voice_metas.append(
                        [filename, scenario, dialogue, url])

        csv_file = "mp3/audio_files.csv"
        with open(csv_file, 'w', newline="") as f:
            writer = csv.writer(f)
            writer.writerow(
                ["filename", "scenario", "dialogue", "url"])
            writer.writerows(self.voice_metas)
            print(f"Voice metas stored to CSV file: {csv_file}.")

    def _download(self, url, headers="", folder="", filename="", retried=0):
        """_download
        # Arguments:
            url:
        """
        filename = filename if filename else os.path.basename(
            (unquote(urlparse(url).path)))

        if not os.path.isdir(folder):
            makedir_exist_ok(folder)
        filepath = os.path.join(folder, filename)

        data = requests.get(url).content
        with open(filepath, "wb") as f:
            f.write(data)
        print(f"Downloaded to {filepath}.")

    def _download_voices(self):
        print(
            f"{self.__class__} has {len(self.voice_metas)} voices. Now downloading...")
        for voice_meta in self.voice_metas:
            pass
            # self._download(url, filename=filename)
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
