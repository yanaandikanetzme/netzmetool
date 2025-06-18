# app/tabs/tools_subtabs/compare_text_tab.py
import tkinter as tk
from tkinter import ttk, messagebox
from app.custom.custom_text import CustomText
from difflib import SequenceMatcher
import threading


class CompareText(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.create_ui()

    def create_ui(self):
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)

        # Mode selection
        mode_frame = ttk.Frame(self)
        mode_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=10)
        tk.Label(mode_frame, text="Select Mode:").pack(side=tk.LEFT, padx=(0, 10))
        self.mode_var = tk.StringVar(value="Compare Text")
        mode_combo = ttk.Combobox(mode_frame, textvariable=self.mode_var, values=["Compare Text", "Two Column View"], state="readonly")
        mode_combo.pack(side=tk.LEFT, expand=True, fill=tk.X)
        mode_combo.bind("<<ComboboxSelected>>", self.show_mode)

        paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        paned.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)
        text1_frame, self.text1 = self.create_text_with_scrollbar(paned)
        text2_frame, self.text2 = self.create_text_with_scrollbar(paned)
        paned.add(text1_frame, weight=1)
        paned.add(text2_frame, weight=1)

        # Text input areas
        self.text1 = CustomText(self, height=10, width=50)
        self.text1.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.text2 = CustomText(self, height=10, width=50)
        self.text2.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

        # Result areas
        self.result = CustomText(self, height=20, width=100, state="disabled")
        self.result_text1 = CustomText(self, height=20, width=50, state="disabled")
        self.result_text2 = CustomText(self, height=20, width=50, state="disabled")

        # Action button
        self.action_button = ttk.Button(self, text="Compare", command=self.compare_texts)
        self.action_button.grid(row=3, column=0, columnspan=2, pady=10)

        #ttk.Label(mode_frame, text="?", cursor="question_arrow").pack(side=tk.LEFT, padx=5)
        #mode_frame.bind("<Enter>", lambda e: messagebox.showinfo("Mode Info", "Compare Text: Shows differences in a single view\nTwo Column View: Shows differences side by side"))

        self.show_mode()

    def create_text_with_scrollbar(self, parent):
        frame = ttk.Frame(parent)
        text = CustomText(frame, height=10, width=50)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=text.yview)
        text.configure(yscrollcommand=scrollbar.set)
        text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        return frame, text

    def show_mode(self, event=None):
        mode = self.mode_var.get()
        if mode == "Compare Text":
            self.result.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
            self.result_text1.grid_remove()
            self.result_text2.grid_remove()
            self.action_button.config(text="Compare", command=self.compare_texts)
        else:
            self.result.grid_remove()
            self.result_text1.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
            self.result_text2.grid(row=2, column=1, padx=10, pady=10, sticky="nsew")
            self.action_button.config(text="Show Difference", command=self.show_diff)

    def compare_texts(self):
        threading.Thread(target=self._compare, args=("compare",), daemon=True).start()

    def _compare(self, mode):
        text1_content = self.text1.get("1.0", "end-1c")
        text2_content = self.text2.get("1.0", "end-1c")
        
        if hasattr(self, 'last_comparison') and self.last_comparison == (text1_content, text2_content, mode):
            return
        
        self.last_comparison = (text1_content, text2_content, mode)

    def show_diff(self):
        threading.Thread(target=self._compare, args=("diff",), daemon=True).start()

    def _compare(self, mode):
        text1_content = self.text1.get("1.0", "end-1c")
        text2_content = self.text2.get("1.0", "end-1c")

        matcher = SequenceMatcher(None, text1_content, text2_content, autojunk=False)
        opcodes = matcher.get_opcodes()

        if mode == "compare":
            self.result.configure(state="normal")
            self.result.delete("1.0", "end")
            for tag, i1, i2, j1, j2 in opcodes:
                if tag == 'equal':
                    self.result.insert("end", text1_content[i1:i2], "equal")
                elif tag == 'delete':
                    self.result.insert("end", text1_content[i1:i2], "delete")
                elif tag == 'insert':
                    self.result.insert("end", text2_content[j1:j2], "insert")
                elif tag == 'replace':
                    self.result.insert("end", text1_content[i1:i2], "delete")
                    self.result.insert("end", text2_content[j1:j2], "insert")
            self.result.configure(state="disabled")
        else:
            self.result_text1.configure(state="normal")
            self.result_text1.delete("1.0", "end")
            self.result_text2.configure(state="normal")
            self.result_text2.delete("1.0", "end")
            for tag, i1, i2, j1, j2 in opcodes:
                if tag == 'equal':
                    self.result_text1.insert("end", text1_content[i1:i2], "equal")
                    self.result_text2.insert("end", text2_content[j1:j2], "equal")
                elif tag == 'delete':
                    self.result_text1.insert("end", text1_content[i1:i2], "delete")
                elif tag == 'insert':
                    self.result_text2.insert("end", text2_content[j1:j2], "insert")
                elif tag == 'replace':
                    self.result_text1.insert("end", text1_content[i1:i2], "delete")
                    self.result_text2.insert("end", text2_content[j1:j2], "insert")
            self.result_text1.configure(state="disabled")
            self.result_text2.configure(state="disabled")

        for widget in [self.result, self.result_text1, self.result_text2]:
            widget.tag_configure("equal", foreground="yellow")
            widget.tag_configure("delete", foreground="red")
            widget.tag_configure("insert", foreground="green")