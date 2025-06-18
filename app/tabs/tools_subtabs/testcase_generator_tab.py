# app/tabs/tools_subtabs/testcase_generator_tab.py
import tkinter as tk
from tkinter import ttk, messagebox
from itertools import permutations
from app.custom.custom_text import CustomText

class TestCaseGenerator(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.create_ui()

    def create_ui(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(3, weight=1)

        # Input frame
        input_frame = ttk.LabelFrame(self, text="Input")
        input_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        input_frame.columnconfigure(1, weight=1)

        tk.Label(input_frame, text="Data (comma-separated):").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.data_entry = ttk.Entry(input_frame)
        self.data_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        tk.Label(input_frame, text="Number of Steps:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.steps_entry = ttk.Entry(input_frame)
        self.steps_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        # Generate button
        ttk.Button(self, text="Generate Test Cases", command=self.generate_test_cases).grid(row=1, column=0, pady=10)

        # Result area
        result_frame = ttk.LabelFrame(self, text="Generated Test Cases")
        result_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        result_frame.columnconfigure(0, weight=1)
        result_frame.rowconfigure(0, weight=1)

        self.result_text = CustomText(result_frame, wrap=tk.WORD)
        self.result_text.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(result_frame, orient="vertical", command=self.result_text.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.result_text.configure(yscrollcommand=scrollbar.set)

    def generate_test_cases(self):
        data = [item.strip() for item in self.data_entry.get().split(",") if item.strip()]
        num_steps_str = self.steps_entry.get()

        if not data:
            messagebox.showerror("Error", "Data cannot be empty.")
            return
        if not num_steps_str.isdigit():
            messagebox.showerror("Error", "Number of steps must be a positive integer.")
            return
        
        num_steps = int(num_steps_str)
        if num_steps < 1:
            messagebox.showerror("Error", "Number of steps must be at least 1.")
            return
        if num_steps > len(data):
            messagebox.showerror("Error", "Number of steps cannot be greater than the number of data items.")
            return

        result = self.generate_test_cases_helper(data, num_steps)
        self.result_text.delete("1.0", tk.END)
        self.result_text.insert(tk.END, result)

    def generate_test_cases_helper(self, data_list, num_steps):
        try:
            test_cases = set(permutations(data_list, num_steps))
            return "\n".join(f"Test Case {i+1}: {' -> '.join(case)}" for i, case in enumerate(test_cases))
        except ValueError as e:
            return str(e)