# app/tabs/settlement_manual_subtabs/settlement_invoice_tab.py
import tkinter as tk
from tkinter import ttk
from app.custom.custom_text import CustomText
from app.custom.custom_treeview import CustomTreeview
from src.modules import Modules
from src.jsonParser import jsonParser
from app.tabs.popup import ResponseOpenAPI
import json
import threading

class SettlementInvoiceTab(tk.Frame):
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
        # Payment method selection
        method_frame = ttk.Frame(parent)
        method_frame.pack(fill=tk.X, pady=(0, 10))

        tk.Label(method_frame, text="Payment Method:").pack(side=tk.LEFT)
        self.payment_method = ttk.Combobox(method_frame, values=[
            'xendit_transfer_bank', 'xendit_retail_outlet', 'xendit_cc', 
            'xendit_va', 'dki', 'settlement_indomaret'
        ], state="readonly")
        self.payment_method.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        self.payment_method.set('xendit_transfer_bank')
        self.payment_method.bind("<<ComboboxSelected>>", self.load_data)

        # Load data button
        self.load_button = ttk.Button(parent, text="Load Data", command=self.load_data)
        self.load_button.pack(fill=tk.X, pady=(0, 10))

        # Transactions treeview
        columns = ('invoice_transaction_id', 'invoice_id', 'merchant_id', 'payment_method', 'amount', 'created_ts')
        self.transactions_tree = CustomTreeview(parent, columns=columns, show='headings')
        self.transactions_tree.pack(fill=tk.BOTH, expand=True)

        for col in columns:
            self.transactions_tree.heading(col, text=col)
            self.transactions_tree.column(col, width=100)

        self.transactions_tree.column('invoice_transaction_id', width=200)
        self.transactions_tree.column('invoice_id', width=200)
        self.transactions_tree.column('created_ts', width=150)

        # Add to settlement button
        self.add_button = ttk.Button(parent, text="Add to Settlement", command=self.add_to_settlement)
        self.add_button.pack(fill=tk.X, pady=(10, 0))
        self.add_button.state(['disabled'])

    def create_right_panel(self, parent):
        # Settlement treeview
        columns = ('invoice_transaction_id', 'invoice_id', 'merchant_id', 'payment_method', 'amount', 'created_ts')
        self.settlement_tree = CustomTreeview(parent, columns=columns, show='headings')
        self.settlement_tree.pack(fill=tk.BOTH, expand=True)

        for col in columns:
            self.settlement_tree.heading(col, text=col)
            self.settlement_tree.column(col, width=100)

        self.settlement_tree.column('invoice_transaction_id', width=200)
        self.settlement_tree.column('invoice_id', width=200)
        self.settlement_tree.column('created_ts', width=150)

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
            method = self.payment_method.get()
            query = self.get_query_for_method(method)
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

    def get_query_for_method(self, method):
        queries = {
            'xendit_transfer_bank': "SELECT mit.invoice_transaction_id, mit.invoice_id, mit.merchant_id, mit.payment_method, mit.total_amount, mit.created_ts FROM merchant_invoice_transaction mit LEFT JOIN merchant_invoice mi ON mi.invoice_id = mit.invoice_id WHERE mit.payment_method IN ('BANK_TRANSFER') AND mit.status NOT IN ('expired','waiting') AND mit.settlement_id IS NULL AND mi.api_source IS NULL ORDER BY mit.created_ts DESC LIMIT 500;",
            'xendit_retail_outlet': "SELECT mit.invoice_transaction_id, mit.invoice_id, mit.merchant_id, mit.payment_method, mit.total_amount, mit.created_ts FROM merchant_invoice_transaction mit WHERE mit.payment_method IN ('RETAIL_OUTLET') AND mit.status NOT IN ('expired','waiting') AND payment_method NOT IN ('QRIS') AND settlement_id IS NULL ORDER BY mit.created_ts DESC LIMIT 500;",
            'xendit_cc': "SELECT mit.invoice_transaction_id, mit.invoice_id, mit.merchant_id, mit.payment_method, mit.total_amount, mit.created_ts FROM merchant_invoice_transaction mit WHERE mit.payment_method IN ('CREDIT_CARD') AND mit.status NOT IN ('expired','waiting') AND payment_method NOT IN ('QRIS') AND settlement_id IS NULL ORDER BY mit.created_ts DESC LIMIT 500;",
            'xendit_va': "SELECT mit.invoice_transaction_id, mit.invoice_id, mit.merchant_id, mit.payment_method, mit.total_amount, mit.created_ts FROM merchant_invoice_transaction mit WHERE mit.payment_method IN ('VA_BCA','VA_CIMB','VA_BRI','VA_BNI','VA_MANDIRI','VA_PERMATA') AND mit.status NOT IN ('expired','waiting') AND payment_method NOT IN ('QRIS') AND settlement_id IS NULL ORDER BY mit.created_ts DESC LIMIT 500;",
            'dki': "SELECT mit.invoice_transaction_id, mit.invoice_id, mit.merchant_id, mit.payment_method, mit.total_amount, mit.created_ts FROM merchant_invoice_transaction mit WHERE mit.payment_method IN ('DKI') AND mit.status NOT IN ('expired','waiting') AND payment_method NOT IN ('QRIS') AND settlement_id IS NULL ORDER BY mit.created_ts DESC LIMIT 500;",
            'settlement_indomaret': "SELECT mit.invoice_transaction_id, mit.response_payment_code, mit.merchant_id, mit.vendor_id AS trx_id, mit.total_amount, mit.created_ts FROM merchant_invoice_transaction mit WHERE 1=1 AND mit.payment_method = 'INDOMARET' AND settlement_id IS NULL AND status = 'paid' ORDER BY created_ts DESC LIMIT 50;"
        }
        return queries.get(method, "")

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
        method = self.payment_method.get()
        settlement_date = Modules.generate_date()
        request_id = Modules.generateUUID()

        if method == 'settlement_indomaret':
            trx_list = []
            for item in self.settlement_tree.get_children():
                values = self.settlement_tree.item(item)['values']
                trx_list.append({
                    "trxId": values[3],
                    "externalId": values[0],
                    "amount": str(values[4]),
                    "paymentCode": values[1],
                    "paidDate": Modules.replaceDateToTZ(values[5])
                })
            body = {
                "requestId": Modules.RandomDigit(9),
                "type": method,
                "body": {
                    "settlementDate": settlement_date,
                    "trxList": trx_list
                }
            }
        else:
            trx_id_list = [self.settlement_tree.item(item)['values'][0] for item in self.settlement_tree.get_children()]
            body = {
                "requestId": request_id,
                "requestTime": None,
                "type": "settlement",
                "body": {
                    "settlementType": method,
                    "settlementDate": settlement_date,
                    "trxIdList": trx_id_list
                }
            }

        self.settlement_body.delete('1.0', tk.END)
        self.settlement_body.insert(tk.END, json.dumps(body, indent=2))

    def settle(self):
        try:
            method = self.payment_method.get()
            url = 'https://tokoapi-stg.netzme.com/api/merchant/invoice/settlement/bit-dna/payment-page' if method == 'settlement_indomaret' else 'https://tokoapi-stg.netzme.com/api/merchant/invoice/settlement/manual'
            
            headers = {"Authorization": 'Basic a2FyZTpkZGUyOGM3ZWRiOWQ4MDQ2OTcyYzVjMzI3N2Q5OTlhMg=='}
            body = json.loads(self.settlement_body.get("1.0", 'end-1c'))
            
            response = Modules.make_http_request(url=url, headers=headers, body_request=body)
            if response:
                http_status_code, response_message = response
                ResponseOpenAPI(f"HTTP Status Code: {http_status_code}\nResponse Message: {jsonParser.jsonParserBeautify(response_message)}")
        except Exception as e:
            ResponseOpenAPI(str(e))