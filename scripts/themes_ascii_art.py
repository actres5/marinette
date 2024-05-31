#!/usr/bin/env python3


from _hacks import *


with open("etc/ascii_art.txt", "r") as logo:
    print('"asciiArt": [')
    lines = logo.readlines()
    lines = map(lambda line: line.replace("\n", ""), lines)
    for line in lines:
        print(" " * 4 + '"' + line + '",')
    print("],")
