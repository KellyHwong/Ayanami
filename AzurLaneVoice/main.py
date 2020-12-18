#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : Dec-18-20 21:43
# @Author  : Kelly Hwong (dianhuangkan@gmail.com)
# @Link    : http://example.org

import os
import csv


def main():
    query_key = "好感度-爱"

    csv_path = os.path.join("mp3", "Z23", "audio_files.csv")
    with open(csv_path, "r") as csvfile:
        csv_reader = csv.reader(csvfile)
        for i, row in enumerate(csv_reader):
            if row[1] == query_key:
                print(f"line {i}: {row}")
                mp3_file = os.path.join("mp3", "Z23", row[0])
                os.system(mp3_file)


if __name__ == "__main__":
    main()
