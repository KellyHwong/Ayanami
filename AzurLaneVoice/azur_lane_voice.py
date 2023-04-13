#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : Dec-14-20 21:44
# @Author  : Kelly Hwong (dianhuangkan@gmail.com)

import os
import csv
import re
import requests
import yaml
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

        # Web configs
        self.headers = {
            "DNT": "1",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36"
        }

        MOEGIRL_BASE_URL = "https://zh.moegirl.org.cn/zh-cn/"
        self.moegirl_page_url = "".join(
            [MOEGIRL_BASE_URL, quote("碧蓝航线"), ":", quote(self.chinese_name)])

        self.wikiru_page_url = None
        if self.japanese_name is not None:
            WIKIRU_BASE_URL = "https://azurlane.wikiru.jp/index.php"
            self.wikiru_page_url = "".join(
                [WIKIRU_BASE_URL, "?", quote(self.japanese_name, encoding="EUC-JP")])

        self.moegirl_page_html = None  # character page
        self.voice_metas = []

        self.page_html_jp = None  # character page jp

        self.folder = os.path.join("characters", f"{self.name}"+"-Voice-Text")
        os.makedirs(self.folder, exist_ok=True)

        # Download config
        self.num_download_processes = 4

    def _get_page_html(self, url, page_name, verbose=0, debug=False):
        """Get Page HTML"""
        if url is None:
            raise ValueError(
                f"url: {url} is None. Maybe self.japanese_name is not set!")
        if verbose:
            print(f"Get HTML from URL: {url}")
        page_html = requests.get(url, headers=self.headers).content
        page_html = page_html.decode("utf-8")

        if debug:
            with open(f"./debug_{page_name}.html", "w", encoding="utf-8") as f:
                f.write(page_html)

        return page_html

    # Moegirl wiki
    def _get_voice_metas_cn(self, verbose=0, debug=False):
        """从 Moegirl 上获取中文台本，以及台词url"""
        if self.moegirl_page_html is None:
            self.moegirl_page_html = self._get_page_html(
                self.moegirl_page_url, page_name="moegirl", verbose=verbose, debug=debug)

        soup = BeautifulSoup(self.moegirl_page_html, "lxml")
        wikitables = soup.find_all("table", {"class": "wikitable"})

        wikitables_with_voice = []
        for table in wikitables:
            tds = table.find("tr").find_all("td")
            if len(tds) == 3 and tds[-1].find("div", {"data-bind": re.compile(r".*")}):
                wikitables_with_voice.append(table)

        current_prefix = ""
        for table in wikitables_with_voice:
            tag = table.previous_sibling.previous_sibling
            if tag and tag.name in ["h2", "h3"]:
                pass
            else:  # tag.name == 'p'
                tag = tag.previous_sibling.previous_sibling

            span = tag.find("span", {"class": "mw-headline"})
            current_prefix = span.string
            if verbose:
                print(f"current_prefix: {current_prefix}")

            all_tr = table.find_all("tr")

            scenario, dialogue = "", ""
            for tr in all_tr:
                tds = tr.find_all("td")
                if len(tds) == 3:
                    scenario = tds[0].string
                if verbose:
                    print(f"scenario: {scenario}")
                dialogue = tds[-2].string
                div_data = tds[-1].find("div",
                                        {"data-bind": re.compile(r".*")})
                if verbose:
                    print(f"dialogue: {dialogue}")
                if div_data:  # If here is a voice play button
                    data_bind = div_data["data-bind"]
                    voice_meta = json.loads(data_bind)
                    playlist = voice_meta["component"]["params"]["playlist"]
                    assert len(playlist) == 1
                    url = playlist[0]["audioFileUrl"]
                    filename = os.path.basename((unquote(urlparse(url).path)))
                    if verbose:
                        print(f"filename: {filename}")
                    self.voice_metas.append(
                        [current_prefix, scenario, dialogue, filename, url])

        csv_file = os.path.join(self.folder, "metadata_cn.csv")
        with open(csv_file, 'w', newline="", encoding="utf-8") as f:
            writer = csv.writer(f, delimiter="|")
            writer.writerow(
                ["prefix",  "scenario", "dialogue", "filename", "url"])
            writer.writerows(self.voice_metas)
            print(f"Voice metas stored to CSV file: {csv_file}.")

    # Azurlane Wikiru
    def _get_voice_metas_jp(self, verbose=0, debug=False):
        """从 wikiru 上获取日语台本"""
        if self.page_html_jp is None:
            self.page_html_jp = self._get_page_html(
                self.wikiru_page_url, page_name="wikiru", verbose=verbose, debug=debug)
        soup = BeautifulSoup(self.page_html_jp, "lxml")

        all_headers = soup.find_all(re.compile('^h[1-6]$'))
        voice_headers = []
        for header in all_headers:
            # for tag in all_h:
            if "ボイス" in header.text:
                voice_headers.append(header)

        count_total = 0
        csv_rows = []

        _div_containers = voice_headers[0].find_next_siblings(
            "div", {"class": "rgn-container"})
        div_containers = []
        for container in _div_containers:
            div_description = container.find(
                "div", {"class": "rgn-description"})
            if div_description and div_description.find("p"):  # 可展开表格的标题
                div_containers.append(container)  # prefix候选词
                print(div_description.p.text)

        for container in div_containers:
            prefix = container.find(
                "div", {"class": "rgn-description"}).find("p").text
            if "クリック" in prefix:
                prefix = container.find_previous_sibling(
                    re.compile('^h[3-4]$')).text.replace('†', '').strip()
            if verbose:
                print(f"栏目名称 prefix: {prefix}")
            div_content = container.find(
                "div", {"class": "rgn-content"})
            all_tr = div_content.find_all("tr")
            count = 0
            for tr in all_tr:
                th, td = tr.find("th"), tr.find("td")
                if th and td:
                    scenario, dialogue = th.text, td.text
                    if scenario == "" or dialogue == "":
                        continue
                    row = [prefix, scenario, dialogue]
                    csv_rows.append(row)
                    print("|".join(row))
                    count += 1
            if verbose:
                print(f"本场景台词数: {count}")
            count_total += count

        if verbose:
            print(f"台词总数: {count_total}")

        csv_file = os.path.join(self.folder, "metadata_jp.csv")
        with open(csv_file, 'w', newline="", encoding="utf-8") as f:
            writer = csv.writer(f, delimiter="|")
            writer.writerow(["prefix", "scenario", "dialogue"])
            writer.writerows(csv_rows)
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

        data = requests.get(url, headers=headers).content
        with open(filepath, "wb") as f:
            f.write(data)
        print(f"Downloaded to {filepath}.")

    def _download_voices(self):
        print(
            f"{self.__class__} has {len(self.voice_metas)} voices. Now downloading...")
        for voice_meta in self.voice_metas:
            # voice_meta header:
            # prefix|scenario|dialogue|filename|url
            filename, url = voice_meta[3], voice_meta[4]
            self._download(url, headers=self.headers, folder=os.path.join(
                self.folder, "mp3"), filename=filename)
        print("Download complete!")

    # Data procedures

    def get_voice_metas(self, langs=None, verbose=0, debug=False):
        """langs: None or List, options can be cn or jp."""
        if langs is None:  # Get both
            self._get_voice_metas_cn(verbose=verbose, debug=debug)
            self._get_voice_metas_jp(verbose=verbose, debug=debug)
        else:
            if "cn" in langs:
                self._get_voice_metas_cn(verbose=verbose, debug=debug)
            if "jp" in langs:
                self._get_voice_metas_jp(verbose=verbose, debug=debug)

    def download_voices(self):
        self._get_voice_metas_cn()
        self._download_voices()


def AzurLaneVoice_test():
    yaml_file = os.path.join("azur_lane_characters.yml")
    with open(yaml_file, 'r', encoding="utf-8") as f:
        data = yaml.safe_load(f)
    characters = data["characters"]

    def get_voice_metas_test():
        # for character in characters:
        character = characters[0]
        character = AzurLaneVoice(**character)
        character.get_voice_metas(langs=["cn", "jp"], verbose=1, debug=True)
        print(f"""Character {character.name} tested successfully!""")
        character.download_voices()
        print(f"Downloading successfully!")

    get_voice_metas_test()


def main():
    AzurLaneVoice_test()
    # AzurLaneVoiceJP_test()


if __name__ == "__main__":
    main()
