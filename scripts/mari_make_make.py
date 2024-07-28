from pathlib import Path
from _hacks import *


def newdir(path):
    return "newdir %s\n" % path


def make(path, dest, size):
    return "make {path} {dest} {size}\n" \
        .format(path=path, dest=dest, size=size)


with open("mari/make.mari", "w") as fd:
    fd.flush()

    fd.write(newdir("/home"))
    fd.write(newdir("/home/guest"))
    fd.write(newdir("/home/guest/Build"))
    fd.write(newdir("/home/guest/Build/Marinette"))
    fd.write(newdir("/home/guest/Build/Marinette/bin"))
    fd.write(newdir("/home/guest/Build/Marinette/marinette"))
    fd.write(newdir("/home/guest/Build/Marinette/marinette/mainframe"))
    fd.write(newdir("/home/guest/Build/Marinette/marinette/mainframe/patches"))

    fd.write(make("/home/guest/Sources/Marinette/src/marinette.src", "/home/guest/Build/Marinette/bin", 150000))
    for patch in Path("patches").iterdir():
        fd.write(make("/home/guest/Sources/Marinette/patches/%s" % patch.name, "/home/guest/Build/Marinette/marinette/mainframe/patches", 150000))
