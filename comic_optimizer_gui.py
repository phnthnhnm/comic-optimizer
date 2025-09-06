import os
import threading
import ttkbootstrap as tb
from ttkbootstrap.dialogs import Messagebox
from tkinter import filedialog
import optimizer_core


class ComicOptimizerGUI:
    def set_status(self, message: str) -> None:
        self.root.after(0, self.status.set, message)

    def show_info(self, message: str, title: str = "Done") -> None:
        self.root.after(0, lambda: Messagebox.show_info(message, title=title))

    def show_error(self, message: str, title: str = "Error") -> None:
        self.root.after(0, lambda: Messagebox.show_error(message, title=title))

    """Modern Tkinter GUI for the Comic Optimizer using ttkbootstrap."""

    def __init__(self, root: tb.Window):
        self.root = root
        self.root.title("Comic Optimizer")
        self.root.geometry("500x300")
        self.root.resizable(False, False)

        self.dir_path = tb.StringVar()
        self.lossy = tb.BooleanVar(value=False)
        self.skip_pingo = tb.BooleanVar(value=False)
        self.status = tb.StringVar(value="Idle.")

        self.create_widgets()

    def create_widgets(self) -> None:
        mainframe = tb.Frame(self.root, padding=20)
        mainframe.pack(fill=tb.BOTH, expand=True)

        # Directory selection
        dir_label = tb.Label(
            mainframe, text="Select Root Directory:", font=("Segoe UI", 11, "bold")
        )
        dir_label.grid(row=0, column=0, sticky=tb.W, pady=(0, 5))

        dir_frame = tb.Frame(mainframe)
        dir_frame.grid(row=1, column=0, sticky=tb.W + tb.E, pady=(0, 10))
        dir_entry = tb.Entry(dir_frame, textvariable=self.dir_path, width=40)
        dir_entry.pack(side=tb.LEFT, fill=tb.X, expand=True)
        browse_btn = tb.Button(dir_frame, text="Browse", command=self.browse_dir)
        browse_btn.pack(side=tb.LEFT, padx=5)

        # Options
        options_frame = tb.Frame(mainframe)
        options_frame.grid(row=2, column=0, sticky=tb.W, pady=(0, 10))
        lossy_chk = tb.Checkbutton(options_frame, text="Lossy", variable=self.lossy)
        lossy_chk.pack(side=tb.LEFT, padx=(0, 20))
        skip_chk = tb.Checkbutton(
            options_frame, text="Skip pingo", variable=self.skip_pingo
        )
        skip_chk.pack(side=tb.LEFT)

        # Start button
        start_btn = tb.Button(
            mainframe, text="Start", command=self.start_processing, width=15
        )
        start_btn.grid(row=3, column=0, pady=(0, 15))

        # Status label
        status_label = tb.Label(
            mainframe, textvariable=self.status, font=("Segoe UI", 10)
        )
        status_label.grid(row=4, column=0, sticky=tb.W, pady=(10, 0))

    def browse_dir(self) -> None:
        path = filedialog.askdirectory()
        if path:
            self.dir_path.set(path)

    def start_processing(self) -> None:
        """Start the processing in a background thread."""
        if not self.dir_path.get():
            Messagebox.show_error("Please select a directory.", title="Error")
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
                            self.set_status(
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
                        self.set_status(f"Processing\n{os.path.basename(item_path)}")
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
            self.set_status("Done!")
            output_message = (
                "\n\n".join(pingo_outputs) if pingo_outputs else "Processing complete!"
            )
            self.show_info(output_message, title="Done")
        except Exception as e:
            self.set_status(f"Error: {e}")
            self.show_error(str(e), title="Error")


def main() -> None:
    """Entry point for the GUI application."""
    root = tb.Window(themename="flatly")
    app = ComicOptimizerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
