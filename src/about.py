import subprocess
import tkinter as tk

import ttkbootstrap as ttk

try:
    from version import __version__ as VERSION
except ImportError:
    try:
        VERSION = subprocess.check_output([
            'git', 'describe', '--tags', '--abbrev=0'
        ], stderr=subprocess.STDOUT).decode().strip()
    except Exception:
        VERSION = "unknown"


class AboutDialog:
    PROJECT_NAME = "Comic Optimizer"
    COPYRIGHT = "\u00A9 2025 phnthnhnm"
    SOURCE_URL = "https://github.com/phnthnhnm/comic-optimizer"

    def __init__(self, parent):
        self.parent = parent
        self.dialog = None

    def show(self):
        about_text = f"{self.PROJECT_NAME}\nVersion: {VERSION}\n{self.COPYRIGHT}"
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title(f"About {self.PROJECT_NAME}")
        self.dialog.geometry("400x200")
        self.dialog.resizable(False, False)
        frame = ttk.Frame(self.dialog, padding=20)
        frame.pack(fill="both", expand=True)
        label = ttk.Label(frame, text=about_text, font=("Segoe UI", 11), justify="left")
        label.pack(anchor="w", pady=(0, 10))
        link = ttk.Label(frame, text=self.SOURCE_URL, foreground="blue", cursor="hand2")
        link.pack(anchor="w")

        def open_link(event):
            import webbrowser
            webbrowser.open_new(self.SOURCE_URL)

        link.bind("<Button-1>", open_link)
        ok_btn = ttk.Button(frame, text="OK", command=self.dialog.destroy, width=10)
        ok_btn.pack(pady=10, anchor="e")
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        self.dialog.focus_set()
