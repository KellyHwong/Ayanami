#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : Dec-18-20 21:43
# @Author  : Kelly Hwong (dianhuangkan@gmail.com)
# @Link    : http://example.org

import os
import csv
import json


def cache_scenario2filename(query_character):
    """
    # Arguments:
        query_character: for example, "Z23".
    """

    csv_path = os.path.join("mp3", query_character, "audio_files.csv")
    with open(csv_path, "r") as csvfile:
        d = {}  # scenario -> filename dict
        csv_reader = csv.reader(csvfile)
        for i, row in enumerate(csv_reader):
            filename, scenario = row[0], row[1]
            # will only append the first scenario if there are multi scenario with the same names.
            if not d.get(scenario):
                d[scenario] = filename

    with open(os.path.join("database", f"{query_character}.cache.json"), "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False)

    scenario2filename = d
    return scenario2filename


def get_scenario2filename(query_character):
    """
    # Arguments:
        query_character: for example, "Z23".
        query_scenario: for example, "好感度-爱".
    """
    cache_file = os.path.join("database", f"{query_character}.cache.json")
    if not os.path.isfile(cache_file):
        scenario2filename = cache_scenario2filename(query_character)
    else:
        with open(cache_file, "r", encoding="utf-8") as f:
            scenario2filename = json.loads("\n".join(f.readlines()))

    return scenario2filename
