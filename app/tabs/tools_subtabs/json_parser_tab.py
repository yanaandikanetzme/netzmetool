# app/tabs/tools_subtabs/parser_tab.py
import tkinter as tk
from tkinter import ttk
from src.jsonParser import jsonParser
from src.xmlParser import xmlParser
from app.custom.custom_text import CustomText

class ParserTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.create_widgets()

    def create_widgets(self):
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        # Input section
        input_frame = ttk.LabelFrame(self, text="Input", padding="10 10 10 10")
        input_frame.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)

        self.input_text = CustomText(input_frame, wrap=tk.WORD, width=80, height=15)
        self.input_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        input_scrollbar = ttk.Scrollbar(input_frame, orient="vertical", command=self.input_text.yview)
        input_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.input_text.configure(yscrollcommand=input_scrollbar.set)

        # Button frame
        button_frame = ttk.Frame(self)
        button_frame.grid(row=0, column=2, sticky="ns", padx=10, pady=10)

        ttk.Button(button_frame, text="JSON Beautify", command=self.json_beautify).pack(fill=tk.X, pady=(0, 5))
        ttk.Button(button_frame, text="JSON Minify", command=self.json_minify).pack(fill=tk.X, pady=(0, 5))
        ttk.Button(button_frame, text="XML Beautify", command=self.xml_beautify).pack(fill=tk.X, pady=(0, 5))
        ttk.Button(button_frame, text="XML Minify", command=self.xml_minify).pack(fill=tk.X)

        # Output section
        output_frame = ttk.LabelFrame(self, text="Output", padding="10 10 10 10")
        output_frame.grid(row=1, column=0, columnspan=3, sticky="nsew", padx=10, pady=10)

        self.output_text = CustomText(output_frame, wrap=tk.WORD, width=80, height=15, state='disabled')
        self.output_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        output_scrollbar = ttk.Scrollbar(output_frame, orient="vertical", command=self.output_text.yview)
        output_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.output_text.configure(yscrollcommand=output_scrollbar.set)

    def json_beautify(self):
        self.process_input(jsonParser.jsonParserBeautify)

    def json_minify(self):
        self.process_input(jsonParser.jsonParserMinify)

    def xml_beautify(self):
        self.process_input(xmlParser.xmlParserBeautify)

    def xml_minify(self):
        self.process_input(xmlParser.xmlParserMinify)

    def process_input(self, parser_function):
        input_text = self.input_text.get("1.0", 'end-1c')
        try:
            processed_text = parser_function(input_text)
            self.set_output(processed_text)
        except Exception as e:
            self.set_output(f"Error processing input: {str(e)}")

    def set_output(self, text):
        self.output_text.config(state='normal')
        self.output_text.delete('1.0', tk.END)
        self.output_text.insert(tk.END, text)
        self.output_text.config(state='disabled')