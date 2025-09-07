@echo off
REM Update version.py with the latest git tag
git describe --tags --abbrev=0 > tmp_version.txt
set /p VERSION=<tmp_version.txt
(echo __version__ = "%VERSION%") > src/version.py
del tmp_version.txt

uv run pyinstaller --onefile --noconsole --name comic-optimizer src/main.py --add-data "src/presets.json;."
PAUSE
