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
from urllib.parse import urlparse, quote, unquote


class AzurLaneVoice(object):
    """Azur Lane character voices downloader from moegirl wiki.
    """

    def __init__(self, name, chinese_name, japanese_name=None):
        self.name = name  # To store archives
        self.chinese_name = chinese_name  # To seek url
        self.japanese_name = japanese_name  # To seek japanese url

        self.headers = {
            "DNT": "1",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36"
        }

        BASE_URL = "https://zh.moegirl.org.cn/zh-cn/"
        self.page_url = "".join(
            [BASE_URL, quote("碧蓝航线"), ":", quote(self.chinese_name)])

        self.page_url_jp = None
        if self.japanese_name is not None:
            BASE_URL_JP = "https://azurlane.wikiru.jp/index.php"
            self.page_url_jp = "".join(
                [BASE_URL_JP, "?", quote(self.japanese_name, encoding="EUC-JP")])

        # Web configs
        self.num_download_processes = 4

        self.page_html = None  # character page
        self.voice_tables = None
        self.voice_metas = []

        self.page_html_jp = None  # character page jp
        self.voice_tables_jp = None

        self.folder = os.path.join("characters", f"{self.name}"+"-Voice")
        os.makedirs(self.folder, exist_ok=True)

    def _get_page_html(self, debug=False):
        page_html = requests.get(self.page_url, headers=self.headers).content
        page_html = page_html.decode("utf-8")
        self.page_html = page_html

        if debug:
            with open(f"./debug_{self.name}.html", "w", encoding="utf-8") as f:
                f.write(self.page_html)

    def _get_page_html_jp(self, debug=False):
        if self.page_url_jp is None:
            raise ValueError(
                "self.page_url_jp is None. Maybe self.japanese_name is not set!")
        else:
            response_jp = requests.get(
                self.page_url_jp, headers=self.headers)
            # page_html_jp = response_jp.context.decode("EUC-JP")
            self.page_html_jp = response_jp.text  # directly use the response's text

            if debug:
                with open(f"./debug_{self.japanese_name}.html", "w", encoding="utf-8") as f:
                    f.write(self.page_html_jp)

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

            scenario, dialogue = "", ""
            for tr in trs:
                tds = tr.find_all("td")

                if len(tds) == 3:
                    scenario = tds[0].text

                dialogue = tds[-2].text
                div_data = tds[-1].find("div",
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
                    # print(filename, scenario, dialogue, url)
                    # input(123)

        csv_file = os.path.join(self.folder, "metadata.csv")
        with open(csv_file, 'w', newline="", encoding="utf-8") as f:
            writer = csv.writer(f, delimiter="|")
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
            os.makedirs(folder, exist_ok=True)
        filepath = os.path.join(folder, filename)

        data = requests.get(url).content
        with open(filepath, "wb") as f:
            f.write(data)
        print(f"Downloaded to {filepath}.")

    def _download_voices(self):
        print(
            f"{self.__class__} has {len(self.voice_metas)} voices. Now downloading...")
        for voice_meta in self.voice_metas:
            filename, url = voice_meta[0], voice_meta[3]
            self._download(url, folder=os.path.join(
                self.folder, "mp3"), filename=filename)
        print("Download complete!")

    # Data procedures
    def get_voice_metas(self):
        self._get_page_html()
        # self.debug_store_page_html()
        self._get_voice_tables()
        self._get_voice_metas()

    def download_voices(self):
        self._get_page_html()
        # self.debug_store_page_html()
        self._get_voice_tables()
        self._get_voice_metas()
        self._download_voices()


def AzurLaneVoice_test():
    from character_names import characters

    def get_voice_metas_test():
        for character in characters:
            character = AzurLaneVoice(**character)
            character.get_voice_metas()

    get_voice_metas_test()
    print("All characters in 'character_names.py' tested successfully!")


def AzurLaneVoiceJP_test():
    from character_names import characters
    character = characters[0]  # Ayanami
    character = AzurLaneVoice(**character)

    character._get_page_html_jp(debug=True)


def main():
    # AzurLaneVoice_test()
    AzurLaneVoiceJP_test()


if __name__ == "__main__":
    main()
