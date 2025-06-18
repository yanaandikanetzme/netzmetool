# app/tabs/open_api_subtabs/netzme_open_api_subtabs/netzme_webview_tab.py
from tkinter import *
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from src.modules import Modules
from app.custom.custom_text import CustomText
import webbrowser
from app.tabs.popup import ResponseOpenAPI
from app.custom.custom_treeview import CustomTreeview
import threading

class NetzmeWebviewTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        # Add your elements here

        self.NWVlbl1 = tk.Label(self, text="AggregatorId")
        self.NWVcb1 = ttk.Combobox(self, width=55)
        self.NWVcb1['values'] = Modules.getAllAggregatorNetzme()
        self.NWVcb1.config(state='readonly')
        self.NWVcb1.bind("<<ComboboxSelected>>", self.getClearPasswordNetzme)

        self.NWVlbl2 = tk.Label(self,text="ClearPassword")
        self.NWVEn1 = tk.Entry(self)

        self.y17 = tk.StringVar()
        self.y18 = tk.StringVar()
        variables = [self.y17, self.y18]
        functions = [self.on_field_NWVcb2change]
        for variable, function in zip(variables, functions):
            variable.trace_add('write', lambda *args, func=function: func())

        self.NWVlbl5 = tk.Label(self,text="Endpoint")
        self.NWVcb2 = ttk.Combobox(self, width=55, textvariable=self.y17)
        self.NWVcb2['values'] = ['Connect To Netzme','Upgrade Account','Payment Bill','Payment QRIS']
        self.NWVcb2.config(state='readonly')

        self.NWVBtn = ttk.Button(self, text="Open Url", command=self.open_url)

        self.NWVlblPhoneNumber = tk.Label(self,text="Phone Number")
        self.NWVEnPhoneNumber = tk.Entry(self)
        self.NWVEnPhoneNumber.bind('<KeyRelease>', self.get_url_webview)

        self.NWVlblUserId = tk.Label(self,text="User Id")
        self.NWVEnUserId = tk.Entry(self)
        self.NWVEnUserId.bind('<KeyRelease>', self.get_url_webview)

        self.NWVlblAmount = tk.Label(self,text="Amount")
        self.NWVEnAmount = tk.Entry(self)
        self.NWVEnAmount.bind('<KeyRelease>', self.get_url_webview)

        self.NWVlblQRType = tk.Label(self,text="QR Type")
        self.NWVlblQRContent = tk.Label(self,text="QR Content")
        self.NWVcbQR = ttk.Combobox(self, width=55)
        self.NWVcbQR['values'] = ['Statis','Dinamis']
        self.NWVcbQR.bind("<<ComboboxSelected>>", self.get_qr_content)

        self.NWVEnQRContent = CustomText(self, height=4)
        self.NWVEnQRContent.bind("<<TextModified>>", self.get_url_webview)

        self.NWVlblUrl = tk.Label(self, text="Url")
        self.NWVEnUrl = CustomText(self, height=8)
        
        self.NWVlblTree = tk.Label(self, text="Data")
        self.Mtree = CustomTreeview(self, show='headings')
        #self.Mtree.pack(pady=0, fill="both")
        columnsQR = ('nmid','merchant_id', 'merchant_name_long', 'qr_content_static')
        self.Mtree.configure(columns=columnsQR)
        self.Mtree.heading('nmid', text='nmid')
        self.Mtree.heading('merchant_id', text='merchant_id')
        self.Mtree.heading('merchant_name_long', text='merchant_name_long')
        self.Mtree.heading('qr_content_static', text='qr_content_static')
        self.Mtree.column('nmid', anchor=tk.W, stretch='NO', width=170, minwidth=120)
        self.Mtree.column('merchant_id', anchor=tk.W, stretch='NO', width=120, minwidth=120)
        self.Mtree.column('merchant_name_long', anchor=tk.W, stretch='NO', width=170, minwidth=170)
        self.Mtree.column('qr_content_static', anchor=tk.W, stretch='NO')
        self.Mtree.place(width=700, height=200)
        self.Mtree["displaycolumns"] = ('nmid', 'merchant_id', 'merchant_name_long', 'qr_content_static')
        self.Mtree.bind("<<TreeviewSelect>>", self.generate_QR)

        self.MtreeInvoice = CustomTreeview(self, show='headings')
        #self.MtreeInvoice.pack(pady=0, fill="both")
        columnsQRIS = ('invoice_id', 'merchant_id', 'merchant_name', 'total_amount', 'qr_content')
        self.MtreeInvoice.configure(columns=columnsQRIS)
        self.MtreeInvoice.heading('invoice_id', text='invoice_id')
        self.MtreeInvoice.heading('merchant_id', text='merchant_id')
        self.MtreeInvoice.heading('merchant_name', text='merchant_name')
        self.MtreeInvoice.heading('total_amount', text='total_amount')
        self.MtreeInvoice.heading('qr_content', text='qr_content')
        self.MtreeInvoice.column('invoice_id', anchor=tk.W, stretch='NO')
        self.MtreeInvoice.column('merchant_id', anchor=tk.W, stretch='NO')
        self.MtreeInvoice.column('merchant_name', anchor=tk.W, stretch='NO')
        self.MtreeInvoice.column('total_amount', anchor=tk.W, stretch='NO')
        self.MtreeInvoice.column('qr_content', anchor=tk.W, stretch='NO')
        self.MtreeInvoice.place(width=800, height=200)  # Tampilkan MtreeInvoice
        self.MtreeInvoice["displaycolumns"] = ('invoice_id', 'merchant_id', 'merchant_name', 'total_amount', 'qr_content')
        self.MtreeInvoice.bind("<<TreeviewSelect>>", self.generate_QR)

        self.NWVcb2.bind("<<ComboboxSelected>>", self.get_url_webview)
        self.loadAwal()
        
    def open_url(self, *args):
        url = self.NWVEnUrl.get('1.0', 'end-1c')
        webbrowser.open_new(url)

    def get_qr_content(self, *args):
        selection = self.NWVcbQR.get()
        self.get_url_webview()
        # Hapus semua item (baris) di Mtree sebelum mengonfigurasi ulang kolomnya
        self.Mtree.delete(*self.Mtree.get_children())
        self.MtreeInvoice.delete(*self.MtreeInvoice.get_children())
        if selection == "Statis":
            self.start_thread_connection_qr_merchant()
        else:
            self.start_thread_connection_db_qris()

    def generate_QR(self, event=None):
        try:
            selection = self.NWVcbQR.get()
            if selection == "Statis":
                selectedItem = self.Mtree.selection()
                qrcodes = self.Mtree.item(selectedItem[0])['values'][3]  # qr_content
                self.NWVEnQRContent.delete('1.0', tk.END)
                self.NWVEnQRContent.insert(tk.END, str(qrcodes))
            else:
                selectedItem = self.MtreeInvoice.selection()
                qrcodes = self.MtreeInvoice.item(selectedItem[0])['values'][4]
                nominal = self.MtreeInvoice.item(selectedItem[0])['values'][3]
                self.NWVEnQRContent.delete('1.0', tk.END)
                self.NWVEnQRContent.insert(tk.END, str(qrcodes))
                self.NWVEnAmount.delete(0, tk.END)
                self.NWVEnAmount.insert(tk.END, str(nominal))
        except IndexError:
            pass

    def show_and_hide(self):
        self.NWVlbl1.place(x=3, y=3)
        self.NWVcb1.place(x=110, y=3)
        self.NWVlbl2.place(x=3, y=33)
        self.NWVEn1.place(x=110, y=33)
        self.NWVlbl5.place(x=3, y=63)
        self.NWVcb2.place(x=110, y=63)
        self.NWVBtn.place(x=575, y=520)
        self.NWVlblUrl.place(x=3, y=410)
        self.NWVEnUrl.place(x=110, y=410)
        selection_nwvcb2 = self.NWVcb2.get()
        self.NWVlblPhoneNumber.place(x=17500, y=3)
        self.NWVEnPhoneNumber.place(x=17500, y=3)
        self.NWVlblUserId.place(x=17500, y=3)
        self.NWVEnUserId.place(x=17500, y=3)
        self.NWVlblAmount.place(x=17500, y=3)
        self.NWVEnAmount.place(x=17500, y=3)
        self.NWVlblQRContent.place(x=17500, y=3)
        self.NWVEnQRContent.place(x=17500, y=3)
        self.NWVcbQR.place(x=17500, y=3)
        self.NWVlblQRType.place(x=17500, y=3)
        self.NWVlblTree.place(x=17500, y=3)
        self.MtreeInvoice.place(x=17500, y=3)
        self.Mtree.place(x=17500, y=3)

        selectionzs = self.NWVcbQR.get()
            
        if selection_nwvcb2 in ["Connect To Netzme","Upgrade Account"]:
            self.NWVlblPhoneNumber.place(x=740, y=3)
            self.NWVEnPhoneNumber.config(state='normal')
            self.NWVEnPhoneNumber.place(x=840, y=3)
            if selection_nwvcb2 in ["Upgrade Account"]:
                self.NWVlblUserId.place(x=3, y=93)
                self.NWVEnUserId.place(x=110, y=93)
                self.NWVEnUserId.config(state='normal')
        elif selection_nwvcb2 in ["Payment Bill","Payment QRIS"]:
            self.NWVlblAmount.place(x=740, y=3)
            self.NWVEnAmount.config(state='normal')
            self.NWVEnAmount.place(x=840, y=3)
            self.NWVlblUserId.place(x=3, y=93)
            self.NWVEnUserId.place(x=110, y=93)
            self.NWVEnUserId.config(state='normal')
            if selection_nwvcb2 in ["Payment QRIS"]:
                self.NWVlblQRType.place(x=3, y=140)
                self.NWVcbQR.place(x=110, y=140)
                self.NWVlblTree.place(x=3, y=200)
                if selectionzs == "Statis":
                    self.Mtree.place(x=110, y=200)  # Tampilkan Mtree
                else:
                    self.MtreeInvoice.place(x=110, y=200)  # Tampilkan MtreeInvoice

    def start_thread_connection_db_qris(self):
        #self.run_button.config(state=tk.DISABLED)
        # Memulai thread baru untuk koneksi database
        thread = threading.Thread(target=self.connectDBQRIS)
        thread.start()

    def connectDBQRIS(self, event=None):
        try:
            querycon = "SELECT mit.invoice_id, qm.merchant_id, qm.merchant_name, qc.amount_value as total_amount, qc.qr_content FROM qris_content qc full outer join merchant_invoice_transaction mit on qc.qris_content_id = mit.invoice_transaction_id inner JOIN qris_merchant qm ON qm.merchant_id=qc.merchant_id where qc.status='open' ORDER BY qc.seq DESC limit 50;"
            ans = Modules.ConnectDBMerchant(querycon)
            for rowz in self.MtreeInvoice.get_children():
                self.MtreeInvoice.delete(rowz)
            for row in ans:
                self.MtreeInvoice.insert('', tk.END, values=(row[0],row[1],row[2],row[3],row[4]))
        except ValueError as error:
            ResponseOpenAPI(str(error))
        except IndexError as err:
            ResponseOpenAPI(str(err))

    def start_thread_connection_qr_merchant(self):
        #self.run_button.config(state=tk.DISABLED)
        # Memulai thread baru untuk koneksi database
        thread = threading.Thread(target=self.onLoadQRMerchant)
        thread.start()

    def onLoadQRMerchant(self, event=None):
        try:
            quiru = ("SELECT qm.nmid, qm.merchant_id, qm.merchant_name_long, qm.qr_content_static FROM qris_merchant qm order by qm.nmid desc;")
            ans = Modules.ConnectDBMerchant(quiru)
            for rowz in self.Mtree.get_children():
                self.Mtree.delete(rowz)
            for row in ans:
                self.Mtree.insert('', tk.END, values=(row[0],row[1],row[2],row[3]))
        except IndexError as err:
            ResponseOpenAPI(str(err))
        except ValueError as error:
            ResponseOpenAPI(str(error))

    def get_url_webview(self, *args):
        self.show_and_hide()
        selection_nwvcb2 = self.NWVcb2.get()
        amount = self.NWVEnAmount.get()
        aggregator = self.NWVcb1.get()
        phoneNo = self.NWVEnPhoneNumber.get()
        userId = self.NWVEnUserId.get()
        guid = Modules.generateUUID()
        qrcontent = str(self.NWVEnQRContent.get("1.0",'end-1c'))
        reqid_payment_bill = 'aggregator' + Modules.RandomDigit(12)
        expired_ts = Modules.generate_timestamp_expired()
        if selection_nwvcb2 in ["Connect To Netzme"]:
            url = f"https://xplorin-stg.netzme.id/connect-to-netzme?fullname=yoga&aggregator_id={aggregator}&android_os=10&android_api=29&id_1=11d18b3b6f123123&device=Xiaomi%20Redmi%208A%20Pro&phone_number={phoneNo}"
            self.NWVEnUrl.delete('1.0', tk.END)
            self.NWVEnUrl.insert(tk.END, str(url))
        elif selection_nwvcb2 in ["Upgrade Account"]:
            url = f"https://xplorin-stg.netzme.id/cdd?requestId={guid}&type=cdd&userId={userId}&aggregatorId={aggregator}&phoneNumber={phoneNo}"
            self.NWVEnUrl.delete('1.0', tk.END)
            self.NWVEnUrl.insert(tk.END, str(url))
        elif selection_nwvcb2 in ["Payment Bill"]:
            if amount == "":
                amount = 0
            url = f"https://xplorin-stg.netzme.id/pin-transaction?requestId={reqid_payment_bill}&type=aggregator_payment_bill&userId={userId}&billId={guid}&amount={amount}&aggregatorId={aggregator}&description=percobaanQA&expired_at={expired_ts}"
            self.NWVEnUrl.delete('1.0', tk.END)
            self.NWVEnUrl.insert(tk.END, str(url))
        elif selection_nwvcb2 in ["Payment QRIS"]:
            if amount == "":
                amount = 0
            url = f"https://xplorin-stg.netzme.id/pin-transaction?requestId={guid}&type=aggregator_pay_qr&userId={userId}&qrContent={qrcontent}&amount={amount}&points=0&aggregatorId={aggregator}"
            self.NWVEnUrl.delete('1.0', tk.END)
            self.NWVEnUrl.insert(tk.END, str(url))

    def getClearPasswordNetzme(self, *args):
        aggId = self.NWVcb1.get()
        if not self.NWVcb1.get() == "":
            self.NWVEn1.config(state='normal')
            getstr = Modules.searchclearPassByaggregatorNetzme(aggId)[0]
            self.NWVEn1.delete(0, END)
            self.NWVEn1.insert(tk.END, str(getstr))

    def loadAwal(self, *args):
        self.get_url_webview()
        self.getClearPasswordNetzme()

    def on_field_NWVcb2change(self):
        self.get_url_webview()
