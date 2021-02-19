#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : Dec-19-20 15:43
# @Author  : Kelly Hwong (dianhuangkan@gmail.com)

import os
from scenario2filename import get_scenario2filename


def main():
    query_character = "Z23"
    query_scenario = "好感度-爱"

    scenario2filename = get_scenario2filename(query_character)

    if scenario2filename.get(query_scenario):
        print(f"query_scenario: {query_scenario}.")
        mp3_file = os.path.join(
            "mp3", "Z23", scenario2filename[query_scenario])
        os.system(mp3_file)


if __name__ == "__main__":
    main()
