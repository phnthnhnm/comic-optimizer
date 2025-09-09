import json
import os
import threading
from tkinter import filedialog

import darkdetect
import ttkbootstrap as ttk
from ttkbootstrap.constants import SUCCESS, DANGER
from ttkbootstrap.dialogs import Messagebox

import config
import core
from settings.settings_utils import load_user_settings, save_user_settings


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
            frame = ttk.Frame(dialog, padding=15)
            frame.pack(fill="both", expand=True)
            # Text widget for report
            text = ttk.Text(frame, wrap="word", font=("Segoe UI", 10))
            text.insert("1.0", message)
            text.config(state="disabled")
            text.pack(fill="both", expand=True)
            # OK button
            ok_btn = ttk.Button(frame, text="OK", command=dialog.destroy, width=10)
            ok_btn.pack(pady=10)
            # Focus and modal
            dialog.transient(self.root)
            dialog.grab_set()
            dialog.focus_set()

        self.root.after(0, lambda *args: show_custom_dialog())

    def show_error(self, message: str, title: str = "Error") -> None:
        self.root.after(0, lambda *args: Messagebox.show_error(message, title=title))

    """Modern Tkinter GUI for the Comic Optimizer using ttkbootstrap."""

    def __init__(self, root: ttk.Window):
        self.user_settings = load_user_settings()
        # Apply user font settings if available
        font_family = self.user_settings.get("font_family", "Segoe UI")
        font_size = self.user_settings.get("font_size", 10)
        ttk.Style().configure(".", font=(font_family, font_size))

        self.preset_content = None
        self.root = root
        self.root.title("Comic Optimizer")
        self.root.geometry("500x330")
        self.root.resizable(True, True)

        # Settings menu
        menubar = ttk.Menu(self.root)
        self.root.config(menu=menubar)
        menubar.add_command(label="Settings", command=self.open_settings)
        menubar.add_command(label="About", command=self.show_about)

        # Set dir_path to last_root_dir if available
        last_dir = self.user_settings.get("last_root_dir", "")
        self.dir_path = ttk.StringVar(value=last_dir)
        # Load available presets from presets.json
        preset_path = os.path.join(os.path.dirname(__file__), "presets.json")
        with open(preset_path, "r", encoding="utf-8") as f:
            self.preset_dict = json.load(f)
            self.presets = list(self.preset_dict.keys())
        self.selected_preset = ttk.StringVar(
            value=self.presets[0] if self.presets else ""
        )
        self.skip_pingo = ttk.BooleanVar(value=False)
        self.status = ttk.StringVar(value="Idle.")
        self.output_extension = ttk.StringVar(value=".cbz")
        self.create_widgets()

    def create_widgets(self) -> None:
        mainframe = ttk.Frame(self.root, padding=20)
        mainframe.pack(fill="both", expand=True)

        # Warning label
        warning_label = ttk.Label(
            mainframe,
            text="!! WARNING !! - DO BACKUP - USE ONLY ON TEST FILES",
            font=("Segoe UI", 10, "bold"),
            foreground="",
            style=DANGER
        )
        warning_label.grid(row=0, column=0, sticky="w", pady=(0, 10))

        # Directory selection
        dir_label = ttk.Label(
            mainframe, text="Select Root Directory:", font=("Segoe UI", 10, "bold")
        )
        dir_label.grid(row=1, column=0, sticky="w", pady=(0, 5))

        dir_frame = ttk.Frame(mainframe)
        dir_frame.grid(row=2, column=0, sticky="we", pady=(0, 10))
        dir_entry = ttk.Entry(dir_frame, textvariable=self.dir_path, width=40)
        dir_entry.pack(side="left", fill="x", expand=True)
        browse_btn = ttk.Button(dir_frame, text="Browse", command=self.browse_dir)
        browse_btn.pack(side="left", padx=5)

        # Output extension selection
        ext_frame = ttk.Frame(mainframe)
        ext_frame.grid(row=3, column=0, sticky="w", pady=(0, 10))
        ext_label = ttk.Label(
            ext_frame, text="Output Extension:", font=("Segoe UI", 10)
        )
        ext_label.pack(side="left")
        ext_combo = ttk.Combobox(
            ext_frame,
            textvariable=self.output_extension,
            values=config.OUTPUT_EXTENSIONS,
            width=8,
            state="readonly",
        )
        ext_combo.pack(side="left", padx=(5, 0))

        # Preset content display
        self.preset_content = ttk.StringVar()
        self.preset_content.set(self._get_preset_content(self.selected_preset.get()))
        preset_content_label = ttk.Label(
            mainframe,
            textvariable=self.preset_content,
            font=("Segoe UI", 10),
            wraplength=450,
            justify="left",
            foreground="#555",
        )
        preset_content_label.grid(row=4, column=0, sticky="w", pady=(0, 5))

        # Options
        options_frame = ttk.Frame(mainframe)
        options_frame.grid(row=5, column=0, sticky="w", pady=(0, 10))
        preset_label = ttk.Label(options_frame, text="Pingo Preset:")
        preset_label.pack(side="left")
        preset_combo = ttk.Combobox(
            options_frame,
            textvariable=self.selected_preset,
            values=self.presets,
            width=18,
            state="readonly",
        )
        preset_combo.pack(side="left", padx=(0, 20))
        skip_chk = ttk.Checkbutton(
            options_frame, text="Skip pingo", variable=self.skip_pingo
        )
        skip_chk.pack(side="left")

        # Start button
        start_btn = ttk.Button(
            mainframe,
            text="Start",
            command=self.start_processing,
            width=15,
            style=SUCCESS,
        )
        start_btn.grid(row=6, column=0, pady=(0, 15))

        # Status label
        status_label = ttk.Label(
            mainframe, textvariable=self.status, font=("Segoe UI", 10)
        )
        status_label.grid(row=7, column=0, sticky="w", pady=(10, 0))

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
            # Save last selected root directory
            self.user_settings["last_root_dir"] = path
            save_user_settings(self.user_settings)

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

    def show_about(self):
        from about import AboutDialog

        dlg = AboutDialog(self.root)
        dlg.show()


def main() -> None:
    from settings.settings_utils import load_user_settings
    user_settings = load_user_settings()
    theme = user_settings.get("theme")
    if not theme:
        theme = "darkly" if darkdetect.isDark() else "flatly"
    root = ttk.Window(themename=theme)
    app = GUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
