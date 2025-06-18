# src/custom_treeview.py
import tkinter as tk
from tkinter import ttk
import platform

class CustomTreeview(ttk.Treeview):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.bind_copy_shortcut()
        self.heading_click_handlers()

    def bind_copy_shortcut(self):
        operating_system = platform.system()
        if operating_system == "Windows":
            self.bind("<Control-c>", self.copy_selection)
        elif operating_system == "Darwin":  # macOS
            self.bind("<Command-c>", self.copy_selection)
        else:
            self.bind("<Control-c>", self.copy_selection)

    def copy_selection(self, event=None):
        selection = self.selection()
        if selection:
            data = ["\t".join(self.item(item, "values")) for item in selection]
            clipboard = "\n".join(data)
            self.clipboard_clear()
            self.clipboard_append(clipboard)

    def heading_click_handlers(self):
        for col in self["columns"]:
            self.heading(col, text=col, command=lambda c=col: self.sort_by(c, False))

    def sort_by(self, col, descending):
        """Sort tree contents when a column header is clicked on."""
        data = [(self.set(child, col), child) for child in self.get_children('')]

        # Sort the data in place
        data.sort(reverse=descending)

        # Rearrange items in sorted positions
        for idx, item in enumerate(data):
            self.move(item[1], '', idx)

        # Reverse sort direction for next click
        self.heading(col, command=lambda: self.sort_by(col, not descending))
