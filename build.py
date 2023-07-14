from platform import system
from shutil import rmtree as rmdir
from os import system as s, remove as rm, path
from sys import argv


if __name__ == '__main__':
    if "clean" in argv:
        if path.exists("__main__.bin"): rm("__main__.bin")
        if path.exists("__main__.exe"): rm("__main__.exe")
        if path.exists("__main__.build"): rmdir("__main__.build")
        if path.exists("__main__.dist"): rmdir("__main__.dist")
        if path.exists("__main__.onefile-build"): rmdir("__main__.onefile-build")
    else:
        extra_args = ""
        if system() == "Linux":
            extra_args = "--include-package=vext" # This is required for the tray icon to work on Linux

        s(f"python -m nuitka --onefile --standalone --follow-imports " \
            f"--include-package=desktop_notifier {extra_args} __main__.py")
    