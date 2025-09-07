import tkinter as tk

import ttkbootstrap as ttk

from .appearance import AppearanceTab


class SettingsDialog:
    def __init__(self, root):
        self.root = root
        self.win = tk.Toplevel(root)
        self.win.title("Settings")
        self.win.geometry("500x500")
        self.win.resizable(False, False)

        nb = ttk.Notebook(self.win)
        nb.pack(fill=ttk.BOTH, expand=True, padx=10, pady=10)

        # Add Appearance tab
        appearance_tab = AppearanceTab(nb, root)
        nb.add(appearance_tab, text="Appearance")

    def show(self):
        self.win.deiconify()
        self.win.lift()
        self.win.grab_set()
