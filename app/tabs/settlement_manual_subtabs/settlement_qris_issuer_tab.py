# app/tabs/settlement_manual_subtabs/settlement_qris_issuer_tab.py
import tkinter as tk
from tkinter import ttk
from app.custom.custom_text import CustomText
from app.custom.custom_treeview import CustomTreeview
from src.modules import Modules
from src.jsonParser import jsonParser
from app.tabs.popup import ResponseOpenAPI
import json
import threading

class SettlementQRISIssuerTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.create_widgets()

    def create_widgets(self):
        # Main container
        main_container = ttk.Frame(self)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Left panel
        left_panel = ttk.Frame(main_container)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        # Right panel
        right_panel = ttk.Frame(main_container)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))

        self.create_left_panel(left_panel)
        self.create_right_panel(right_panel)

    def create_left_panel(self, parent):
        # Load data button
        self.load_button = ttk.Button(parent, text="Load Data", command=self.load_data)
        self.load_button.pack(fill=tk.X, pady=(0, 10))

        # Transactions treeview
        columns = ('ref_id', 'user_id', 'amount_value', 'request_body', 'qris_type', 'ts')
        self.transactions_tree = CustomTreeview(parent, columns=columns, show='headings')
        self.transactions_tree.pack(fill=tk.BOTH, expand=True)

        for col in columns:
            self.transactions_tree.heading(col, text=col)
            self.transactions_tree.column(col, width=100)

        self.transactions_tree.column('ref_id', width=200)
        self.transactions_tree.column('request_body', width=150)
        self.transactions_tree.column('ts', width=150)

        # Add to settlement button
        self.add_button = ttk.Button(parent, text="Add to Settlement", command=self.add_to_settlement)
        self.add_button.pack(fill=tk.X, pady=(10, 0))
        self.add_button.state(['disabled'])

    def create_right_panel(self, parent):
        # Settlement treeview
        columns = ('ref_id', 'user_id', 'amount_value', 'request_body', 'qris_type', 'ts')
        self.settlement_tree = CustomTreeview(parent, columns=columns, show='headings')
        self.settlement_tree.pack(fill=tk.BOTH, expand=True)

        for col in columns:
            self.settlement_tree.heading(col, text=col)
            self.settlement_tree.column(col, width=100)

        self.settlement_tree.column('ref_id', width=200)
        self.settlement_tree.column('request_body', width=150)
        self.settlement_tree.column('ts', width=150)

        # Settlement body
        self.settlement_body = CustomText(parent, height=10)
        self.settlement_body.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

        # Settle button
        self.settle_button = ttk.Button(parent, text="Settle", command=self.settle)
        self.settle_button.pack(fill=tk.X, pady=(10, 0))
        self.settle_button.state(['disabled'])

    def load_data(self):
        self.load_button.state(['disabled'])
        threading.Thread(target=self._load_data).start()

    def _load_data(self):
        try:
            query = "SELECT qp.rrn_payment, qp.username, qp.amount_value, qp.request_body, qp.qris_type, qp.ts FROM qris_payment qp WHERE qp.status = 'success' AND is_refund = false AND qp.request_body ->> 'acquirerId' != '93600814' ORDER BY qp.ts DESC LIMIT 50;"
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
            selected_items = self.transactions_tree.selection()
            if not selected_items:
                raise ValueError("Please select items to add to settlement.")

            for item in selected_items:
                values = self.transactions_tree.item(item)['values']
                self.transactions_tree.delete(item)
                self.settlement_tree.insert('', tk.END, values=values)

            self.update_settlement_body()
            self.settle_button.state(['!disabled'])
        except Exception as e:
            ResponseOpenAPI(str(e))

    def update_settlement_body(self):
        list_data = []
        for item in self.settlement_tree.get_children():
            values = self.settlement_tree.item(item)['values']
            ref_id = values[0]
            amount = values[2]
            request_body = json.loads(values[3].replace("'", '"'))
            pan = request_body['pan']

            # Pad ref_id to 12 or 28 digits
            ref_id_length = len(str(ref_id))
            if ref_id_length < 12:
                ref_id = f"{ref_id:0>12}"
            elif ref_id_length > 12:
                ref_id = f"{ref_id:0>28}"

            list_data.append({
                "refId": str(ref_id),
                "pan": str(pan),
                "nominal": str(amount)
            })

        body = {"listData": list_data}
        self.settlement_body.delete('1.0', tk.END)
        self.settlement_body.insert(tk.END, json.dumps(body, indent=2))

    def settle(self):
        try:
            url = 'https://tokoapi-stg.netzme.com/api/merchant/qr/qris/settlement/off/us/issuer'
            headers = {"Authorization": 'Basic a2FyZTpkZGUyOGM3ZWRiOWQ4MDQ2OTcyYzVjMzI3N2Q5OTlhMg=='}
            body = json.loads(self.settlement_body.get("1.0", 'end-1c'))

            response = Modules.POSThttpHeaders(url, headers, body)
            ResponseOpenAPI(json.dumps(response, indent=4))
        except Exception as e:
            ResponseOpenAPI(str(e))