import os
import threading
import ttkbootstrap as tb
from ttkbootstrap.dialogs import Messagebox
from tkinter import filedialog
import core
import config


class GUI:
    def open_settings(self):
        from settings.dialog import SettingsDialog

        dlg = SettingsDialog(self.root)
        dlg.show()

    def set_status(self, message: str) -> None:
        self.root.after(0, self.status.set, message)

    def show_info(self, message: str, title: str = "Done") -> None:
        import tkinter as tk

        def show_custom_dialog():
            dialog = tk.Toplevel(self.root)
            dialog.title(title)
            dialog.geometry("700x400")
            dialog.resizable(True, True)
            # Frame for padding
            frame = tb.Frame(dialog, padding=15)
            frame.pack(fill=tb.BOTH, expand=True)
            # Text widget for report
            text = tb.Text(frame, wrap="word", font=("Segoe UI", 10))
            text.insert("1.0", message)
            text.config(state="disabled")
            text.pack(fill=tb.BOTH, expand=True)
            # OK button
            ok_btn = tb.Button(frame, text="OK", command=dialog.destroy, width=10)
            ok_btn.pack(pady=10)
            # Focus and modal
            dialog.transient(self.root)
            dialog.grab_set()
            dialog.focus_set()

        self.root.after(0, show_custom_dialog)

    def show_error(self, message: str, title: str = "Error") -> None:
        self.root.after(0, lambda: Messagebox.show_error(message, title=title))

    """Modern Tkinter GUI for the Comic Optimizer using ttkbootstrap."""

    def __init__(self, root: tb.Window):
        import config

        self.root = root
        self.root.title("Comic Optimizer")
        self.root.geometry("500x330")
        self.root.resizable(False, False)

        # Settings menu
        menubar = tb.Menu(self.root)
        self.root.config(menu=menubar)
        settings_menu = tb.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Settings", menu=settings_menu)
        settings_menu.add_command(label="Preferences...", command=self.open_settings)

        self.dir_path = tb.StringVar()
        # Load available presets from presets.json
        import json

        preset_path = os.path.join(os.path.dirname(__file__), "presets.json")
        with open(preset_path, "r", encoding="utf-8") as f:
            self.preset_dict = json.load(f)
            self.presets = list(self.preset_dict.keys())
        self.selected_preset = tb.StringVar(
            value=self.presets[0] if self.presets else ""
        )
        self.skip_pingo = tb.BooleanVar(value=False)
        self.status = tb.StringVar(value="Idle.")
        self.output_extension = tb.StringVar(value=".cbz")
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

        # Output extension selection
        ext_frame = tb.Frame(mainframe)
        ext_frame.grid(row=2, column=0, sticky=tb.W, pady=(0, 10))
        ext_label = tb.Label(ext_frame, text="Output Extension:", font=("Segoe UI", 10))
        ext_label.pack(side=tb.LEFT)
        ext_combo = tb.Combobox(
            ext_frame,
            textvariable=self.output_extension,
            values=config.OUTPUT_EXTENSIONS,
            width=8,
            state="readonly",
        )
        ext_combo.pack(side=tb.LEFT, padx=(5, 0))

        # Preset content display
        self.preset_content = tb.StringVar()
        self.preset_content.set(self._get_preset_content(self.selected_preset.get()))
        preset_content_label = tb.Label(
            mainframe,
            textvariable=self.preset_content,
            font=("Segoe UI", 9),
            wraplength=450,
            justify=tb.LEFT,
            foreground="#555",
        )
        preset_content_label.grid(row=3, column=0, sticky=tb.W, pady=(0, 5))

        # Options
        options_frame = tb.Frame(mainframe)
        options_frame.grid(row=4, column=0, sticky=tb.W, pady=(0, 10))
        preset_label = tb.Label(options_frame, text="Pingo Preset:")
        preset_label.pack(side=tb.LEFT)
        preset_combo = tb.Combobox(
            options_frame,
            textvariable=self.selected_preset,
            values=self.presets,
            width=18,
            state="readonly",
        )
        preset_combo.pack(side=tb.LEFT, padx=(0, 20))
        skip_chk = tb.Checkbutton(
            options_frame, text="Skip pingo", variable=self.skip_pingo
        )
        skip_chk.pack(side=tb.LEFT)

        # Start button
        start_btn = tb.Button(
            mainframe, text="Start", command=self.start_processing, width=15
        )
        start_btn.grid(row=5, column=0, pady=(0, 15))

        # Status label
        status_label = tb.Label(
            mainframe, textvariable=self.status, font=("Segoe UI", 10)
        )
        status_label.grid(row=6, column=0, sticky=tb.W, pady=(10, 0))

        # Update preset content when selection changes
        preset_combo.bind("<<ComboboxSelected>>", self._on_preset_change)

    def _get_preset_content(self, preset_name: str) -> str:
        cmd = self.preset_dict.get(preset_name, [])
        return (
            "Command: " + " ".join(cmd) if cmd else "No command found for this preset."
        )

    def _on_preset_change(self, event=None):
        self.preset_content.set(self._get_preset_content(self.selected_preset.get()))

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
        output_ext = self.output_extension.get()
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
                                item_path, f"{os.path.basename(subfolder)}{output_ext}"
                            )
                            self.set_status(
                                f"Processing\n{os.path.basename(subfolder)}"
                            )
                            pingo_output = core.process_single_folder(
                                subfolder,
                                zip_file_path,
                                self.selected_preset.get(),
                                self.skip_pingo.get(),
                            )
                            if pingo_output:
                                pingo_outputs.append(
                                    f"{os.path.basename(subfolder)}:\n{pingo_output}"
                                )
                    else:
                        zip_file_path = os.path.join(root_dir, f"{item}{output_ext}")
                        self.set_status(f"Processing\n{os.path.basename(item_path)}")
                        pingo_output = core.process_single_folder(
                            item_path,
                            zip_file_path,
                            self.selected_preset.get(),
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
    app = GUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
