# app/tabs/invoice_subtabs/indomaret_tab.py
from tkinter import *
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from src.modules import Modules
from app.custom.custom_text import CustomText
from app.tabs.popup import ResponseOpenAPI
from src.InvoiceIndomaret import InvoiceIndomaret
from app.custom.custom_treeview import CustomTreeview
from src.jsonParser import jsonParser
import threading

class IndomaretTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.configure(width=1300, height=750)

        # Frame untuk Treeview
        self.tree_frame = tk.Frame(self)
        self.tree_frame.place(relx=0.01, rely=0.01, relwidth=0.98, relheight=0.85)

        # Treeview
        columnsIndomaret = ('merchant_id', 'invoice_id', 'total_amount', 'response_payment_code', 'created_ts')
        self.MtreeInvoiceIndomaret = CustomTreeview(self.tree_frame, columns=columnsIndomaret, show='headings')
        self.MtreeInvoiceIndomaret.pack(fill=tk.BOTH, expand=True)

        # Scrollbar for Treeview
        tree_scrollbar = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.MtreeInvoiceIndomaret.yview)
        tree_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.MtreeInvoiceIndomaret.configure(yscrollcommand=tree_scrollbar.set)

        headings = ['merchant_id', 'invoice_id', 'total_amount', 'response_payment_code', 'created_ts']
        for heading in headings:
            self.MtreeInvoiceIndomaret.heading(heading, text=heading)
            self.MtreeInvoiceIndomaret.column(heading, anchor=tk.W, width=int(1200/len(headings)))

        # Frame untuk tombol
        self.button_frame = tk.Frame(self)
        self.button_frame.place(relx=0.01, rely=0.88, relwidth=0.98, relheight=0.1)

        # Tombol
        self.LoadInvoiceIndomaretbutton1 = ttk.Button(self.button_frame, text="Load Data", command=self.start_thread_connection, width=20, padding=(0, 10))
        self.LoadInvoiceIndomaretbutton1.pack(side=tk.LEFT, padx=(0, 10))

        self.LoadInvoiceIndomaretbutton2 = ttk.Button(self.button_frame, text="Pay Invoice", command=self.payIndomaret, width=20, padding=(0, 10))
        self.LoadInvoiceIndomaretbutton2.pack(side=tk.LEFT)
        self.LoadInvoiceIndomaretbutton2.config(state='disabled')

    def start_thread_connection(self):
        self.LoadInvoiceIndomaretbutton1.config(state=tk.DISABLED)
        thread = threading.Thread(target=self.connectDBIndomaret)
        thread.start()

    def connectDBIndomaret(self, event=None):
        try:
            querycon = "select merchant_id,invoice_id, total_amount, response_payment_code, created_ts from merchant_invoice_transaction mit where payment_method='INDOMARET' and status ='waiting' and expired_ts >= now() and vendor_name='BIT_DNA_INDOMARET' order by mit.created_ts desc limit 50;"
            ans = Modules.ConnectDBMerchant(querycon)
            self.LoadInvoiceIndomaretbutton2.config(state='normal')

            self.MtreeInvoiceIndomaret.delete(*self.MtreeInvoiceIndomaret.get_children())

            for row in ans:
                self.MtreeInvoiceIndomaret.insert('', tk.END, values=(row[0],row[1],row[2],row[3],row[4]))
            self.LoadInvoiceIndomaretbutton1.config(state=tk.NORMAL)
        except ValueError as error:
            ResponseOpenAPI(str(error))
        except IndexError as err:
            ResponseOpenAPI(str(err))

    def payIndomaret(self, event=None):
        try:
            selectedItem = self.MtreeInvoiceIndomaret.selection()[0]
            selectedMerchId = self.MtreeInvoiceIndomaret.item(selectedItem)['values'][0]
            selectedTotalAmount = self.MtreeInvoiceIndomaret.item(selectedItem)['values'][2]
            selectedVa = self.MtreeInvoiceIndomaret.item(selectedItem)['values'][3]
            resinq = InvoiceIndomaret.inquiryIndomaret(selectedVa, selectedMerchId)
            respay = InvoiceIndomaret.paymentIndomaret(selectedVa, selectedTotalAmount, selectedMerchId)
            resinq = jsonParser.jsonParserBeautify(resinq)
            respay = jsonParser.jsonParserBeautify(respay)
            ResponseOpenAPI(str("Inquiry Response:\n" + resinq + "\n" + "Payment Response:\n" + respay))
            self.start_thread_connection()
        except IndexError:
            ResponseOpenAPI('Please select data first')