# app/tabs/tools_subtabs/generator_tab.py
import tkinter as tk
from tkinter import ttk
import json
import threading
from src.modules import Modules
from app.custom.custom_text import CustomText
from app.tabs.popup import ResponseOpenAPI
from src.jsonParser import jsonParser

class HitCurl(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding="20")
        self.create_widgets()

    def create_widgets(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # Input frame
        input_frame = ttk.LabelFrame(self, text="cURL Input", padding="10")
        input_frame.grid(row=0, column=0, sticky="nsew")
        input_frame.columnconfigure(0, weight=1)
        input_frame.rowconfigure(0, weight=1)

        self.curl_input = CustomText(input_frame, width=80, height=20, wrap="word")
        self.curl_input.grid(row=0, column=0, sticky="nsew")

        input_scrollbar = ttk.Scrollbar(input_frame, orient="vertical", command=self.curl_input.yview)
        input_scrollbar.grid(row=0, column=1, sticky="ns")
        self.curl_input.configure(yscrollcommand=input_scrollbar.set)

        # Button frame
        button_frame = ttk.Frame(self, padding="10 10 0 0")
        button_frame.grid(row=1, column=0, sticky="e")

        self.send_button = ttk.Button(button_frame, text='Send Request', command=self.start_thread_connection)
        self.send_button.pack()

    def start_thread_connection(self):
        self.send_button.config(state=tk.DISABLED)
        thread = threading.Thread(target=self.hit_curl_request)
        thread.start()

    def hit_curl_request(self):
        try:
            curl_text = self.curl_input.get("1.0", 'end-1c')
            response = Modules.run_curl(curl_text)

            if response:
                if isinstance(response, list) and len(response) == 2:
                    http_status_code, response_message = response
                else:
                    http_status_code, response_message = None, str(response)

                try:
                    if isinstance(response_message, (dict, list)):
                        response_message = json.dumps(response_message, indent=2)
                        response_message = jsonParser.jsonParserBeautify(response_message)
                    else:
                        response_message = str(response_message)
                except Exception as e:
                    print(f"Error parsing response: {e}")
                    response_message = str(response_message)

                if http_status_code is None:
                    msgbox = f"Response:\n{response_message}"
                else:
                    msgbox = f"HTTP Status Code: {http_status_code}\nResponse Message:\n{response_message}"

                self.show_response(msgbox)
        finally:
            self.send_button.config(state=tk.NORMAL)

    def show_response(self, message):
        ResponseOpenAPI(message, self.master)