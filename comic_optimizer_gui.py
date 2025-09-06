import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
import optimizer_core


class ComicOptimizerGUI:
    """Tkinter GUI for the Comic Optimizer."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Comic Optimizer")
        self.root.geometry("500x300")

        self.dir_path = tk.StringVar()
        self.lossy = tk.BooleanVar(value=False)
        self.skip_pingo = tk.BooleanVar(value=False)
        self.status = tk.StringVar(value="Idle.")

        self.create_widgets()

    def create_widgets(self) -> None:
        tk.Label(self.root, text="Select Root Directory:").pack(pady=5)
        frame = tk.Frame(self.root)
        frame.pack(pady=5)
        tk.Entry(frame, textvariable=self.dir_path, width=40).pack(side=tk.LEFT)
        tk.Button(frame, text="Browse", command=self.browse_dir).pack(
            side=tk.LEFT, padx=5
        )

        tk.Checkbutton(self.root, text="Lossy", variable=self.lossy).pack(
            anchor=tk.W, padx=20
        )
        tk.Checkbutton(self.root, text="Skip pingo", variable=self.skip_pingo).pack(
            anchor=tk.W, padx=20
        )

        tk.Button(self.root, text="Start", command=self.start_processing).pack(pady=10)
        tk.Label(self.root, textvariable=self.status, fg="blue").pack(pady=10)

    def browse_dir(self) -> None:
        path = filedialog.askdirectory()
        if path:
            self.dir_path.set(path)

    def start_processing(self) -> None:
        """Start the processing in a background thread."""
        if not self.dir_path.get():
            messagebox.showerror("Error", "Please select a directory.")
            return
        self.status.set("Processing...")
        threading.Thread(target=self.process_folders, daemon=True).start()

    def process_folders(self) -> None:
        """Process all folders in the selected root directory."""
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
                            pingo_output = optimizer_core.process_single_folder(
                                subfolder,
                                zip_file_path,
                                self.lossy.get(),
                                self.skip_pingo.get(),
                            )
                            if pingo_output:
                                pingo_outputs.append(
                                    f"{os.path.basename(subfolder)}:\n{pingo_output}"
                                )
                    else:
                        zip_file_path = os.path.join(root_dir, f"{item}.cbz")
                        self.status.set(f"Processing\n{os.path.basename(item_path)}")
                        pingo_output = optimizer_core.process_single_folder(
                            item_path,
                            zip_file_path,
                            self.lossy.get(),
                            self.skip_pingo.get(),
                        )
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


def main() -> None:
    """Entry point for the GUI application."""
    root = tk.Tk()
    app = ComicOptimizerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
