import os
import subprocess
import zipfile
from typing import Optional

from natsort import natsorted
from send2trash import send2trash

import config


def delete_non_image_files(item_path: str) -> None:
    """Delete all non-image files in the given directory recursively."""
    for root, _, files in os.walk(item_path):
        for file in files:
            if not any(file.endswith(ext) for ext in config.IMAGE_EXTENSIONS):
                os.remove(os.path.join(root, file))


def rename_files_with_zero_padding(item_path: str) -> None:
    """Rename image files in the directory with zero-padded numbers."""
    image_files = [
        file
        for file in os.listdir(item_path)
        if any(file.endswith(ext) for ext in config.IMAGE_EXTENSIONS)
    ]
    num_files = len(image_files)
    padding = len(str(num_files))
    for index, file in enumerate(natsorted(image_files), start=1):
        ext = os.path.splitext(file)[1]
        new_name = f"{str(index).zfill(padding)}{ext}"
        os.rename(os.path.join(item_path, file), os.path.join(item_path, new_name))


def run_pingo(item_path: str, preset_name: str, presets: dict) -> Optional[str]:
    """Run pingo on the directory and return its output, using the selected preset from the given presets dict."""
    cmd = presets.get(preset_name, [])
    if not cmd:
        raise ValueError(f"Preset '{preset_name}' not found in user settings")
    cmd = cmd + [item_path]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout + ("\n" + result.stderr if result.stderr else "")


def remove_redundant_images(item_path: str) -> None:
    """Remove any image file (except .webp) if a .webp with the same name exists."""
    for root, _, files in os.walk(item_path):
        webp_files = {
            os.path.splitext(file)[0] for file in files if file.endswith(".webp")
        }
        for file in files:
            name, ext = os.path.splitext(file)
            if (
                ext.lower() in config.IMAGE_EXTENSIONS
                and ext.lower() != ".webp"
                and name in webp_files
            ):
                os.remove(os.path.join(root, file))


def compress_to_cbz(item_path: str, zip_file_path: str) -> None:
    """Compress the directory into a cbz file."""
    with zipfile.ZipFile(zip_file_path, "w", zipfile.ZIP_STORED) as zipf:
        for root, _, files in os.walk(item_path):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, start=item_path)
                zipf.write(file_path, arcname)


def safe_remove_folder(item_path: str) -> None:
    """Try to send folder to trash, else remove it."""
    import shutil

    try:
        send2trash(item_path)
    except Exception:
        try:
            os.rmdir(item_path)
        except OSError:
            shutil.rmtree(item_path, ignore_errors=True)


def process_single_folder(
        item_path: str, zip_file_path: str, preset_name: str, skip_pingo: bool, presets: dict
) -> Optional[str]:
    """Process a single folder and return pingo output if run."""
    delete_non_image_files(item_path)
    rename_files_with_zero_padding(item_path)
    pingo_output = None
    if not skip_pingo:
        pingo_output = run_pingo(item_path, preset_name, presets)
    remove_redundant_images(item_path)
    compress_to_cbz(item_path, zip_file_path)
    safe_remove_folder(item_path)
    return pingo_output
