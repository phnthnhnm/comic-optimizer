import threading
import tkinter as tk  # Add for Text/Scrollbar widgets
from tkinter import filedialog

import darkdetect
import ttkbootstrap as ttk
from ttkbootstrap.constants import SUCCESS, DANGER, INFO
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
        self.root.geometry("900x400")  # Wider for report panel
        self.root.resizable(True, True)

        # Settings menu
        menubar = ttk.Menu(self.root)
        self.root.config(menu=menubar)
        menubar.add_command(label="Settings", command=self.open_settings)
        menubar.add_command(label="About", command=self.show_about)

        # Set dir_path to last_root_dir if available
        last_dir = self.user_settings.get("last_root_dir", "")
        self.dir_path = ttk.StringVar(value=last_dir)

        # Load available presets from user_settings
        self.preset_dict = self.user_settings.get("presets", {})
        self.presets = list(self.preset_dict.keys())

        # Set selected_preset from last_preset if available and valid
        last_preset = self.user_settings.get("last_preset", "")
        initial_preset = last_preset if last_preset in self.presets else (self.presets[0] if self.presets else "")
        self.selected_preset = ttk.StringVar(value=initial_preset)

        # Set skip_pingo from user_settings
        self.skip_pingo = ttk.BooleanVar(value=self.user_settings.get("skip_pingo", False))
        self.status = ttk.StringVar(value="Idle.")

        # Set output_extension from last_output_ext if available and valid
        last_output_ext = self.user_settings.get("last_output_ext", ".cbz")
        initial_output_ext = last_output_ext if last_output_ext in config.OUTPUT_EXTENSIONS else \
        config.OUTPUT_EXTENSIONS[0]
        self.output_extension = ttk.StringVar(value=initial_output_ext)
        self.report_text = None  # Initialize here to avoid warning
        self.create_widgets()

    def create_widgets(self) -> None:
        # Main horizontal frame
        container = ttk.Frame(self.root)
        container.pack(fill="both", expand=True)
        container.columnconfigure(0, weight=1)
        container.columnconfigure(1, weight=2)
        container.rowconfigure(0, weight=1)

        # Left: main controls
        mainframe = ttk.Frame(container, padding=20)
        mainframe.grid(row=0, column=0, sticky="nsew")

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
        ext_combo.bind("<<ComboboxSelected>>", self._on_output_ext_change)

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
            options_frame, text="Skip pingo", variable=self.skip_pingo,
            command=self._on_skip_pingo_change
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
            mainframe, textvariable=self.status, font=("Segoe UI", 10), style=INFO
        )
        status_label.grid(row=7, column=0, sticky="w", pady=(10, 0))

        # Update preset content when selection changes
        preset_combo.bind("<<ComboboxSelected>>", self._on_preset_change)

        # Right: live pingo report panel
        report_frame = ttk.Frame(container, padding=10)
        report_frame.grid(row=0, column=1, sticky="nsew")
        report_label = ttk.Label(report_frame, text="Pingo Report Output", font=("Segoe UI", 11, "bold"))
        report_label.pack(anchor="w")
        # Use native tkinter Text for better control
        self.report_text = tk.Text(report_frame, wrap="word", font=("Segoe UI", 10), state="disabled", height=20,
                                   width=60)
        self.report_text.pack(fill="both", expand=True, side="left")
        report_scroll = ttk.Scrollbar(report_frame, orient="vertical", command=self.report_text.yview)
        report_scroll.pack(side="right", fill="y")
        self.report_text["yscrollcommand"] = report_scroll.set

    def _get_preset_content(self, preset_name: str) -> str:
        cmd = self.preset_dict.get(preset_name, [])
        return (
            "Command: " + " ".join(cmd) if cmd else "No command found for this preset."
        )

    def _on_preset_change(self, event=None):
        """Save last chosen preset."""
        self.preset_content.set(self._get_preset_content(self.selected_preset.get()))
        self.user_settings["last_preset"] = self.selected_preset.get()
        save_user_settings(self.user_settings)

    def _on_skip_pingo_change(self):
        """Save skip_pingo state."""
        self.user_settings["skip_pingo"] = self.skip_pingo.get()
        save_user_settings(self.user_settings)

    def _on_output_ext_change(self, event=None):
        """Save last selected output extension."""
        self.user_settings["last_output_ext"] = self.output_extension.get()
        save_user_settings(self.user_settings)

    def browse_dir(self) -> None:
        path = filedialog.askdirectory()
        if path:
            self.dir_path.set(path)
            # Save last selected root directory
            self.user_settings["last_root_dir"] = path
            save_user_settings(self.user_settings)

    def clear_report(self):
        self.report_text.config(state="normal")
        self.report_text.delete("1.0", tk.END)
        self.report_text.config(state="disabled")

    def append_report(self, text):
        def _append():
            self.report_text.config(state="normal")
            self.report_text.insert(tk.END, text + "\n\n")
            self.report_text.see(tk.END)
            self.report_text.config(state="disabled")

        self.root.after(0, _append)

    def start_processing(self) -> None:
        """Start the processing in a background thread."""
        if not self.dir_path.get():
            Messagebox.show_error("Please select a directory.", title="Error")
            return
        self.clear_report()  # Clear report at start
        threading.Thread(target=self.run_processing_thread, daemon=True).start()

    def _process_and_report_folder(self, folder_path, zip_file_path, status_callback, report_callback, pingo_outputs):
        status_callback(f"Processing\n{core.os.path.basename(folder_path)}")
        pingo_output = core.process_single_folder(
            folder_path,
            zip_file_path,
            self.selected_preset.get(),
            self.skip_pingo.get(),
            self.preset_dict
        )
        if pingo_output:
            report_callback(core.os.path.basename(folder_path), pingo_output)
            pingo_outputs.append(f"{core.os.path.basename(folder_path)}:\n{pingo_output}")

    def run_processing_thread(self) -> None:
        """Thread target: call core.process_root_directory and update GUI."""
        root_dir = self.dir_path.get()
        output_ext = self.output_extension.get()
        try:
            # Custom callback to update report live
            def status_callback(msg):
                self.set_status(msg)

            def report_callback(folder, pingo_output):
                if pingo_output:
                    self.append_report(f"{folder}:\n{pingo_output}")

            # Wrap process_root_directory to call report_callback after each folder
            pingo_outputs = []
            for item in core.os.listdir(root_dir):
                item_path = core.os.path.join(root_dir, item)
                if core.os.path.isdir(item_path):
                    subfolders = [
                        core.os.path.join(item_path, subfolder)
                        for subfolder in core.os.listdir(item_path)
                        if core.os.path.isdir(core.os.path.join(item_path, subfolder))
                    ]
                    if subfolders:
                        for subfolder in subfolders:
                            zip_file_path = core.os.path.join(
                                item_path, f"{core.os.path.basename(subfolder)}{output_ext}"
                            )
                            self._process_and_report_folder(subfolder, zip_file_path, status_callback, report_callback,
                                                            pingo_outputs)
                    else:
                        zip_file_path = core.os.path.join(root_dir, f"{item}{output_ext}")
                        self._process_and_report_folder(item_path, zip_file_path, status_callback, report_callback,
                                                        pingo_outputs)
            self.set_status("Done!")
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
