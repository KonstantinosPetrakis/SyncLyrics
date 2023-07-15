from platform import system
from shutil import rmtree as rmdir
from os import system as s, remove as rm, path
from sys import argv


if __name__ == "__main__":
    main_name = "sync_lyrics.py"

    if "clean" in argv:
        if path.exists(f"{main_name}.bin"): rm(f"{main_name}.bin")
        if path.exists(f"{main_name}.exe"): rm(f"{main_name}.exe")
        if path.exists(f"{main_name}.build"): rmdir(f"{main_name}.build")
        if path.exists(f"{main_name}.dist"): rmdir(f"{main_name}.dist")
        if path.exists(f"{main_name}.onefile-build"): rmdir(f"{main_name}.onefile-build")
    else:
        extra_args = ""
        if system() == "Linux":
            extra_args = "--include-package=vext" # This is required for the tray icon to work on Linux

        s(f"python -m nuitka --onefile --standalone --follow-imports " \
            f"--include-package=desktop_notifier {extra_args} {main_name}")
    