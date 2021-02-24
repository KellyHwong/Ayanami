#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : Feb-22-21 02:01
# @Author  : Kelly Hwong (dianhuangkan@gmail.com)

import re
from bs4 import BeautifulSoup


def main():
    with open("debug_綾波.html", "rb") as f:
        content = f.read()
    text = content.decode('utf-8')
    soup = BeautifulSoup(text, "lxml")

    all_h3 = soup.find_all("h3")
    all_h2 = soup.find_all("h2")

    voice_tags = []
    for e in all_h3:
        if "ボイス" in e.text:
            voice_tags.append(e)
    for e in all_h2:
        if "ボイス" in e.text:
            voice_tags.append(e)

    for voice_tag in voice_tags:
        _text = voice_tag.next_sibling
        table_tag = _text.next_sibling
        div_tag = table_tag.find("div", {"class", "ie5"})

        all_tr = div_tag.find_all("tr")
        count = 0
        for tr in all_tr:
            th = tr.find("th")
            td = tr.find("td")
            if th and td:
                count += 1
                scenario, dialogue = th.text, td.text
                print("|".join([scenario, dialogue]))
        print(count)


if __name__ == "__main__":
    main()
