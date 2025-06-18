# app/tabs/qr_subtabs/refund_subtabs/issuer_tab.py
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

class IssuerTab(tk.Frame):
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
        self.MtreeRefundIssuer.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        button_frame = tk.Frame(self.left_frame)
        button_frame.pack(fill=tk.X)
        self.LoadRefundIssuerbutton1.pack(side=tk.LEFT, padx=(0, 5))
        self.HitRefundIssuerButton1.pack(side=tk.LEFT)

        # Right frame
        self.textbodyQrisRefundIssuer.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        hmac_frame = tk.Frame(self.right_frame)
        hmac_frame.pack(fill=tk.X)
        tk.Label(hmac_frame, text="HMAC:").pack(side=tk.LEFT, padx=(0, 5))
        self.shamacQRISRefundIssuer.pack(side=tk.LEFT, fill=tk.X, expand=True)

    def create_treeview(self):
        columns = ('ref_id', 'username', 'amount_value', 'status', 'ts', 'invoice_number', 'trace_rrn', 'rrn_payment', 'request_body', 'qris_type')
        self.MtreeRefundIssuer = CustomTreeview(self.left_frame, columns=columns, show='headings')
        self.setup_treeview(columns)

    def setup_treeview(self, columns):
        column_widths = {
            'ref_id': 100, 'username': 50, 'amount_value': 50, 'status': 30, 'ts': 100,
            'invoice_number': 90, 'trace_rrn': 90, 'rrn_payment': 90, 'request_body': 150, 'qris_type': 150
        }
        for column in columns:
            self.MtreeRefundIssuer.heading(column, text=column)
            self.MtreeRefundIssuer.column(column, width=column_widths[column], minwidth=150, anchor=tk.W)

        self.MtreeRefundIssuer.bind("<<TreeviewSelect>>", self.getPayloadQRISIssuerRefund)

    def create_buttons(self):
        self.LoadRefundIssuerbutton1 = ttk.Button(self.left_frame, text="Load QR Payment", command=self.start_thread_connection, width=15)
        self.HitRefundIssuerButton1 = ttk.Button(self.left_frame, text="Refund QR Payment", command=self.HitRefundIssuer, state='disabled', width=15)

    def create_text_area(self):
        self.textbodyQrisRefundIssuer = CustomText(self.right_frame, width=60, height=20)
        self.textbodyQrisRefundIssuer.bind("<<TextModified>>", self.generateHMACQRISRefundIssuer)

    def create_hmac_entry(self):
        self.shamacQRISRefundIssuer = tk.Entry(self.right_frame, width=60)

    def start_thread_connection(self):
        self.LoadRefundIssuerbutton1.config(state=tk.DISABLED)
        thread = threading.Thread(target=self.onLoadRefundIssuer)
        thread.start()

    def onLoadRefundIssuer(self):
        try:
            query = """
            SELECT ref_id, username, amount_value, status, ts, invoice_number, trace_rrn, rrn_payment, request_body, qris_type 
            FROM qris_payment 
            WHERE status NOT IN ('suspend', 'failed', 'settle') AND is_refund = 'false' 
            ORDER BY ts DESC LIMIT 500;
            """
            results = Modules.ConnectDBMerchant(query)

            self.MtreeRefundIssuer.delete(*self.MtreeRefundIssuer.get_children())
            for row in results:
                self.MtreeRefundIssuer.insert('', tk.END, values=row)

            self.LoadRefundIssuerbutton1.config(state=tk.NORMAL)
            self.HitRefundIssuerButton1.config(state='normal')
        except Exception as e:
            ResponseOpenAPI(str(e))

    def getPayloadQRISIssuerRefund(self, event=None):
        try:
            selected_item = self.MtreeRefundIssuer.selection()[0]
            values = self.MtreeRefundIssuer.item(selected_item)['values']
            qris_type = values[9]
            
            request_body = ast.literal_eval(values[8])
            rrn = Modules.RandomDigit(12)
            
            payload = self.create_payload(qris_type, values, request_body, rrn)
            
            formatted_payload = jsonParser.jsonParserBeautify(json.dumps(payload))
            self.textbodyQrisRefundIssuer.delete('1.0', tk.END)
            self.textbodyQrisRefundIssuer.insert(tk.END, formatted_payload)
        except IndexError:
            pass

    def create_payload(self, qris_type, values, request_body, rrn):
        common_payload = {
            "pan": request_body['customerPan'],
            "processingCode": "200000",
            "transactionAmount": request_body['transactionAmount'],
            "transmissionDateTime": request_body['transmissionDateTime'],
            "systemTraceAuditNumber": request_body['systemTraceAuditNumber'],
            "localTransactionDateTime": request_body['localTransactionDateTime'],
            "settlementDate": request_body['settlementDate'],
            "captureDate": request_body['captureDate'],
            "merchantType": request_body['merchantType'],
            "posEntryMode": request_body['posEntryMode'],
            "acquirerId": request_body['acquirerId'],
            "issuerId": request_body['issuerId'],
            "forwardingId": request_body['forwardingId'],
            "rrn": rrn,
            "terminalId": request_body['terminalId'],
            "merchantId": request_body['merchantId'],
            "merchantName": request_body['merchantName'],
            "merchantCity": request_body['merchantCity'],
            "merchantCountry": request_body['merchantCountry'],
            "productIndicator": request_body['productIndicator'],
            "customerData": request_body['customerData'],
            "merchantCriteria": request_body['merchantCriteria'],
            "currencyCode": request_body['currencyCode'],
            "merchantPan": request_body['pan']
        }

        if qris_type == 'qris_cb_payment':
            inv_num = str(int(values[5])).rjust(10, '0') * 2
            common_payload.update({
                "msgId": request_body['msgId'],
                "settlementAmount": request_body['settlementAmount'],
                "cardholderAmount": request_body['cardholderAmount'],
                "settlementRate": request_body['settlementRate'],
                "cardholderRate": request_body['cardholderRate'],
                "feeType": request_body['feeType'],
                "feeAmount": request_body['feeAmount'],
                "settlementCurrCode": request_body['settlementCurrCode'],
                "cardholderCurrCode": request_body['cardholderCurrCode'],
                "invoiceNumber": inv_num
            })
        else:
            inv_num = str(int(values[5])).rjust(10, '0') + str(values[6]).rjust(10, '0')
            common_payload.update({
                "feeType": "C",
                "feeAmount": "0.00",
                "invoiceNumber": inv_num
            })

        return common_payload

    def HitRefundIssuer(self):
        try:
            with open("config/config.yaml", "r") as yamlfile:
                config = yaml.safe_load(yamlfile)

            payload = json.loads(self.textbodyQrisRefundIssuer.get("1.0", 'end-1c'))
            selected_item = self.MtreeRefundIssuer.selection()[0]
            qris_type = self.MtreeRefundIssuer.item(selected_item)['values'][9]

            if qris_type == 'qris_cb_payment':
                key = config[0]['Details']['QRIS']['KeyCrossBorder']
                url = 'https://tokoapi-stg.netzme.com/qr/cb/refund?username=netzme&password=netzme123'
                response = Modules.POSThttpHeadersQRIS(url, payload, key)
            else:
                url = 'https://tokoapi-stg.netzme.com/qr/refund'
                response = Modules.POSThttpHeadersWithoutHeaders(url, payload)

            messagebox.showinfo('Response', str(response))
        except IndexError:
            messagebox.showinfo('Response', 'Please select data first')
        except Exception as e:
            messagebox.showerror('Error', str(e))

    def generateHMACQRISRefundIssuer(self, event=None):
        try:
            with open("config/config.yaml", "r") as yamlfile:
                config = yaml.safe_load(yamlfile)
            
            selected_item = self.MtreeRefundIssuer.selection()[0]
            qris_type = self.MtreeRefundIssuer.item(selected_item)['values'][9]

            key = config[0]['Details']['QRIS']['KeyCrossBorder' if qris_type == 'qris_cb_payment' else 'KeyDomestik']
            
            payload = self.textbodyQrisRefundIssuer.get("1.0", "end-1c")
            hash_value = Modules.HashSHA256(payload, key).upper()
            
            self.shamacQRISRefundIssuer.delete(0, tk.END)
            self.shamacQRISRefundIssuer.insert(tk.END, hash_value)
        except Exception:
            pass