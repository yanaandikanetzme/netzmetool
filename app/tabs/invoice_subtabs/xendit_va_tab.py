# app/tabs/invoice_subtabs/xendit_va_tab.py
from tkinter import *
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from src.modules import Modules
from app.tabs.popup import ResponseOpenAPI
from src.InvoiceXenditVA import InvoiceXenditVA
from app.custom.custom_treeview import CustomTreeview
from src.jsonParser import jsonParser
import threading

class XenditVATab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.configure(width=1300, height=750)

        # Frame untuk Treeview
        self.tree_frame = tk.Frame(self)
        self.tree_frame.place(relx=0.01, rely=0.01, relwidth=0.98, relheight=0.85)

        # Treeview
        columnsXendit = ('merchant_id', 'invoice_id', 'total_amount', 'vendor_id', 'created_ts', 'payment_method')
        self.MtreeInvoiceXendit = CustomTreeview(self.tree_frame, columns=columnsXendit, show='headings')
        self.MtreeInvoiceXendit.pack(fill=tk.BOTH, expand=True)

        # Scrollbar for Treeview
        tree_scrollbar = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.MtreeInvoiceXendit.yview)
        tree_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.MtreeInvoiceXendit.configure(yscrollcommand=tree_scrollbar.set)

        headings = ['merchant_id', 'invoice_id', 'total_amount', 'vendor_id', 'created_ts', 'payment_method']
        for heading in headings:
            self.MtreeInvoiceXendit.heading(heading, text=heading)
            self.MtreeInvoiceXendit.column(heading, anchor=tk.W, width=int(1200/len(headings)))

        # Frame untuk tombol
        self.button_frame = tk.Frame(self)
        self.button_frame.place(relx=0.01, rely=0.88, relwidth=0.98, relheight=0.1)

        # Tombol
        self.LoadInvoiceXenditbutton1 = ttk.Button(self.button_frame, text="Load Data", command=self.start_thread_connection, width=20, padding=(0, 10))
        self.LoadInvoiceXenditbutton1.pack(side=tk.LEFT, padx=(0, 10))

        self.LoadInvoiceXenditbutton2 = ttk.Button(self.button_frame, text="Pay Invoice", command=self.payXenditVA, width=20, padding=(0, 10))
        self.LoadInvoiceXenditbutton2.pack(side=tk.LEFT)
        self.LoadInvoiceXenditbutton2.config(state='disabled')

    def start_thread_connection(self):
        self.LoadInvoiceXenditbutton1.config(state=tk.DISABLED)
        thread = threading.Thread(target=self.connectDBXenditVA)
        thread.start()

    def connectDBXenditVA(self, event=None):
        try:
            querycon = "select invoice_id, merchant_id, total_amount, vendor_id, created_ts, payment_method from merchant_invoice_transaction mit where status='waiting' and payment_method like '%VA%' and vendor_name = 'XENDIT' and expired_ts >= now() order by mit.created_ts desc limit 50;"
            ans = Modules.ConnectDBMerchant(querycon)
            self.LoadInvoiceXenditbutton2.config(state='normal')

            self.MtreeInvoiceXendit.delete(*self.MtreeInvoiceXendit.get_children())

            for row in ans:
                self.MtreeInvoiceXendit.insert('', tk.END, values=(row[0],row[1],row[2],row[3],row[4],row[5]))
            self.LoadInvoiceXenditbutton1.config(state=tk.NORMAL)
        except ValueError as error:
            ResponseOpenAPI(str(error))
        except IndexError as err:
            ResponseOpenAPI(str(err))

    def payXenditVA(self, event=None):
        try:
            selectedItem = self.MtreeInvoiceXendit.selection()[0]
            selectedAmount = str(self.MtreeInvoiceXendit.item(selectedItem)['values'][2])
            selectedVA = str(self.MtreeInvoiceXendit.item(selectedItem)['values'][3])
            bodyreqpay = InvoiceXenditVA.generateURLXenditVA(selectedVA,selectedAmount)
            bodyreqpay = jsonParser.jsonParserBeautify(bodyreqpay)
            ResponseOpenAPI('Payment Response :\n' + str(bodyreqpay))
            self.start_thread_connection()
        except IndexError:
            ResponseOpenAPI('Response', 'Please select data first')
        except ValueError as error:
            ResponseOpenAPI(str(error))