# Why this exists? Well...
# It turns out files on Windows and on Linux are encoded a bit different
# So when I switched to Windows I couldn't use any of the scripts located here
# This is an ugly hack to actually run the project on Windows machines

# Why not just change every script like any good girl would do?
# Well, because I'm too lazy for that :P Here's a hack instead, enjoy~


import platform
import pathlib


if platform.system() == "Windows":
    # Hack no. 1: Windows does not open files with utf-8 by default(Not to mention LF/CRLF magic!)
    _PYTHON_OPEN = open
    def open(*args, **kwargs):
        # Yes, it is literally THAT stupid
        kwargs["encoding"] = "utf-8"
        return _PYTHON_OPEN(*args, **kwargs)

    # Hack no. 2: By default Windows uses PureWindowsPath, which breaks Marinette installer generation script
    PurePath = pathlib.PurePosixPath

    # Hack no. 3: To be made :D
