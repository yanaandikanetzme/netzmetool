# app/tabs/settlement_manual_subtabs/settlement_qris_acquirer_tab.py
from tkinter import *
import tkinter as tk
from tkinter import ttk
from app.custom.custom_text import CustomText
from app.custom.custom_treeview import CustomTreeview
from src.modules import Modules
from app.tabs.popup import ResponseOpenAPI
import json
import threading

class SettlementQRISAcquirerTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.create_widgets()

    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Left frame
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        # Right frame
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))

        # Left frame contents
        self.create_left_frame(left_frame)

        # Right frame contents
        self.create_right_frame(right_frame)

    def create_left_frame(self, parent):
        # Vendor selection
        vendor_frame = ttk.Frame(parent)
        vendor_frame.pack(fill=tk.X, pady=(0, 10))

        tk.Label(vendor_frame, text="Vendor:").pack(side=tk.LEFT)
        self.vendor_combobox = ttk.Combobox(vendor_frame, values=['jalin', 'artajasa'], state="readonly")
        self.vendor_combobox.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        self.vendor_combobox.set('jalin')
        self.vendor_combobox.bind("<<ComboboxSelected>>", self.load_data)

        # Load data button
        self.load_button = ttk.Button(parent, text="Load Data", command=self.load_data)
        self.load_button.pack(fill=tk.X, pady=(0, 10))

        # Transactions treeview
        columns = ('ref_id', 'merchant_id', 'amount_value', 'qr_type', 'vendor_name', 'ts')
        self.transactions_tree = CustomTreeview(parent, columns=columns, show='headings')
        self.transactions_tree.pack(fill=tk.BOTH, expand=True)

        for col in columns:
            self.transactions_tree.heading(col, text=col)
            self.transactions_tree.column(col, width=100)

        self.transactions_tree.column('ref_id', width=200)
        self.transactions_tree.column('ts', width=150)

        # Add to settlement button
        self.add_button = ttk.Button(parent, text="Add to Settlement", command=self.add_to_settlement)
        self.add_button.pack(fill=tk.X, pady=(10, 0))
        self.add_button.state(['disabled'])

    def create_right_frame(self, parent):
        # Settlement treeview
        columns = ('ref_id', 'merchant_id', 'amount_value', 'qr_type', 'vendor_name', 'ts')
        self.settlement_tree = CustomTreeview(parent, columns=columns, show='headings')
        self.settlement_tree.pack(fill=tk.BOTH, expand=True)

        for col in columns:
            self.settlement_tree.heading(col, text=col)
            self.settlement_tree.column(col, width=100)

        self.settlement_tree.column('ref_id', width=200)
        self.settlement_tree.column('ts', width=150)

        # Settlement body
        self.settlement_body = CustomText(parent, height=10)
        self.settlement_body.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

        # Settle button
        self.settle_button = ttk.Button(parent, text="Settle", command=self.settle)
        self.settle_button.pack(fill=tk.X, pady=(10, 0))
        self.settle_button.state(['disabled'])

    def load_data(self, event=None):
        self.load_button.state(['disabled'])
        threading.Thread(target=self._load_data).start()

    def _load_data(self):
        try:
            vendor = self.vendor_combobox.get()
            query = f"SELECT ref_id, merchant_id, amount_value, qr_type, vendor_name, ts FROM qr_merchant_transaction WHERE is_refund = false AND is_on_us = false AND status NOT IN ('settlement') AND vendor_name = '{vendor}' ORDER BY ts DESC LIMIT 500;"
            
            results = Modules.ConnectDBMerchant(query)

            self.transactions_tree.delete(*self.transactions_tree.get_children())
            self.settlement_tree.delete(*self.settlement_tree.get_children())
            self.settlement_body.delete('1.0', tk.END)

            for row in results:
                self.transactions_tree.insert('', tk.END, values=row)

            self.add_button.state(['!disabled'])
        except Exception as e:
            ResponseOpenAPI(str(e))
        finally:
            self.load_button.state(['!disabled'])

    def add_to_settlement(self):
        try:
            selected_item = self.transactions_tree.selection()[0]
            values = self.transactions_tree.item(selected_item)['values']
            self.transactions_tree.delete(selected_item)
            self.settlement_tree.insert('', tk.END, values=values)

            self.update_settlement_body()
            self.settle_button.state(['!disabled'])
        except IndexError:
            ResponseOpenAPI("Please select an item to add to settlement.")

    def update_settlement_body(self):
        total_amount = 0
        list_data = []

        for item in self.settlement_tree.get_children():
            values = self.settlement_tree.item(item)['values']
            ref_id, amount = values[0], float(values[2])
            total_amount += amount
            list_data.append({"refId": ref_id, "nominal": str(amount)})

        body = {
            "requestId": Modules.generateUUID(),
            "totalAmount": total_amount,
            "period": Modules.generate_date(),
            "vendorName": self.vendor_combobox.get(),
            "listData": list_data
        }

        self.settlement_body.delete('1.0', tk.END)
        self.settlement_body.insert(tk.END, json.dumps(body, indent=2))

    def settle(self):
        try:
            url = 'https://tokoapi-stg.netzme.com/api/toko-settlement/settlement/qris/off-us'
            headers = {"Authorization": 'Basic a2FyZTpkZGUyOGM3ZWRiOWQ4MDQ2OTcyYzVjMzI3N2Q5OTlhMg=='}
            body = json.loads(self.settlement_body.get("1.0", 'end-1c'))

            response = Modules.make_http_request(url=url, headers=headers, body_request=body)
            if response:
                http_status_code, response_message = response
                ResponseOpenAPI(f"HTTP Status Code: {http_status_code}\nResponse Message: {response_message}")
        except Exception as e:
            ResponseOpenAPI(str(e))