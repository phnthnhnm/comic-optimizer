@echo off

REM --------------------------------------------------------------------------
REM Get the latest tag from the entire repository and strip the "v".
REM --------------------------------------------------------------------------
for /f "delims=v" %%i in ('git tag --sort=-version:refname 2^>nul') do set "GIT_TAG=%%i" & goto :foundTag

:foundTag

if "%GIT_TAG%"=="" (
    echo No Git tag found. Using default version.
    set "FINAL_NAME=comic-optimizer-dev"
    set "VERSION_STRING=dev"
) else (
    echo Found Git tag: v%GIT_TAG%
    set "FINAL_NAME=comic-optimizer-%GIT_TAG%"
    set "VERSION_STRING=%GIT_TAG%"
)

REM --------------------------------------------------------------------------
REM Update the src/version.py file with the latest version
REM --------------------------------------------------------------------------
(echo __version__ = "%VERSION_STRING%") > src/version.py

REM --------------------------------------------------------------------------
REM Delete the existing spec file to force a new one to be generated.
REM --------------------------------------------------------------------------
if exist comic-optimizer.spec (
    echo Deleting old comic-optimizer.spec...
    del /q /f comic-optimizer.spec
)

REM --------------------------------------------------------------------------
REM Run PyInstaller, setting a static name to keep the .spec file name consistent.
REM --------------------------------------------------------------------------
uv run pyinstaller --onefile --noconsole --name comic-optimizer src/main.py --add-data "src/presets.json;."

REM --------------------------------------------------------------------------
REM Rename the output executable to include the version tag.
REM --------------------------------------------------------------------------
echo Renaming executable...
rename "dist\comic-optimizer.exe" "%FINAL_NAME%.exe"

PAUSE