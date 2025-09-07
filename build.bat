@echo off
uv run pyinstaller --onefile --noconsole --name comic-optimizer main.py --add-data "presets.json;."
PAUSE
