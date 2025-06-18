# src/custom_text.py
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter import *
from tkinter.filedialog import askopenfile


class CustomText(tk.Text):
    def __init__(self, parent, width=None, height=None, *args, **kwargs):
        """A text widget that reports on internal widget commands"""
        tk.Text.__init__(self, parent, *args, **kwargs)
        
        # Konfigurasi wrap, width, dan height
        self.config(wrap='word', undo=True, autoseparators=True, maxundo=-1)
        if width:
            self.config(width=width)
        if height:
            self.config(height=height)
        
        # Membuat proxy untuk widget yang mendasarinya
        self._orig = self._w + "_orig"
        self.tk.call("rename", self._w, self._orig)
        self.tk.createcommand(self._w, self._proxy)
        
        # Binding shortcut keyboard
        self.bind('<Control-z>', self.undo)
        self.bind('<Control-y>', self.redo)
        self.bind('<Control-Shift-Z>', self.redo)
        
        # Binding untuk Mac
        self.bind('<Command-z>', self.undo)
        self.bind('<Command-y>', self.redo)
        self.bind('<Command-Shift-Z>', self.redo)

    def _proxy(self, command, *args):
        cmd = (self._orig, command) + args
        try:
            result = self.tk.call(cmd)
        except Exception:
            return None

        if command in ("insert", "delete", "replace"):
            self.event_generate("<<TextModified>>")

        return result

    def undo(self, event=None):
        """Melakukan undo"""
        try:
            self.edit_undo()
        except tk.TclError:
            pass
        return "break"

    def redo(self, event=None):
        """Melakukan redo"""
        try:
            self.edit_redo()
        except tk.TclError:
            pass
        return "break"

    def set_dimensions(self, width=None, height=None):
        """Mengatur ulang dimensi widget"""
        if width:
            self.config(width=width)
        if height:
            self.config(height=height)