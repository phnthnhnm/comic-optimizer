@echo off

REM --------------------------------------------------------------------------
REM Get the latest tag from the entire repository and strip the "v".
REM --------------------------------------------------------------------------
for /f "delims=v" %%i in ('git tag --sort=-version:refname 2^>nul') do set "GIT_TAG=%%i" & goto :foundTag

:foundTag

if "%GIT_TAG%"=="" (
    echo No Git tag found. Using default version.
    set "VERSION_STRING=dev"
) else (
    echo Found Git tag: v%GIT_TAG%
    set "VERSION_STRING=%GIT_TAG%"
)

REM --------------------------------------------------------------------------
REM Update the src/version.py file with the latest version
REM --------------------------------------------------------------------------
(echo __version__ = "%VERSION_STRING%") > src/version.py

REM --------------------------------------------------------------------------
REM Run Nuitka
REM --------------------------------------------------------------------------
uv run nuitka --standalone --msvc=latest --product-name=comic-optimizer --product-version=%VERSION_STRING% --copyright="© 2025 Nam Phan" --enable-plugin=tk-inter --enable-plugin=upx --windows-console-mode=disable --windows-icon-from-ico=python.ico --output-dir=dist --remove-output --output-filename=comic-optimizer.exe src/main.py

REM Rename main.dist to comic-optimizer
ren dist\main.dist comic-optimizer

REM Zip the folder
pushd dist
7z a comic-optimizer-%VERSION_STRING%.zip comic-optimizer
popd
PAUSE