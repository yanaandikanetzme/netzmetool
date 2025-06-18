# app/tabs/tools_subtabs/hash_tab.py
import tkinter as tk
from tkinter import ttk
from app.custom.custom_text import CustomText
from src.modules import Modules

class HashTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.create_widgets()

    def create_widgets(self):
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=3)
        self.rowconfigure(1, weight=1)

        # Input section
        input_frame = ttk.LabelFrame(self, text="Input", padding="10 10 10 10")
        input_frame.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)

        self.input_text = CustomText(input_frame, height=10, width=80)
        self.input_text.pack(fill=tk.BOTH, expand=True)
        self.input_text.bind("<<TextModified>>", self.update_output)

        # Mode selection
        mode_frame = ttk.Frame(self)
        mode_frame.grid(row=1, column=0, sticky="nw", padx=10, pady=10)

        tk.Label(mode_frame, text="Algorithm:").pack(side=tk.LEFT)
        self.algo_var = tk.StringVar(value="base64")
        self.algo_combo = ttk.Combobox(mode_frame, textvariable=self.algo_var, 
                                    values=['base64', 'MD5', 'SHA1', 'SHA256', 'SHA512', 'AES128'], 
                                    state="readonly", width=15)
        self.algo_combo.pack(side=tk.LEFT, padx=(5, 0))
        self.algo_combo.bind("<<ComboboxSelected>>", self.update_mode_visibility)

        tk.Label(mode_frame, text="Operation:").pack(side=tk.LEFT, padx=(10, 0))
        self.operation_var = tk.StringVar(value="encode")
        self.operation_combo = ttk.Combobox(mode_frame, textvariable=self.operation_var, 
                                            values=['encode', 'decode'], 
                                            state="readonly", width=15)
        self.operation_combo.pack(side=tk.LEFT, padx=(5, 0))
        self.operation_combo.bind("<<ComboboxSelected>>", self.update_output)

        # Key selection
        tk.Label(mode_frame, text="Key:").pack(side=tk.LEFT, padx=(10, 0))
        self.key_var = tk.StringVar(value="without key")
        self.key_combo = ttk.Combobox(mode_frame, textvariable=self.key_var, 
                                    values=['with key', 'without key'], 
                                    state="readonly", width=15)
        self.key_combo.pack(side=tk.LEFT, padx=(5, 0))
        self.key_combo.bind("<<ComboboxSelected>>", self.update_mode_visibility)
        
        # Secret key input
        self.secret_frame = ttk.LabelFrame(self, text="Secret Key (optional)", padding="10 10 10 10")
        self.secret_frame.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)

        self.secret_text = CustomText(self.secret_frame, height=5, width=60)
        self.secret_text.pack(fill=tk.BOTH, expand=True)
        self.secret_text.bind("<<TextModified>>", self.update_output)

        # Output section
        output_frame = ttk.LabelFrame(self, text="Output", padding="10 10 10 10")
        output_frame.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)

        self.output_text = CustomText(output_frame, height=10, width=80, state='disabled')
        self.output_text.pack(fill=tk.BOTH, expand=True)

        self.update_mode_visibility()

    def update_mode_visibility(self, event=None):
        algo = self.algo_var.get()
        key_option = self.key_var.get()

        # Update secret frame visibility
        if algo in ['SHA256', 'SHA512', 'AES128'] and key_option == 'with key':
            self.secret_frame.grid()
        else:
            self.secret_frame.grid_remove()

        # Update key combo state
        if algo in ['SHA256', 'SHA512', 'AES128']:
            self.key_combo.config(state='readonly')
        else:
            self.key_var.set('without key')
            self.key_combo.config(state='disabled')

        # Update operation combo state
        if algo in ['MD5', 'SHA1', 'SHA256', 'SHA512']:
            self.operation_var.set('encode')
            self.operation_combo.config(state='disabled')
        else:
            self.operation_combo.config(state='readonly')

        # Update output without calling update_mode_visibility again
        self.update_output(skip_visibility_check=True)

    def update_output(self, event=None, skip_visibility_check=False):
        if not skip_visibility_check:
            self.update_mode_visibility()
            return

        input_string = self.input_text.get("1.0", 'end-1c').strip()
        
        if not input_string:
            self.set_output("Please fill the Input Text")
            return

        algo = self.algo_var.get()
        operation = self.operation_var.get()
        withkey = self.key_var.get()
        key = self.secret_text.get("1.0", 'end-1c').strip() if self.secret_frame.winfo_viewable() else None

        try:
            if algo == 'base64':
                result = Modules.base64Encode(input_string) if operation == 'encode' else Modules.base64Decode(input_string)
            elif algo == 'MD5':
                result = Modules.HashMD5(input_string)
            elif algo == 'SHA1':
                result = Modules.HashSHA1(input_string)
            elif algo in ('SHA256', 'SHA512', 'AES128'):
                if withkey == 'with key':
                    if algo == 'SHA256':
                        result = Modules.HashSHA256(input_string, key)
                    elif algo == 'SHA512':
                        result = Modules.HashSHA512(input_string, key)
                    elif algo == 'AES128':
                        if operation == 'encode':
                            result = Modules.AES128Encrypt(input_string, key)
                        else:
                            result = Modules.AES128Decrypt(input_string, key)
                else:
                    if algo == 'SHA256':
                        result = Modules.HashSHA256(input_string)
                    elif algo == 'SHA512':
                        result = Modules.HashSHA512(input_string)
                    elif algo == 'AES128':
                        if operation == 'encode':
                            result = Modules.AES128Encrypt(input_string)
                        else:
                            result = Modules.AES128Decrypt(input_string)
            else:
                result = "Invalid algorithm selected"
        except Exception as e:
            result = f"Error: {str(e)}"

        self.set_output(result)

    def set_output(self, text):
        self.output_text.config(state='normal')
        self.output_text.delete('1.0', tk.END)
        self.output_text.insert(tk.END, text)
        self.output_text.config(state='disabled')