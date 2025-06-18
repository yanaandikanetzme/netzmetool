# app/tabs/tools_subtabs/topup_netzme_subtabs/topup_agent_balance.py
import tkinter as tk
from tkinter import ttk, messagebox
from src.modules import Modules
from app.tabs.popup import ResponseOpenAPI
import json
from src.bni_agent_balance import hash_data
from app.custom.custom_text import CustomText
from app.custom.custom_treeview import CustomTreeview
from src.jsonParser import jsonParser
import threading

bni_client_id = '368'
bni_secret_key = 'e9731d356964eabe8396bf43166e77c2'

class TopupAgent(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.create_ui()

    def create_ui(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        # Agent Data Frame
        agent_frame = ttk.LabelFrame(self, text="Agent Data")
        agent_frame.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")
        agent_frame.columnconfigure(0, weight=1)
        agent_frame.rowconfigure(0, weight=1)

        columns = ('id', 'username', 'bank_code', 'account_number', 'account_holder_name', 'client_id')
        self.agent_tree = CustomTreeview(agent_frame, columns=columns, show='headings')
        self.agent_tree.grid(row=0, column=0, sticky="nsew")

        for col in columns:
            self.agent_tree.heading(col, text=col.replace('_', ' ').title())
            self.agent_tree.column(col, anchor=tk.W, width=100)

        self.agent_tree.column('id', width=260)
        self.agent_tree.column('username', width=120)
        self.agent_tree.column('account_number', width=140)
        self.agent_tree.column('account_holder_name', width=145)
        self.agent_tree.column('client_id', width=150)

        scrollbar = ttk.Scrollbar(agent_frame, orient="vertical", command=self.agent_tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.agent_tree.configure(yscrollcommand=scrollbar.set)

        self.agent_tree.bind("<<TreeviewSelect>>", self.generate_raw)

        # Amount Frame
        amount_frame = ttk.Frame(self)
        amount_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        amount_frame.columnconfigure(1, weight=1)

        tk.Label(amount_frame, text="Amount:").grid(row=0, column=0, padx=(0, 5))
        self.amount_entry = ttk.Entry(amount_frame)
        self.amount_entry.grid(row=0, column=1, sticky="ew")
        self.amount_entry.bind('<KeyRelease>', self.generate_raw)

        # Payload Frame
        payload_frame = ttk.LabelFrame(self, text="Payload")
        payload_frame.grid(row=2, column=0, padx=10, pady=5, sticky="nsew")
        payload_frame.columnconfigure(0, weight=1)
        payload_frame.columnconfigure(1, weight=1)
        payload_frame.rowconfigure(0, weight=1)

        self.raw_payload = CustomText(payload_frame, width=60, height=11)
        self.raw_payload.grid(row=0, column=0, padx=(0, 5), sticky="nsew")

        self.payload_topup = CustomText(payload_frame, width=60, height=11)
        self.payload_topup.grid(row=0, column=1, padx=(5, 0), sticky="nsew")

        # Button Frame
        button_frame = ttk.Frame(self)
        button_frame.grid(row=3, column=0, padx=10, pady=5, sticky="ew")
        button_frame.columnconfigure(1, weight=1)

        self.load_button = ttk.Button(button_frame, text="Load Data", command=self.start_thread_connection)
        self.load_button.grid(row=0, column=0, padx=(0, 5))

        self.topup_button = ttk.Button(button_frame, text="Top Up", command=self.topup_va_agent, state='disabled')
        self.topup_button.grid(row=0, column=2, padx=(5, 0))

    def start_thread_connection(self):
        self.load_button.config(state=tk.DISABLED)
        thread = threading.Thread(target=self.connectDBAgentVA)
        thread.start()

    def connectDBAgentVA(self):
        try:
            query = "SELECT id, username, bank_code, account_number, account_holder_name, client_id FROM merchant_deposit_virtual_accounts ORDER BY account_holder_name;"
            results = Modules.ConnectDBMerchant(query)
            self.topup_button.config(state='normal')

            self.agent_tree.delete(*self.agent_tree.get_children())
            for row in results:
                self.agent_tree.insert('', tk.END, values=row)
        except Exception as e:
            ResponseOpenAPI(str(e))
        finally:
            self.load_button.config(state=tk.NORMAL)

    def generate_raw(self, event=None):
        try:
            selected_item = self.agent_tree.selection()[0]
            values = self.agent_tree.item(selected_item)['values']

            date_now = Modules.get_current_date_topup()
            date_now_iso = Modules.getXtimestamp()
            amount = self.amount_entry.get()
            random_digit = Modules.RandomDigit(6)

            raw_payload = {
                "trx_id": values[0],
                "virtual_account": values[3],
                "customer_name": values[4],
                "payment_amount": amount,
                "cumulative_payment_amount": amount,
                "payment_ntb": random_digit,
                "datetime_payment": date_now,
                "datetime_payment_iso8601": date_now_iso
            }

            self.raw_payload.delete('1.0', tk.END)
            self.raw_payload.insert(tk.END, jsonParser.jsonParserBeautify(raw_payload))
            
            bni_encrypt = hash_data(jsonParser.jsonParserMinify(raw_payload), bni_client_id, bni_secret_key)
            payload_request = {"data": bni_encrypt, "client_id": bni_client_id}
            
            self.payload_topup.delete('1.0', tk.END)
            self.payload_topup.insert(tk.END, jsonParser.jsonParserBeautify(payload_request))
        except IndexError:
            messagebox.showinfo('Response', 'Please select an agent first')

    def topup_va_agent(self):
        try:
            url = "https://tokoapi-stg.netzme.com/bni/va/notif"
            headers = {
                "User-Agent": "BNI eCollection payment notification",
                "Content-Type": "application/json"
            }
            body = json.loads(self.payload_topup.get("1.0", 'end-1c'))
            
            response = Modules.POSThttpHeaders(url, headers, body)
            messagebox.showinfo('Response', str(response))
        except Exception as e:
            messagebox.showerror('Error', str(e))