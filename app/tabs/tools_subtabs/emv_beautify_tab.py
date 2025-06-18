# app/tabs/tools_subtabs/emv_beautify_tab.py
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from app.custom.custom_text import CustomText
from src.emv.supp import supp
from app.custom.custom_scrolledtext import CustomScrolledText


class EMVBeautifyTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.create_ui()

    def create_ui(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        # Input frame
        input_frame = ttk.LabelFrame(self, text="Input")
        input_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=(10, 5))
        input_frame.columnconfigure(0, weight=1)

        self.input_text = CustomText(input_frame, height=5)
        self.input_text.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.input_text.bind("<<TextModified>>", self.beautify_emv)

        # Add scrollbar to input text
        input_scrollbar = ttk.Scrollbar(input_frame, orient="vertical", command=self.input_text.yview)
        input_scrollbar.grid(row=0, column=1, sticky="ns")
        self.input_text.configure(yscrollcommand=input_scrollbar.set)

        # Output frame
        output_frame = ttk.LabelFrame(self, text="Output")
        output_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(5, 10))
        output_frame.columnconfigure(0, weight=1)
        output_frame.rowconfigure(0, weight=1)

        self.output_text = CustomScrolledText(output_frame, wrap=tk.WORD)
        self.output_text.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        # Make the output text read-only by binding to all key events
        self.output_text.bind("<Key>", lambda e: "break")

        # Button frame
        button_frame = ttk.Frame(self)
        button_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=5)
        button_frame.columnconfigure(1, weight=1)

        ttk.Button(button_frame, text="Clear", command=self.clear_all).grid(row=0, column=0, padx=(0, 5))
        ttk.Button(button_frame, text="Copy Output", command=self.copy_output).grid(row=0, column=2, padx=(5, 0))

    def beautify_emv(self, event=None):
        input_emv = self.input_text.get("1.0", 'end-1c').strip()
        if input_emv:
            try:
                result = supp.getAll(input_emv)
                formatted_result = result.replace(r'\n', '\n')
                self.update_output(formatted_result)
            except Exception as e:
                self.update_output(f"Error: {str(e)}")
        else:
            self.update_output("")

    def update_output(self, text):
        # Since we can't use state configuration, we'll use a different approach
        self.output_text.delete('1.0', tk.END)
        self.output_text.insert(tk.END, text)

    def clear_all(self):
        self.input_text.delete('1.0', tk.END)
        self.update_output("")

    def copy_output(self):
        output_content = self.output_text.get('1.0', tk.END).strip()
        if output_content:
            self.clipboard_clear()
            self.clipboard_append(output_content)
            messagebox.showinfo("Copy", "Output copied to clipboard!")
        else:
            messagebox.showinfo("Copy", "No output to copy.")