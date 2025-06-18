# app/tabs/invoice_subtabs/bca_faspay_tab.py
from tkinter import *
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from src.modules import Modules
from app.tabs.popup import ResponseOpenAPI
from src.InvoiceFaspay import FaspayPay
from app.custom.custom_treeview import CustomTreeview
from src.jsonParser import jsonParser
import threading

class BCAFaspayTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.configure(width=1300, height=750)

        # Frame untuk Treeview
        self.tree_frame = tk.Frame(self)
        self.tree_frame.place(relx=0.01, rely=0.01, relwidth=0.98, relheight=0.85)

        # Treeview
        columnsBCA = ('invoice_id', 'amount', 'trx_id', 'bill_no', 'request_ts')
        self.MtreeInvoiceBCA = CustomTreeview(self.tree_frame, columns=columnsBCA, show='headings')
        self.MtreeInvoiceBCA.pack(fill=tk.BOTH, expand=True)

        # Scrollbar for Treeview
        tree_scrollbar = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.MtreeInvoiceBCA.yview)
        tree_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.MtreeInvoiceBCA.configure(yscrollcommand=tree_scrollbar.set)

        headings = ['invoice_id', 'amount', 'trx_id', 'bill_no', 'request_ts']
        for heading in headings:
            self.MtreeInvoiceBCA.heading(heading, text=heading)
            self.MtreeInvoiceBCA.column(heading, anchor=tk.W, width=int(1200/len(headings)))

        # Frame untuk tombol
        self.button_frame = tk.Frame(self)
        self.button_frame.place(relx=0.01, rely=0.88, relwidth=0.98, relheight=0.1)

        # Tombol
        self.LoadInvoiceBCAbutton1 = ttk.Button(self.button_frame, text="Load Data", command=self.start_thread_connection, width=20, padding=(0, 10))
        self.LoadInvoiceBCAbutton1.pack(side=tk.LEFT, padx=(0, 10))

        self.LoadInvoicePaybutton1 = ttk.Button(self.button_frame, text="Pay Invoice", command=self.PayBCA, width=20, padding=(0, 10))
        self.LoadInvoicePaybutton1.pack(side=tk.LEFT)
        self.LoadInvoicePaybutton1.config(state='disabled')

    def start_thread_connection(self):
        self.LoadInvoiceBCAbutton1.config(state=tk.DISABLED)
        thread = threading.Thread(target=self.connectDBFaspay)
        thread.start()

    def connectDBFaspay(self, event=None):
        try:
            querycon = "select invoice_id, json_request ->> 'bill_total' as amount , json_response ->> 'trx_id' as trx_id, json_response ->>'bill_no' as bill_no, request_ts from faspay_create_invoice where invoice_id in (select invoice_id from merchant_invoice_transaction where payment_method='BANK_TRANSFER_FASPAY' and status != 'paid' and expired_ts > now()) order by request_ts desc limit 20;"
            ans = Modules.ConnectDBMerchant(querycon)
            self.MtreeInvoiceBCA.delete(*self.MtreeInvoiceBCA.get_children())
            for row in ans:
                amountmin2 = int(row[1]) // 100
                self.MtreeInvoiceBCA.insert('', tk.END, values=(row[0],amountmin2,row[2],row[3],row[4]))
            self.LoadInvoiceBCAbutton1.config(state=tk.NORMAL)
            self.LoadInvoicePaybutton1.config(state='normal')
        except ValueError as error:
            ResponseOpenAPI(str(error))
        except IndexError as err:
            ResponseOpenAPI(str(err))

    def PayBCA(self, event=None):
        try:
            url = 'https://tokoapi-stg.netzme.com/faspay/payment/notification'
            selectedItem = self.MtreeInvoiceBCA.selection()[0]
            selectedAmount = self.MtreeInvoiceBCA.item(selectedItem)['values'][1]
            selectedTrxId = self.MtreeInvoiceBCA.item(selectedItem)['values'][2]
            selectedBillNo = self.MtreeInvoiceBCA.item(selectedItem)['values'][3]
            bodyreq = FaspayPay.FaspayPayDef(selectedAmount, selectedTrxId, selectedBillNo)
            HitPOST = Modules.POSThttp(url, bodyreq)
            HitPOST = jsonParser.jsonParserBeautify(HitPOST)
            ResponseOpenAPI(str(HitPOST))
            self.start_thread_connection()
        except IndexError:
            ResponseOpenAPI('Please select data first')