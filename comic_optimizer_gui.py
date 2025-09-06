import os
import zipfile
import subprocess
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
from send2trash import send2trash
from natsort import natsorted


class ComicOptimizerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Comic Optimizer")
        self.root.geometry("500x300")

        self.dir_path = tk.StringVar()
        self.lossy = tk.BooleanVar(value=False)
        self.skip_pingo = tk.BooleanVar(value=False)
        self.status = tk.StringVar(value="Idle.")

        self.create_widgets()

    def create_widgets(self):
        tk.Label(self.root, text="Select Root Directory:").pack(pady=5)
        frame = tk.Frame(self.root)
        frame.pack(pady=5)
        tk.Entry(frame, textvariable=self.dir_path, width=40).pack(side=tk.LEFT)
        tk.Button(frame, text="Browse", command=self.browse_dir).pack(
            side=tk.LEFT, padx=5
        )

        tk.Checkbutton(
            self.root, text="Lossy (process-lossy)", variable=self.lossy
        ).pack(anchor=tk.W, padx=20)
        tk.Checkbutton(self.root, text="Skip pingo", variable=self.skip_pingo).pack(
            anchor=tk.W, padx=20
        )

        tk.Button(self.root, text="Start", command=self.start_processing).pack(pady=10)
        tk.Label(self.root, textvariable=self.status, fg="blue").pack(pady=10)

    def browse_dir(self):
        path = filedialog.askdirectory()
        if path:
            self.dir_path.set(path)

    def start_processing(self):
        if not self.dir_path.get():
            messagebox.showerror("Error", "Please select a directory.")
            return
        self.status.set("Processing...")
        threading.Thread(target=self.process_folders, daemon=True).start()

    def delete_non_image_files(self, item_path):
        image_extensions = {".png", ".jpg", ".jpeg", ".webp", ".avif", ".gif"}
        for root, _, files in os.walk(item_path):
            for file in files:
                if not any(file.endswith(ext) for ext in image_extensions):
                    os.remove(os.path.join(root, file))

    def rename_files_with_zero_padding(self, item_path):
        image_extensions = {".png", ".jpg", ".jpeg", ".webp", ".avif", ".gif"}
        image_files = [
            file
            for file in os.listdir(item_path)
            if any(file.endswith(ext) for ext in image_extensions)
        ]
        num_files = len(image_files)
        padding = len(str(num_files))
        for index, file in enumerate(natsorted(image_files), start=1):
            ext = os.path.splitext(file)[1]
            new_name = f"{str(index).zfill(padding)}{ext}"
            os.rename(os.path.join(item_path, file), os.path.join(item_path, new_name))

    def process_and_compress_folder(self, item_path, zip_file_path):
        self.delete_non_image_files(item_path)
        self.rename_files_with_zero_padding(item_path)
        pingo_output = None
        if not self.skip_pingo.get():
            if self.lossy.get():
                result = subprocess.run(
                    ["pingo", "-s4", "-webp", "-process=4", item_path],
                    capture_output=True,
                    text=True,
                )
            else:
                result = subprocess.run(
                    [
                        "pingo",
                        "-s4",
                        "-lossless",
                        "-webp",
                        "-process=4",
                        "-no-jpeg",
                        item_path,
                    ],
                    capture_output=True,
                    text=True,
                )
            pingo_output = result.stdout + (
                "\n" + result.stderr if result.stderr else ""
            )

        # Remove any image file (except .webp) if a .webp with the same name exists
        image_extensions = {".png", ".jpg", ".jpeg", ".avif", ".gif"}
        for root, _, files in os.walk(item_path):
            webp_files = {
                os.path.splitext(file)[0] for file in files if file.endswith(".webp")
            }
            for file in files:
                name, ext = os.path.splitext(file)
                if ext.lower() in image_extensions and name in webp_files:
                    os.remove(os.path.join(root, file))
        # Compress to cbz
        with zipfile.ZipFile(zip_file_path, "w", zipfile.ZIP_STORED) as zipf:
            for root, _, files in os.walk(item_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, start=item_path)
                    zipf.write(file_path, arcname)
        import shutil

        try:
            send2trash(item_path)
        except Exception:
            # Fallback: try to remove empty dir, else remove recursively
            try:
                os.rmdir(item_path)
            except Exception:
                shutil.rmtree(item_path, ignore_errors=True)

    def process_folders(self):
        root_dir = self.dir_path.get()
        pingo_outputs = []
        try:
            for item in os.listdir(root_dir):
                item_path = os.path.join(root_dir, item)
                if os.path.isdir(item_path):
                    subfolders = [
                        os.path.join(item_path, subfolder)
                        for subfolder in os.listdir(item_path)
                        if os.path.isdir(os.path.join(item_path, subfolder))
                    ]
                    if subfolders:
                        for subfolder in subfolders:
                            zip_file_path = os.path.join(
                                item_path, f"{os.path.basename(subfolder)}.cbz"
                            )
                            self.status.set(
                                f"Processing\n{os.path.basename(subfolder)}"
                            )
                            self.delete_non_image_files(subfolder)
                            self.rename_files_with_zero_padding(subfolder)
                            pingo_output = None
                            if not self.skip_pingo.get():
                                if self.lossy.get():
                                    result = subprocess.run(
                                        [
                                            "pingo",
                                            "-s4",
                                            "-webp",
                                            "-process=4",
                                            subfolder,
                                        ],
                                        capture_output=True,
                                        text=True,
                                    )
                                else:
                                    result = subprocess.run(
                                        [
                                            "pingo",
                                            "-s4",
                                            "-lossless",
                                            "-webp",
                                            "-process=4",
                                            "-no-jpeg",
                                            subfolder,
                                        ],
                                        capture_output=True,
                                        text=True,
                                    )
                                pingo_output = result.stdout + (
                                    "\n" + result.stderr if result.stderr else ""
                                )
                            # Remove any image file (except .webp) if a .webp with the same name exists
                            image_extensions = {
                                ".png",
                                ".jpg",
                                ".jpeg",
                                ".avif",
                                ".gif",
                            }
                            for root, _, files in os.walk(subfolder):
                                webp_files = {
                                    os.path.splitext(file)[0]
                                    for file in files
                                    if file.endswith(".webp")
                                }
                                for file in files:
                                    name, ext = os.path.splitext(file)
                                    if (
                                        ext.lower() in image_extensions
                                        and name in webp_files
                                    ):
                                        os.remove(os.path.join(root, file))
                            # Compress to cbz
                            with zipfile.ZipFile(
                                zip_file_path, "w", zipfile.ZIP_STORED
                            ) as zipf:
                                for root, _, files in os.walk(subfolder):
                                    for file in files:
                                        file_path = os.path.join(root, file)
                                        arcname = os.path.relpath(
                                            file_path, start=subfolder
                                        )
                                        zipf.write(file_path, arcname)
                            import shutil

                            try:
                                send2trash(subfolder)
                            except Exception:
                                try:
                                    os.rmdir(subfolder)
                                except Exception:
                                    shutil.rmtree(subfolder, ignore_errors=True)
                            if pingo_output:
                                pingo_outputs.append(
                                    f"{os.path.basename(subfolder)}:\n{pingo_output}"
                                )
                    else:
                        zip_file_path = os.path.join(root_dir, f"{item}.cbz")
                        self.status.set(f"Processing\n{os.path.basename(item_path)}")
                        self.delete_non_image_files(item_path)
                        self.rename_files_with_zero_padding(item_path)
                        pingo_output = None
                        if not self.skip_pingo.get():
                            if self.lossy.get():
                                result = subprocess.run(
                                    ["pingo", "-s4", "-webp", "-process=4", item_path],
                                    capture_output=True,
                                    text=True,
                                )
                            else:
                                result = subprocess.run(
                                    [
                                        "pingo",
                                        "-s4",
                                        "-lossless",
                                        "-webp",
                                        "-process=4",
                                        "-no-jpeg",
                                        item_path,
                                    ],
                                    capture_output=True,
                                    text=True,
                                )
                            pingo_output = result.stdout + (
                                "\n" + result.stderr if result.stderr else ""
                            )
                        # Remove any image file (except .webp) if a .webp with the same name exists
                        image_extensions = {".png", ".jpg", ".jpeg", ".avif", ".gif"}
                        for root, _, files in os.walk(item_path):
                            webp_files = {
                                os.path.splitext(file)[0]
                                for file in files
                                if file.endswith(".webp")
                            }
                            for file in files:
                                name, ext = os.path.splitext(file)
                                if (
                                    ext.lower() in image_extensions
                                    and name in webp_files
                                ):
                                    os.remove(os.path.join(root, file))
                        # Compress to cbz
                        with zipfile.ZipFile(
                            zip_file_path, "w", zipfile.ZIP_STORED
                        ) as zipf:
                            for root, _, files in os.walk(item_path):
                                for file in files:
                                    file_path = os.path.join(root, file)
                                    arcname = os.path.relpath(
                                        file_path, start=item_path
                                    )
                                    zipf.write(file_path, arcname)
                        import shutil

                        try:
                            send2trash(item_path)
                        except Exception:
                            try:
                                os.rmdir(item_path)
                            except Exception:
                                shutil.rmtree(item_path, ignore_errors=True)
                        if pingo_output:
                            pingo_outputs.append(
                                f"{os.path.basename(item_path)}:\n{pingo_output}"
                            )
            self.status.set("Done!")
            output_message = (
                "\n\n".join(pingo_outputs) if pingo_outputs else "Processing complete!"
            )
            messagebox.showinfo("Done", output_message)
        except Exception as e:
            self.status.set(f"Error: {e}")
            messagebox.showerror("Error", str(e))


def main():
    root = tk.Tk()
    app = ComicOptimizerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
