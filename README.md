# Comic Optimizer

Comic Optimizer is a modern, user-friendly tool for optimizing comic book archives (CBZ) by compressing images and optionally running the pingo optimizer. It features a graphical interface built with ttkbootstrap for easy batch processing of comic folders.

## Features

- Batch optimize comic folders into CBZ/CBR/ZIP files
- Select from multiple pingo presets (customizable in `presets.json`)
- See the exact pingo command that will be run for each preset
- Option to skip pingo optimization
- Modern, easy-to-use GUI
- User settings for theme, font, and more, saved per user in a cross-platform config directory

## Requirements

- **[pingo](https://css-ig.net/pingo)** v1.24.2+ (must be installed and available in your system PATH)
- **Python** 3.13+ (if running from source)
- **[uv](https://docs.astral.sh/uv/)** (if running from source; for dependency management)

## Installation

### Download the Standalone Release (Recommended)

- Go to the [GitHub Releases](https://github.com/phnthnhnm/comic-optimizer/releases) page.
- Download the latest `comic-optimizer-<version>.zip` file for Windows.
- Extract the zip file. Inside, you will find a `comic-optimizer` folder.
- Open the `comic-optimizer` folder and double-click `comic-optimizer.exe` to launch the GUI.

### Build the Standalone Release Yourself

If you want to build the Windows release yourself, simply run:

```bat
build.bat
```

This will use `uv` and [Nuitka](https://nuitka.net/) to create a standalone folder in the `dist` directory. The output
will be a `comic-optimizer` folder containing `comic-optimizer.exe` and all required files. The build script will also
zip this folder for distribution.

### Run from Source

1. **Clone the repository:**
   ```sh
   git clone https://github.com/phnthnhnm/comic-optimizer.git
   cd comic-optimizer
   ```
2. **Install dependencies using uv:**
   ```sh
   uv pip install -r pyproject.toml
   ```
3. **Ensure pingo is installed and available in your PATH.**
4. **Run the GUI:**
   ```sh
   uv run src/main.py
   ```

## How to Use

1. Launch the application (either from the extracted release folder or from source).
2. Click "Browse" to select the root directory containing your comic folders.
3. Choose a pingo preset from the dropdown (presets are defined in `presets.json`).
   - The exact command for the selected preset is shown above the dropdown.
   - (Optional) Check "Skip pingo" to skip pingo optimization.
4. Click "Start" to begin processing. A report will be shown when done.
5. To change the theme, font, or other preferences, click the "Settings" menu in the menu bar.

## User Settings Location

User-specific settings (theme, font, etc.) are saved in a TOML file in a user-writable config directory:

- **Windows:** `%APPDATA%/comic-optimizer/user_settings.toml`
- **macOS:** `~/Library/Application Support/comic-optimizer/user_settings.toml`
- **Linux:** `~/.config/comic-optimizer/user_settings.toml`

This file is created automatically on first run. You can delete it to reset your preferences.

## Troubleshooting

- **Settings dialog does not open in the release:**
    - Make sure you are using the latest release zip and have extracted all files before running the exe.
    - If you see an error about missing modules, ensure you are running `comic-optimizer.exe` from inside the extracted
      `comic-optimizer` folder.
- **Settings are not saved or loaded:**
    - Check that your user config directory is writable.
    - Delete the `user_settings.toml` file to reset preferences if needed.
- **General issues:**
    - Run the exe from a terminal (e.g., `cmd.exe`) to see error messages.

## License

See [LICENSE](LICENSE) for details.
