# app/tabs/popup.py
import tkinter as tk
from tkinter import ttk
from tkinter import *
from tkinter.filedialog import askopenfile
import json
import webbrowser
from app.custom.custom_text import CustomText
from src.xmlParser import xmlParser
import xml.etree.ElementTree as ET

class ResponseOpenAPI(tk.Frame):
    def __init__(self, msg, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.create_window(msg)
        #print(f'Message: {msg}')

    def create_window(self, message):
        dialog = Toplevel(self.parent)
        dialog.wm_title("Response API")
        
        # Dynamically set the window size based on screen resolution
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        window_width = int(screen_width * 0.3)
        window_height = int(screen_height * 0.7)

        dialog.geometry(f"{window_width}x{window_height}")
        dialog.minsize(int(screen_width * 0.3), int(screen_height * 0.7))  # Set minimum size
        
        dialog.wm_transient(self.parent)
        dialog.wm_protocol("WM_DELETE_WINDOW", lambda: self.onDeleteChild(dialog))

        # Create main frame
        main_frame = tk.Frame(dialog)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Create Text element
        self.text = CustomText(main_frame, width=80, height=40)
        self.text.pack(fill=tk.BOTH, expand=True)
        
        # Format and insert the message
        formatted_message = self.format_message(message)
        self.text.insert(tk.END, formatted_message)

        # Create bottom frame
        bottom_frame = tk.Frame(main_frame)
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X)

        # Create Close Button
        close_button = ttk.Button(bottom_frame, text="Close", command=lambda: self.onDeleteChild(dialog))
        close_button.pack(side=tk.RIGHT, padx=10)

        # Create Label element
        self.label = tk.Label(bottom_frame, cursor="hand2")
        self.label.pack(side=tk.LEFT, padx=10)
        self.label.bind("<Button-1>", self.open_url)

        self.parse_message(message)

    def format_message(self, message):
        message_content = message.split("Response Message: ")[-1]
        
        # Cek apakah message_content adalah JSON
        try:
            data = json.loads(message_content)
            return json.dumps(data, indent=2)
        except json.JSONDecodeError:
            # Jika bukan JSON, coba sebagai XML
            try:
                root = ET.fromstring(message_content)
                return xmlParser.xmlParserBeautify(message_content)
            except ET.ParseError:
                # Jika bukan JSON dan bukan XML, kembalikan string asli
                return message_content

    def parse_message(self, message):
        payment_url = None
        message_content = message.split("Response Message: ")[-1]
        
        # Coba parsing sebagai JSON
        try:
            data = json.loads(message_content)
            if "result" in data and data["result"]:
                if "url" in data["result"]:
                    payment_url = data["result"]["url"]
                elif "paymentUrl" in data["result"]:
                    payment_url = data["result"]["paymentUrl"]
            elif "paymentUrl" in data:
                payment_url = data["paymentUrl"]
        except json.JSONDecodeError:
            # Jika bukan JSON, coba parsing sebagai XML
            try:
                root = ET.fromstring(message_content)
                payment_url = root.find('.//paymentUrl').text if root.find('.//paymentUrl') is not None else None
            except ET.ParseError:
                # Jika bukan JSON atau XML, tidak melakukan apa-apa
                pass

        if payment_url:
            self.label.config(text=payment_url)
            self.label.pack(side=tk.LEFT, padx=10)
        else:
            self.label.pack_forget()

    def onDeleteChild(self, w):
        w.destroy()

    def open_url(self, event):
        webbrowser.open_new(self.label.cget("text"))