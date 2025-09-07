import ttkbootstrap as tb
import tkinter as tk


class AppearanceTab(tb.Frame):
    def __init__(self, parent, root, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.root = root
        # Theme selection
        theme_label = tb.Label(self, text="Theme:", font=("Segoe UI", 10, "bold"))
        theme_label.pack(anchor=tb.W, pady=(10, 2))
        theme_names = list(self.root.style.theme_names())
        self.theme_var = tb.StringVar(value=self.root.style.theme_use())
        theme_combo = tb.Combobox(
            self,
            textvariable=self.theme_var,
            values=theme_names,
            state="readonly",
            width=20,
        )
        theme_combo.pack(anchor=tb.W, pady=(0, 10))

        def apply_theme(event=None):
            new_theme = self.theme_var.get()
            self.root.style.theme_use(new_theme)

        theme_combo.bind("<<ComboboxSelected>>", apply_theme)

        # Font size
        font_label = tb.Label(self, text="Font Size:", font=("Segoe UI", 10, "bold"))
        font_label.pack(anchor=tb.W, pady=(10, 2))
        self.font_size_var = tb.IntVar(value=10)
        font_spin = tb.Spinbox(
            self,
            from_=8,
            to=24,
            textvariable=self.font_size_var,
            width=5,
        )
        font_spin.pack(anchor=tb.W, pady=(0, 10))

        def apply_font():
            size = self.font_size_var.get()
            self.root.option_add("*Font", f"Segoe UI {size}")

        font_btn = tb.Button(self, text="Apply Font Size", command=apply_font)
        font_btn.pack(anchor=tb.W, pady=(0, 10))
