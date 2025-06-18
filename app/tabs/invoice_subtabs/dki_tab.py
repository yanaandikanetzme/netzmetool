# app/tabs/invoice_subtabs/dki_tab.py
from tkinter import *
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from src.modules import Modules
from app.custom.custom_text import CustomText
from app.tabs.popup import ResponseOpenAPI
from src.InvoiceDKI import InvoiceDKI
from app.custom.custom_treeview import CustomTreeview
from src.jsonParser import jsonParser
import threading

class DKITab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.configure(width=1300, height=750)

        # Frame untuk Treeview
        self.tree_frame = tk.Frame(self)
        self.tree_frame.place(relx=0.01, rely=0.01, relwidth=0.98, relheight=0.85)

        # Treeview
        columnsDKI = ('merchant_id', 'invoice_id', 'total_amount', 'response_payment_code', 'created_ts')
        self.MtreeInvoiceDKI = CustomTreeview(self.tree_frame, columns=columnsDKI, show='headings')
        self.MtreeInvoiceDKI.pack(fill=tk.BOTH, expand=True)

        # Scrollbar for Treeview
        tree_scrollbar = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.MtreeInvoiceDKI.yview)
        tree_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.MtreeInvoiceDKI.configure(yscrollcommand=tree_scrollbar.set)

        headings = ['merchant_id', 'invoice_id', 'total_amount', 'response_payment_code', 'created_ts']
        for heading in headings:
            self.MtreeInvoiceDKI.heading(heading, text=heading)
            self.MtreeInvoiceDKI.column(heading, anchor=tk.W, width=int(1200/len(headings)))

        # Frame untuk tombol
        self.button_frame = tk.Frame(self)
        self.button_frame.place(relx=0.01, rely=0.88, relwidth=0.98, relheight=0.1)

        # Tombol
        self.LoadInvoiceDKIbutton1 = ttk.Button(self.button_frame, text="Load Data", command=self.start_thread_connection, width=15, padding=(0, 10))
        self.LoadInvoiceDKIbutton1.pack(side=tk.LEFT, padx=(0, 10))

        self.LoadInvoiceDKIbutton4 = ttk.Button(self.button_frame, text="Inquiry Invoice", command=self.InquiryDKI, width=15, padding=(0, 10))
        self.LoadInvoiceDKIbutton4.pack(side=tk.LEFT, padx=(0, 10))
        self.LoadInvoiceDKIbutton4.config(state='disabled')

        self.LoadInvoiceDKIbutton3 = ttk.Button(self.button_frame, text="Pay Invoice", command=self.PayDKI, width=15, padding=(0, 10))
        self.LoadInvoiceDKIbutton3.pack(side=tk.LEFT)
        self.LoadInvoiceDKIbutton3.config(state='disabled')

        self.TextBodyInvoiceDKI1 = CustomText(self)

    def start_thread_connection(self):
        self.LoadInvoiceDKIbutton1.config(state=tk.DISABLED)
        thread = threading.Thread(target=self.connectDBDKI)
        thread.start()

    def connectDBDKI(self, event=None):
        try:
            querycon = "select invoice_id, merchant_id, total_amount, response_payment_code, created_ts from merchant_invoice_transaction mit where payment_method='DKI' and status='waiting' order by mit.created_ts desc limit 50;"
            ans = Modules.ConnectDBMerchant(querycon)
            self.LoadInvoiceDKIbutton3.config(state='normal')
            self.LoadInvoiceDKIbutton4.config(state='normal')

            self.MtreeInvoiceDKI.delete(*self.MtreeInvoiceDKI.get_children())

            for row in ans:
                self.MtreeInvoiceDKI.insert('', tk.END, values=(row[0],row[1],row[2],row[3],row[4]))
            self.LoadInvoiceDKIbutton1.config(state=tk.NORMAL)
        except ValueError as error:
            ResponseOpenAPI(str(error))
        except IndexError as err:
            ResponseOpenAPI(str(err))

    def InquiryDKI(self, event=None):
        try:
            selectedItem = self.MtreeInvoiceDKI.selection()[0]
            selectedAmount = str(self.MtreeInvoiceDKI.item(selectedItem)['values'][2])
            selectedVA = str(self.MtreeInvoiceDKI.item(selectedItem)['values'][3])
            authtoken =  str(InvoiceDKI.getRequestTokenDKI())
            bodyreqinq = InvoiceDKI.inquiryInvoiceDKI(selectedVA, selectedAmount, authtoken)
            bodyreqinq = jsonParser.jsonParserBeautify(bodyreqinq)
            ResponseOpenAPI('Inquiry Response :\n'+ str(bodyreqinq))
        except IndexError:
            ResponseOpenAPI('Please select data first')

    def PayDKI(self, event=None):
        try:
            selectedItem = self.MtreeInvoiceDKI.selection()[0]
            selectedAmount = str(self.MtreeInvoiceDKI.item(selectedItem)['values'][2])
            selectedVA = str(self.MtreeInvoiceDKI.item(selectedItem)['values'][3])
            authtoken =  str(InvoiceDKI.getRequestTokenDKI())
            bodyreqinq = InvoiceDKI.inquiryInvoiceDKI(selectedVA, selectedAmount, authtoken)
            bodyreqpay = InvoiceDKI.paymentInvoiceDKI(selectedVA, selectedAmount, authtoken)
            bodyreqinq = jsonParser.jsonParserBeautify(bodyreqinq)
            bodyreqpay = jsonParser.jsonParserBeautify(bodyreqpay)
            ResponseOpenAPI('Inquiry Response :\n'+ str(bodyreqinq) + '\n' + 'Payment Response :\n' + str(bodyreqpay))
            self.start_thread_connection()
        except IndexError:
            ResponseOpenAPI('Please select data first')