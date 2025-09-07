import tkinter.font as tkfont

import ttkbootstrap as ttk

import config


class AppearanceTab(ttk.Frame):
    def __init__(self, parent, root, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.root = root
        # Theme selection
        theme_label = ttk.Label(self, text="Theme:", font=("Segoe UI", 10, "bold"))
        theme_label.pack(anchor="w", pady=(10, 2))
        theme_names = list(self.root.style.theme_names())
        self.theme_var = ttk.StringVar(value=self.root.style.theme_use())
        theme_combo = ttk.Combobox(
            self,
            textvariable=self.theme_var,
            values=theme_names,
            state="readonly",
            width=20,
        )
        theme_combo.pack(anchor="w", pady=(0, 10))

        def apply_theme(event=None):
            new_theme = self.theme_var.get()
            self.root.style.theme_use(new_theme)

        theme_combo.bind("<<ComboboxSelected>>", apply_theme)

        # Font family selection
        font_label = ttk.Label(self, text="Font Family:", font=("Segoe UI", 10, "bold"))
        font_label.pack(anchor="w", pady=(10, 2))
        font_families = sorted(tkfont.families())
        self.font_family_var = ttk.StringVar(value=config.DEFAULT_FONT_FAMILY)
        font_family_combo = ttk.Combobox(
            self,
            textvariable=self.font_family_var,
            values=font_families,
            state="readonly",
            width=30,
        )
        font_family_combo.pack(anchor="w", pady=(0, 10))

        # Font size selection
        size_label = ttk.Label(self, text="Font Size:", font=("Segoe UI", 10, "bold"))
        size_label.pack(anchor="w", pady=(10, 2))
        self.font_size_var = ttk.IntVar(value=config.DEFAULT_FONT_SIZE)
        size_spin = ttk.Spinbox(
            self,
            from_=8,
            to=32,
            textvariable=self.font_size_var,
            width=5,
            increment=1,
            state="readonly",
        )
        size_spin.pack(anchor="w", pady=(0, 10))

        def apply_font(event=None):
            family = self.font_family_var.get()
            size = self.font_size_var.get()
            new_font = (family, size)
            self._set_font_recursive(self.root, new_font)

        font_family_combo.bind("<<ComboboxSelected>>", apply_font)
        self.font_size_var.trace_add("write", lambda *args: apply_font())
        size_spin.bind("<FocusOut>", apply_font)

        # Restore Default Button
        def restore_defaults():
            self.font_family_var.set(config.DEFAULT_FONT_FAMILY)
            self.font_size_var.set(config.DEFAULT_FONT_SIZE)
            self.root.after(0, apply_font)

        restore_btn = ttk.Button(self, text="Restore Default Font", command=restore_defaults)
        restore_btn.pack(anchor="w", pady=(10, 2))

    def _set_font_recursive(self, widget, font_tuple):
        try:
            widget.configure(font=font_tuple)
        except Exception:
            pass
        for child in widget.winfo_children():
            self._set_font_recursive(child, font_tuple)
