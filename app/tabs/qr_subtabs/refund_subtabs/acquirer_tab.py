# app/tabs/qr_subtabs/refund_subtabs/acquirer_tab.py
from tkinter import *
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from src.modules import Modules
from app.tabs.popup import ResponseOpenAPI
from app.custom.custom_text import CustomText
from src.jsonParser import jsonParser
import platform
import yaml
import ast
import json
from app.custom.custom_treeview import CustomTreeview
import threading

class AcquirerTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.create_layout()
        self.create_widgets()
        self.place_widgets()

    def create_layout(self):
        self.left_frame = tk.Frame(self)
        self.right_frame = tk.Frame(self)
        
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

    def create_widgets(self):
        self.create_treeview()
        self.create_buttons()
        self.create_text_area()
        self.create_hmac_entry()

    def place_widgets(self):
        # Left frame
        self.MtreeRefundAcquirer.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        button_frame = tk.Frame(self.left_frame)
        button_frame.pack(fill=tk.X)
        self.LoadRefundAcquirerbutton1.pack(side=tk.LEFT, padx=(0, 5))
        self.HitRefundAcquirerButton1.pack(side=tk.LEFT)

        # Right frame
        self.textbodyQrisRefundAcquirer.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        hmac_frame = tk.Frame(self.right_frame)
        hmac_frame.pack(fill=tk.X)
        tk.Label(hmac_frame, text="HMAC:").pack(side=tk.LEFT, padx=(0, 5))
        self.shamacQRISRefundAcquirer.pack(side=tk.LEFT, fill=tk.X, expand=True)

    def create_treeview(self):
        columns = ('ref_id', 'rrn_origin', 'trx_id', 'amount_value', 'merchant_id', 'ts')
        self.MtreeRefundAcquirer = CustomTreeview(self.left_frame, columns=columns, show='headings')
        self.setup_treeview(columns)

    def setup_treeview(self, columns):
        column_widths = {
            'ref_id': 250, 'rrn_origin': 120, 'trx_id': 100,
            'amount_value': 100, 'merchant_id': 100, 'ts': 250
        }
        for column in columns:
            self.MtreeRefundAcquirer.heading(column, text=column)
            self.MtreeRefundAcquirer.column(column, width=column_widths[column], minwidth=150, anchor=tk.W)

        self.MtreeRefundAcquirer.bind("<<TreeviewSelect>>", self.getPayloadQRISAcquirerRefund)

    def create_buttons(self):
        self.LoadRefundAcquirerbutton1 = ttk.Button(self.left_frame, text="Load QR Payment", command=self.start_thread_connection, width=15)
        self.HitRefundAcquirerButton1 = ttk.Button(self.left_frame, text="Refund QR Payment", command=self.HitRefundAcquirer, state='disabled', width=15)

    def create_text_area(self):
        self.textbodyQrisRefundAcquirer = CustomText(self.right_frame, width=60, height=20)
        self.textbodyQrisRefundAcquirer.bind("<<TextModified>>", self.generateHMACQRISRefundAcquirer)

    def create_hmac_entry(self):
        self.shamacQRISRefundAcquirer = tk.Entry(self.right_frame, width=60)

    def start_thread_connection(self):
        self.LoadRefundAcquirerbutton1.config(state=tk.DISABLED)
        thread = threading.Thread(target=self.onLoadRefundAcquirer)
        thread.start()

    def onLoadRefundAcquirer(self):
        try:
            query = """
            SELECT ref_id, rrn_origin, trx_id, amount_value, merchant_id, ts 
            FROM qr_merchant_transaction 
            WHERE refund_type IS NULL AND is_on_us = false 
            ORDER BY ts DESC LIMIT 50;
            """
            results = Modules.ConnectDBMerchant(query)

            self.MtreeRefundAcquirer.delete(*self.MtreeRefundAcquirer.get_children())
            for row in results:
                self.MtreeRefundAcquirer.insert('', tk.END, values=row)

            self.LoadRefundAcquirerbutton1.config(state=tk.NORMAL)
            self.HitRefundAcquirerButton1.config(state='normal')
        except Exception as e:
            ResponseOpenAPI(str(e))

    def getPayloadQRISAcquirerRefund(self, event=None):
        try:
            selected_item = self.MtreeRefundAcquirer.selection()[0]
            values = self.MtreeRefundAcquirer.item(selected_item)['values']
            
            payload = {
                "body": {
                    "amount": f"IDR {values[3]}",
                    "merchantId": values[4],
                    "transactionId": values[2]
                },
                "requestId": Modules.generateUUID(),
                "requestTime": None,
                "type": "refund_qris"
            }

            formatted_payload = jsonParser.jsonParserBeautify(json.dumps(payload))
            self.textbodyQrisRefundAcquirer.delete('1.0', tk.END)
            self.textbodyQrisRefundAcquirer.insert(tk.END, formatted_payload)
        except IndexError:
            pass

    def HitRefundAcquirer(self):
        try:
            payload = json.loads(self.textbodyQrisRefundAcquirer.get("1.0", 'end-1c'))
            url = 'https://tokoapi-stg.netzme.com/api/merchant/qr/refund'
            headers = {
                "Content-Type": "application/json",
                "Authorization": 'Basic dG9rb2thcmU6YzRmOTZiZmRhOGQ5ZDVhMDgxNmU1MWE5M2JkZWNjNWU='
            }
            response = Modules.make_http_request(url=url, headers=headers, body_request=payload)
            if response:
                status_code, message = response
                formatted_message = jsonParser.jsonParserBeautify(message)
                ResponseOpenAPI(f"HTTP Status Code: {status_code}\nResponse Message: {formatted_message}")
        except IndexError:
            messagebox.showinfo('Response', 'Please select data first')

    def generateHMACQRISRefundAcquirer(self, event=None):
        try:
            with open("config/config.yaml", "r") as yamlfile:
                data = yaml.safe_load(yamlfile)
                key = data[0]['Details']['QRIS']['KeyCrossBorder']
                
            payload = self.textbodyQrisRefundAcquirer.get("1.0", "end-1c")
            hash_value = Modules.HashSHA256(payload, key).upper()
            
            self.shamacQRISRefundAcquirer.delete(0, tk.END)
            self.shamacQRISRefundAcquirer.insert(tk.END, hash_value)
        except Exception:
            pass