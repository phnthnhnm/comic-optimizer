# Comic Optimizer

Comic Optimizer is a modern, user-friendly tool for optimizing comic book archives (CBZ) by compressing images and optionally running the pingo optimizer. It features a graphical interface built with ttkbootstrap for easy batch processing of comic folders.

## Features

- Batch optimize comic folders into CBZ files
- Optional lossy compression
- Option to skip pingo optimization
- Modern, easy-to-use GUI

## Requirements

- **[pingo](https://css-ig.net/pingo)** v1.24.2+ (must be installed and available in your system PATH)
- **Python** 3.13+ (if running from source)
- **[uv](https://docs.astral.sh/uv/)** (if running from source; for dependency management)

## Installation

### Download the Standalone Executable

- Go to the [GitHub Releases](https://github.com/phnthnhnm/comic-optimizer/releases) page.
- Download the latest `comic-optimizer.exe` file for Windows.
- Double-click the executable to launch the GUI.

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
   uv run main.py
   ```

## How to Use

1. Launch the application (either the EXE or from source).
2. Click "Browse" to select the root directory containing your comic folders.
3. (Optional) Check "Lossy" for lossy compression, or "Skip pingo" to skip pingo optimization.
4. Click "Start" to begin processing. A report will be shown when done.
