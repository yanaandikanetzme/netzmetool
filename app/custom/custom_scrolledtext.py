# src/custom_scrolledtext.py
import platform
import tkinter as tk
from tkinter import scrolledtext

class CustomScrolledText(tk.Frame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master)
        
        # Extracting custom arguments
        self.width = kwargs.pop('width', None)
        self.height = kwargs.pop('height', None)
        self.wrap = kwargs.pop('wrap', tk.WORD)
        self.state = kwargs.pop('state', tk.NORMAL)
        
        # Creating the scrolled text widget
        self.text_widget = scrolledtext.ScrolledText(self, 
                                                     width=self.width, 
                                                     height=self.height, 
                                                     wrap=self.wrap, 
                                                     state=self.state, 
                                                     undo=True, 
                                                     **kwargs)
        self.text_widget.grid(sticky=tk.NSEW)
        
        # Configure row and column weights to make text_widget expandable
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Binding keyboard shortcuts for undo/redo
        self.bind_shortcuts()
    
    def bind_shortcuts(self):
        # Detect the operating system
        system = platform.system()
        
        if system == 'Darwin':  # macOS
            self.text_widget.bind('<Command-z>', self.undo)
            self.text_widget.bind('<Command-y>', self.redo)
            self.text_widget.bind('<Command-Shift-z>', self.redo)
        else:  # Windows and Linux
            self.text_widget.bind('<Control-z>', self.undo)
            self.text_widget.bind('<Control-y>', self.redo)
            self.text_widget.bind('<Control-Shift-z>', self.redo)
    
    def undo(self, event=None):
        try:
            self.text_widget.edit_undo()
        except tk.TclError:
            pass
        return "break"
    
    def redo(self, event=None):
        try:
            self.text_widget.edit_redo()
        except tk.TclError:
            pass
        return "break"
    
    def get(self, *args):
        return self.text_widget.get(*args)
    
    def delete(self, *args):
        self.text_widget.delete(*args)

    def insert(self, *args):
        self.text_widget.insert(*args)
