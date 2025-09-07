@echo off
REM Update version.py with the latest git tag
git describe --tags --abbrev=0 > tmp_version.txt
set /p VERSION=<tmp_version.txt
(echo __version__ = "%VERSION%") > version.py
del tmp_version.txt

uv run pyinstaller --onefile --noconsole --name comic-optimizer main.py --add-data "presets.json;."
PAUSE
