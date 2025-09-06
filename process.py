import os
import zipfile
import subprocess
from send2trash import send2trash
from natsort import natsorted

def delete_non_image_files(item_path):
    image_extensions = {'.png', '.jpg', '.jpeg', '.webp', '.avif', '.gif'}
    for root, _, files in os.walk(item_path):
        for file in files:
            if not any(file.endswith(ext) for ext in image_extensions):
                os.remove(os.path.join(root, file))

def rename_files_with_zero_padding(item_path):
    image_extensions = {'.png', '.jpg', '.jpeg', '.webp', '.avif', '.gif'}
    image_files = [file for file in os.listdir(item_path) if any(file.endswith(ext) for ext in image_extensions)]
    num_files = len(image_files)
    padding = len(str(num_files))
    
    for index, file in enumerate(natsorted(image_files), start=1):
        ext = os.path.splitext(file)[1]
        new_name = f"{str(index).zfill(padding)}{ext}"
        os.rename(os.path.join(item_path, file), os.path.join(item_path, new_name))

def process_and_compress_folder(item_path, zip_file_path, skip_pingo):
    delete_non_image_files(item_path)
    
    rename_files_with_zero_padding(item_path)
    
    if not skip_pingo:
        subprocess.run(['pingo', '-s4', '-lossless', '-webp', '-process=4', '-no-jpeg', item_path])
    
    # Delete .png files that have a matching .webp file
    for root, _, files in os.walk(item_path):
        webp_files = {os.path.splitext(file)[0] for file in files if file.endswith('.webp')}
        for file in files:
            if file.endswith('.png') and os.path.splitext(file)[0] in webp_files:
                os.remove(os.path.join(root, file))
    
    # Compress the folder to a cbz file
    with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_STORED) as zipf:
        for root, _, files in os.walk(item_path):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, start=item_path)
                zipf.write(file_path, arcname)
    
    send2trash(item_path)

def process_folders(root_dir, skip_pingo):
    for item in os.listdir(root_dir):
        item_path = os.path.join(root_dir, item)
        if os.path.isdir(item_path):
            subfolders = [os.path.join(item_path, subfolder) for subfolder in os.listdir(item_path) if os.path.isdir(os.path.join(item_path, subfolder))]
            if subfolders:
                for subfolder in subfolders:
                    zip_file_path = os.path.join(item_path, f"{os.path.basename(subfolder)}.cbz")
                    process_and_compress_folder(subfolder, zip_file_path, skip_pingo)
            else:
                zip_file_path = os.path.join(root_dir, f"{item}.cbz")
                process_and_compress_folder(item_path, zip_file_path, skip_pingo)

if __name__ == "__main__":
    import sys
    script_root_dir = os.path.dirname(os.path.abspath(__file__))
    skip_pingo = '-no-pingo' in sys.argv
    
    if '-p' in sys.argv:
        p_index = sys.argv.index('-p')
        if p_index + 1 < len(sys.argv):
            root_dir = sys.argv[p_index + 1]
        else:
            print("Error: No folder path provided after -p")
            sys.exit(1)
    else:
        root_dir = script_root_dir
    
    process_folders(root_dir, skip_pingo)
