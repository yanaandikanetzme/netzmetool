# app/tabs/invoice_subtabs/qris_tab.py
from tkinter import *
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import json
import yaml
import re
from app.custom.custom_treeview import CustomTreeview
import threading
import qrcode
from app.custom.custom_text import CustomText
from src.modules import Modules
from src.jsonParser import jsonParser
from app.tabs.popup import ResponseOpenAPI

class QRISTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.create_widgets()
        self.layout_widgets()
        self.key_url = []
        self.setup_initial_state()

    def create_widgets(self):
        # Main frames
        self.left_frame = ttk.Frame(self)
        self.right_frame = ttk.Frame(self)

        # Left frame sub-frames
        self.frame_A = ttk.Frame(self.left_frame)
        self.frame_B = ttk.Frame(self.left_frame)

        # Frame A sub-frames
        self.frame_A1 = ttk.Frame(self.frame_A)
        self.frame_A2 = ttk.Frame(self.frame_A)

        # Create widgets
        self.create_qr_display()
        self.create_mode_selector()
        self.create_qris_listbox()
        self.create_treeview()
        self.create_input_fields()
        self.create_buttons()
        self.create_text_area()
        
        # Add shamacInvoiceQRIS
        self.shamacInvoiceQRIS = ttk.Entry(self.right_frame)

    def layout_widgets(self):
        self.columnconfigure(0, weight=3)
        self.columnconfigure(1, weight=2)
        self.rowconfigure(0, weight=1)

        self.left_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.right_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        # Left frame layout
        self.left_frame.columnconfigure(0, weight=1)
        self.left_frame.rowconfigure(0, weight=1)  # For frame B
        self.left_frame.rowconfigure(1, weight=0)  # For frame A
        
        self.frame_B.grid(row=0, column=0, sticky="nsew", pady=10)
        self.frame_A.grid(row=1, column=0, sticky="nsew", pady=10)

        # Frame B layout
        self.frame_B.columnconfigure(0, weight=1)
        self.frame_B.rowconfigure(0, weight=1)
        self.frame_B.rowconfigure(1, weight=0)
        
        self.MtreeInvoiceQRIS.grid(row=0, column=0, sticky="nsew", pady=10)
        self.shamacInvoiceQRIS.grid(row=1, column=0, sticky="ew", pady=5)

        # Frame A layout
        self.frame_A.columnconfigure(0, weight=1)  # For A1
        self.frame_A.columnconfigure(1, weight=1)  # For A2
        
        self.frame_A1.grid(row=0, column=0, sticky="nsew", padx=5)
        self.frame_A2.grid(row=0, column=1, sticky="nsew", padx=5)

        # Frame A1 layout
        self.frame_A1.columnconfigure(0, weight=1)
        self.frame_A1.rowconfigure(0, weight=1)
        self.img_frame.grid(row=0, column=0, sticky="nsew", pady=10)

        # Frame A2 layout
        self.frame_A2.columnconfigure(0, weight=1)
        self.frame_A2.rowconfigure(0, weight=0)
        self.frame_A2.rowconfigure(1, weight=0)
        self.OnOffusCombobox.grid(row=0, column=0, pady=5, sticky="ew")
        self.QRISlistbox.grid(row=1, column=0, pady=5, sticky="ew")

        # Right frame layout
        self.right_frame.columnconfigure(0, weight=1)
        self.right_frame.columnconfigure(1, weight=1)
        self.right_frame.rowconfigure(9, weight=1)
        
        self.layout_input_fields()
        self.layout_buttons()
        
        self.textbodyqrisInv.grid(row=9, column=0, columnspan=2, sticky="nsew", pady=10)
        self.shamacInvoiceQRIS.grid(row=10, column=0, columnspan=2, sticky="ew", pady=5)

        self.EnUserId.grid(row=0, column=1, sticky="ew", padx=5, pady=2)
        self.EnPin.grid(row=1, column=1, sticky="ew", padx=5, pady=2)
        self.QRISlistbox.grid(row=1, column=0, pady=5, sticky="ew")
        self.shamacInvoiceQRIS.grid(row=10, column=0, columnspan=2, sticky="ew", pady=5)

    def create_treeview(self):
        columns = ('invoice_id', 'invoice_transaction_id', 'merchant_name', 'total_amount', 'qr_content', 'merchant_pan', 'merchant_type', 'nmid', 'merchant_city', 'postal_code', 'ms_user_id', 'merchant_criteria', 'terminal_id')
        self.MtreeInvoiceQRIS = CustomTreeview(self.frame_B, columns=columns, show='headings', height=10)
        self.MtreeInvoiceQRIS["displaycolumns"] = ('invoice_id', 'invoice_transaction_id', 'merchant_name', 'total_amount', 'qr_content')
        for col in columns:
            self.MtreeInvoiceQRIS.heading(col, text=col)
            self.MtreeInvoiceQRIS.column(col, width=100, anchor=tk.W)
        self.MtreeInvoiceQRIS.bind("<<TreeviewSelect>>", self.bodyQRInvoice)

    def create_qris_listbox(self):
        self.x = tk.StringVar(value='Domestik')
        self.QRISlistbox = ttk.Combobox(self.frame_A2, textvariable=self.x, 
                                        values=['Domestik', 'Cross Border', 'ArtaJasa', 
                                                'Check Status Domestik', 'Check Status Cross Border', 
                                                'Check Status ArtaJasa'],
                                        state="readonly")
        self.QRISlistbox.bind("<<ComboboxSelected>>", self.bodyQRInvoice)

    def create_qr_display(self):
        self.qr_size = (195, 195)
        self.display_size = (200, 200)
        self.img_frame = ttk.Frame(self.frame_A1, width=self.display_size[0], height=self.display_size[1])
        self.img_qrinvoicelbl = tk.Label(self.img_frame)
        self.img_qrinvoicelbl.grid(row=0, column=0, sticky="nsew")
        self.img_frame.grid_propagate(False)

    def create_mode_selector(self):
        self.x2 = tk.StringVar()
        self.OnOffusCombobox = ttk.Combobox(self.frame_A2, textvariable=self.x2, values=['Off Us', 'On Us'], state="readonly")
        self.OnOffusCombobox.bind("<<ComboboxSelected>>", self.on_mode_change)

    def create_input_fields(self):
        self.EnUserId = ttk.Entry(self.right_frame)
        self.pin_var = tk.StringVar()
        self.pin_var.trace_add("write", self.limit_pin)
        self.EnPin = ttk.Entry(self.right_frame, show="*", textvariable=self.pin_var)
        
        self.EnUserId.bind('<KeyRelease>', self.bodyQRInvoice)
        self.EnPin.bind('<KeyRelease>', self.bodyQRInvoice)

    def layout_input_fields(self):
        tk.Label(self.right_frame, text="User ID").grid(row=0, column=0, sticky="e", padx=5, pady=2)
        self.EnUserId.grid(row=0, column=1, sticky="ew", padx=5, pady=2)
        tk.Label(self.right_frame, text="PIN").grid(row=1, column=0, sticky="e", padx=5, pady=2)
        self.EnPin.grid(row=1, column=1, sticky="ew", padx=5, pady=2)

    def create_buttons(self):
        self.LoadInvoiceQRISbutton1 = ttk.Button(self.right_frame, text="Load Data", command=self.start_thread_connection)
        self.LoadInvoiceQRISbutton2 = ttk.Button(self.right_frame, text="Pay Invoice", command=self.validate_and_pay_qris_invoice, state='disabled')

    def layout_buttons(self):
        self.LoadInvoiceQRISbutton1.grid(row=5, column=0, columnspan=2, sticky="ew", padx=5, pady=2)
        self.LoadInvoiceQRISbutton2.grid(row=6, column=0, columnspan=2, sticky="ew", padx=5, pady=2)

    def create_text_area(self):
        self.textbodyqrisInv = CustomText(self.right_frame, width=40, height=20)
        self.textbodyqrisInv.bind("<<TextModified>>", self.generateHMACInvoice)

    def setup_initial_state(self):
        self.OnOffusCombobox.set('Off Us')
        self.on_mode_change()

    def on_mode_change(self, event=None):
        mode = self.OnOffusCombobox.get()
        if mode == 'On Us':
            self.EnUserId.grid()
            self.EnPin.grid()
            self.QRISlistbox.grid_remove()
            self.shamacInvoiceQRIS.grid_remove()
        else:
            self.EnUserId.grid_remove()
            self.EnPin.grid_remove()
            self.QRISlistbox.grid()
            self.shamacInvoiceQRIS.grid()
        self.bodyQRInvoice()
    
    def limit_pin(self, *args):
        value = self.pin_var.get()
        if len(value) > 6:
            self.pin_var.set(value[:6])

    def validate_and_pay_qris_invoice(self):
        if self.OnOffusCombobox.get() == "On Us":
            if len(self.pin_var.get()) != 6:
                messagebox.showerror("Error", "PIN harus 6 digit")
                return
        self.payQRISInvoice()

    def start_thread_connection(self):
        self.LoadInvoiceQRISbutton1.config(state=tk.DISABLED)
        # Memulai thread baru untuk koneksi database
        thread = threading.Thread(target=self.connectDBQRIS)
        thread.start()

    def connectDBQRIS(self, event=None):
        try:
            querycon = "SELECT mit.invoice_id, qc.qris_content_id as invoice_transaction_id,qm.merchant_name, qc.amount_value as total_amount,qc.qr_content,qm.merchant_pan,qm.merchant_type,qm.nmid,qm.merchant_city,qm.postal_code,qm.merchant_criteria,qm.ms_user_id,qc.terminal_id FROM qris_content qc full outer join merchant_invoice_transaction mit on qc.qris_content_id = mit.invoice_transaction_id inner JOIN qris_merchant qm ON qm.merchant_id=qc.merchant_id where qc.status='open' ORDER BY qc.seq DESC limit 50;"
            ans = Modules.ConnectDBMerchant(querycon)
            self.LoadInvoiceQRISbutton2.config(state='normal')

            for rowz in self.MtreeInvoiceQRIS.get_children():
                self.MtreeInvoiceQRIS.delete(rowz)

            for row in ans:
                self.MtreeInvoiceQRIS.insert('', tk.END, values=(row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12]))
            self.LoadInvoiceQRISbutton1.config(state=tk.NORMAL)
        except ValueError as error:
            ResponseOpenAPI(str(error))
        except IndexError as err:
            ResponseOpenAPI(str(err))
    key_url = []
    def generate_QRInvoice(self, event=None):
        try:
            with open("config/config.yaml", "r") as yamlfile:
                data = yaml.load(yamlfile, Loader=yaml.FullLoader)
                selection = str(self.QRISlistbox.get())
                if selection == 'Domestik':
                    NetzmeKey = data[0]['Details']['QRIS']['KeyDomestik']
                    urllinkQRInv = 'https://tokoapi-stg.netzme.com/qr/payment'
                elif selection == 'Cross Border':
                    NetzmeKey = data[0]['Details']['QRIS']['KeyCrossBorder']
                    urllinkQRInv = 'https://tokoapi-stg.netzme.com/qr/cb/payment'
                elif selection == 'Check Status Domestik':
                    NetzmeKey = data[0]['Details']['QRIS']['KeyDomestik']
                    urllinkQRInv = 'https://tokoapi-stg.netzme.com/qr/check'
                elif selection == 'Check Status Cross Border':
                    NetzmeKey = data[0]['Details']['QRIS']['KeyCrossBorder']
                    urllinkQRInv = 'https://tokoapi-stg.netzme.com/qr/cb/check'
                elif selection == 'ArtaJasa':
                    NetzmeKey = data[0]['Details']['QRIS']['KeyCrossBorder']
                    urllinkQRInv = 'https://tokoapi-stg.netzme.com/api/kare-aj/qr/payment/generic'
                elif selection == 'Check Status ArtaJasa':
                    NetzmeKey = data[0]['Details']['QRIS']['KeyCrossBorder']
                    urllinkQRInv = 'https://tokoapi-stg.netzme.com/api/kare-aj/qr/check/generic'
                self.key_url.clear()
                self.key_url.append(NetzmeKey)
                self.key_url.append(urllinkQRInv)
            bdy = self.getQRISInvoiceContent()
            bodyr = jsonParser.jsonParserBeautify(bdy)
            self.textbodyqrisInv.delete('1.0', tk.END)
            self.textbodyqrisInv.insert(tk.END, str(bodyr))
            #self.generateHMACInvoice()
        except ValueError as er:
            print(er)

    def payQRISInvoice(self, event=None):
        try:
            on_off_us = str(self.OnOffusCombobox.get())
            if on_off_us == "On Us":
                header = {"Authorization": "Basic c2t5ZmVlZDpza3lmZWVkKio="}
                urls = 'https://api-stg.netzme.com/internal/payment/aggregator/qr/pay'
                body = jsonParser.jsonParserMinify(self.textbodyqrisInv.get("1.0",'end-1c'))
                post_response = Modules.make_http_request(url=urls, headers=header, body_request=body)
                if post_response:
                    http_status_code = post_response[0]
                    response_message = post_response[1]
                    response_message = jsonParser.jsonParserBeautify(response_message)
                    msgbox = f"HTTP Status Code: {http_status_code}\nResponse Message: {response_message}"
                    ResponseOpenAPI(msgbox)
            else:
                selection = str(self.QRISlistbox.get())
                NetzmeKey = self.key_url[0]
                urllinkQRInv = self.key_url[1]
                getbd = json.loads(self.textbodyqrisInv.get("1.0",'end-1c'))
                if selection == 'ArtaJasa' or selection == 'Check Status ArtaJasa':
                    post_response = Modules.POSThttpHeadersQRISAJ(urllinkQRInv, getbd, NetzmeKey)
                else:
                    post_response = Modules.POSThttpHeadersQRIS(urllinkQRInv, getbd, NetzmeKey)
                    messagebox.showinfo('Response', str(post_response))
            print(post_response)
        except IndexError:
            messagebox.showinfo('Response', 'Please select data first')
        except ValueError as error:
            ResponseOpenAPI(str(error))

    def generateHMACInvoice(self, event=None):
        try:
            NetzmeKey = self.key_url[0]
            bdy = json.loads(self.textbodyqrisInv.get("1.0",'end-1c'))
            jsonString = json.dumps(bdy)
            hash = Modules.HashSHA256(str(jsonString),NetzmeKey).upper()
            self.shamacInvoiceQRIS.delete(0, tk.END)
            self.shamacInvoiceQRIS.insert(tk.END, str(hash))
        except:
            pass
    
    def bodyQRInvoice(self, *args, **kwargs):
        check_list = self.OnOffusCombobox.get()
        if check_list == 'On Us':
            self.generate_body_on_us()
        else:
            self.generate_QRInvoice()
    
    def generate_body_on_us(self, *args, **kwargs):
        try:
            selectedItem = self.MtreeInvoiceQRIS.selection()[0]
            selected_item_values = self.MtreeInvoiceQRIS.item(selectedItem)['values']
            uuid = Modules.generateUUID()
            qrcodes = str(selected_item_values[4])#qr_content
            invoiceAmount = str(selected_item_values[3])
            user_id = str(self.EnUserId.get())
            pin = str(self.EnPin.get())
            s = 'R!we8~#2K*6PYf{y'
            rawpin = Modules.HashSHA256(pin + s)
            body = {"requestId":uuid,"type":"aggregator_pay_qr","body":{"userId":user_id,"qrContent":qrcodes,"amount":invoiceAmount,"aggregatorId":"purba_snap","hashPin":rawpin}}
            bdyString = jsonParser.jsonParserBeautify(body)
            self.textbodyqrisInv.delete('1.0', tk.END)
            self.textbodyqrisInv.insert(tk.END, str(bdyString))
            self.generate_image_qr()
        except IndexError as e:
            pass

    def getQRISInvoiceContent(self, event=None):
        try:
            selection = str(self.QRISlistbox.get())
            selectedItem = self.MtreeInvoiceQRIS.selection()[0]
            selected_item_values = self.MtreeInvoiceQRIS.item(selectedItem)['values']
            invoice_id = selected_item_values[0]
            invoice_transaction_id = selected_item_values[1]
            merchant_name = selected_item_values[2]
            invoiceAmount = str(selected_item_values[3])
            qrcodes = selected_item_values[4]
            mpan = str(selected_item_values[5])
            mtype = selected_item_values[6]
            mId = selected_item_values[7]
            mcity = selected_item_values[8]
            mposcode = selected_item_values[9]
            mnamelong = selected_item_values[11]
            mcriteria = selected_item_values[10]
            terminals = selected_item_values[12]
            uuid = Modules.generateUUID()
            rrn = Modules.random_string(12).upper()
            costumerdata = str(invoice_id)
            datesec = Modules.DateNowSec()
            datenowtgl = Modules.generate_date()
            customerPan = '93600911' + Modules.RandomDigit(11)

            resultss = re.search('0703A0108(.*)99420002000132', qrcodes).group(1)
            invoicetrx = '0703A0108' + str(resultss) + '99420002000132' + str(invoice_transaction_id)
            
            if selection == 'Domestik':
                bodyreq = {"pan": str(mpan), "processingCode":"260000", "transactionAmount": str(invoiceAmount), "transmissionDateTime": datesec, "systemTraceAuditNumber": "123456","localTransactionDateTime": datesec,"settlementDate": datenowtgl,"captureDate": datenowtgl,"merchantType": str(mtype),"posEntryMode": "011","feeType": "C","feeAmount": 0,"acquirerId": "93600814","issuerId": "93600911","forwardingId": "008","rrn":str(rrn),"approvalCode": "121212","terminalId": str(terminals),"merchantId": str(mId),"merchantName": str(merchant_name),"merchantCity": str(mcity),"merchantCountry": "62","productIndicator": "Q001","customerData": str(costumerdata),"merchantCriteria": str(mcriteria),"currencyCode": "360","postalCode": str(mposcode),"additionalField": str(invoicetrx),"customerPan": str(customerPan)}
            elif selection == 'Cross Border':
                bodyreq = {"msgId": datesec + "123456360004123456233459","pan": str(mpan),"processingCode": "260000","transactionAmount": str(invoiceAmount),"settlementAmount": str(invoiceAmount),"cardholderAmount":"50000","transmissionDateTime": datesec,"settlementRate": "1","cardholderRate": "500","systemTraceAuditNumber": "123456","localTransactionDateTime": datesec,"settlementDate": datenowtgl,"captureDate": datenowtgl,"merchantType": str(mtype),"posEntryMode": "011","feeType": "C","feeAmount": 0,"acquirerId": "93600814","issuerId": "97640922","forwardingId": "008","rrn": str(rrn),"approvalCode": "121212","terminalId": str(terminals),"merchantId": str(mId),"merchantName": str(merchant_name),"merchantCity": str(mcity),"merchantCountry": "62","productIndicator": "Q001","customerData": str(costumerdata),"merchantCriteria": str(mcriteria),"currencyCode": "764","settlementCurrCode": "764","cardholderCurrCode": "360","postalCode": str(mposcode),"additionalField": str(invoicetrx),"customerPan": str(customerPan),"additionalData": "0002010102122654000200011893600153019"}
            elif selection == 'Check Status Domestik':
                bodyreq = {"pan": str(mpan), "processingCode":"360000", "transactionAmount": str(invoiceAmount), "transmissionDateTime": datesec, "systemTraceAuditNumber": "123456","localTransactionDateTime": datesec,"settlementDate": datenowtgl,"captureDate": datenowtgl,"merchantType": str(mtype),"posEntryMode": "011","feeType": "C","feeAmount": 0,"acquirerId": "93600814","issuerId": "93600911","forwardingId": "008","rrn":str(rrn),"approvalCode": "121212","terminalId": str(terminals),"merchantId": str(mId),"merchantName": str(merchant_name),"merchantCity": str(mcity),"merchantCountry": "62","productIndicator": "Q001","customerData": str(costumerdata),"merchantCriteria": str(mcriteria),"currencyCode": "360","postalCode": str(mposcode),"additionalField": str(invoicetrx),"customerPan": str(customerPan)}
            elif selection == 'Check Status Cross Border':
                bodyreq = {"msgId": datesec + "123456360004123456233459","pan": str(mpan),"processingCode": "360000","transactionAmount": str(invoiceAmount),"settlementAmount": str(invoiceAmount),"cardholderAmount":"50000","transmissionDateTime": datesec,"settlementRate": "1","cardholderRate": "500","systemTraceAuditNumber": "123456","localTransactionDateTime": datesec,"settlementDate": datenowtgl,"captureDate": datenowtgl,"merchantType": str(mtype),"posEntryMode": "011","feeType": "C","feeAmount": 0,"acquirerId": "93600814","issuerId": "97640922","forwardingId": "008","rrn": str(rrn),"approvalCode": "121212","terminalId": str(terminals),"merchantId": str(mId),"merchantName": str(merchant_name),"merchantCity": str(mcity),"merchantCountry": "62","productIndicator": "Q001","customerData": str(costumerdata),"merchantCriteria": str(mcriteria),"currencyCode": "764","settlementCurrCode": "764","cardholderCurrCode": "360","postalCode": str(mposcode),"additionalField": str(invoicetrx),"customerPan": str(customerPan),"additionalData": "0002010102122654000200011893600153019"}
            elif selection == 'ArtaJasa':
                bodyreq = {"acquirerId":"93600814","additionalField":str(invoicetrx),"approvalCode":"069547","captureDate":str(datenowtgl),"currencyCode":"360","customerData":str(costumerdata),"customerPan":str(customerPan),"feeAmount":0,"feeType":"C","forwardingId":"360001","issuerId":"93600987","localTransactionDateTime":str(datesec),"merchantCity":str(mcity),"merchantCountry":"ID","merchantCriteria":str(mcriteria),"merchantId":str(mId),"merchantName":str(merchant_name),"merchantType":str(mtype),"msgId":str(uuid),"paidAmount":str(invoiceAmount),"pan":str(mpan),"posEntryMode":"011","postalCode":str(mposcode),"processingCode":"262000","productIndicator":"Q001","rrn":str(rrn),"rrnOrigin":str(rrn),"settlementDate":str(datenowtgl),"systemTraceAuditNumber":"033462","terminalId":str(terminals),"transactionAmount":str(invoiceAmount),"transmissionDateTime":str(datesec)}
            elif selection == 'Check Status ArtaJasa':
                bodyreq = {"acquirerId":"93600814","additionalField":str(invoicetrx),"approvalCode":"069547","captureDate":str(datenowtgl),"currencyCode":"360","customerData":str(costumerdata),"customerPan":str(customerPan),"feeAmount":0,"feeType":"C","forwardingId":"360001","issuerId":"93600987","localTransactionDateTime":str(datesec),"merchantCity":str(mcity),"merchantCountry":"ID","merchantCriteria":str(mcriteria),"merchantId":str(mId),"merchantName":str(merchant_name),"merchantType":str(mtype),"msgId":str(uuid),"pan":str(mpan),"posEntryMode":"011","postalCode":str(mposcode),"processingCode":"362000","productIndicator":"Q001","rrn":str(rrn),"settlementDate":str(datenowtgl),"systemTraceAuditNumber":"033462","terminalId":str(terminals),"transactionAmount":str(invoiceAmount),"transmissionDateTime":str(datesec)}
            bodyreqstr = json.dumps(bodyreq)
            self.generate_image_qr()
            return str(bodyreqstr)
        except IndexError:
            pass

    def generate_image_qr(self):
        try:
            selectedItem = self.MtreeInvoiceQRIS.selection()[0]
            qrcodes2 = self.MtreeInvoiceQRIS.item(selectedItem)['values'][4]  # qr_content
            if qrcodes2:
                # Buat QR code
                qr = qrcode.QRCode(version=1, box_size=1, border=0)
                qr.add_data(qrcodes2)
                qr.make(fit=True)

                # Buat gambar QR
                img = qr.make_image(fill_color="black", back_color="white")

                # Resize gambar ke ukuran yang diinginkan
                img_resized = Image.new('RGB', self.display_size, color='white')
                qr_img = img.resize(self.qr_size, Image.NEAREST)
                paste_pos = ((self.display_size[0] - self.qr_size[0]) // 2,
                            (self.display_size[1] - self.qr_size[1]) // 2)
                img_resized.paste(qr_img, paste_pos)

                # Konversi ke PhotoImage
                photo = ImageTk.PhotoImage(img_resized)

                # Tampilkan di label
                self.img_qrinvoicelbl.config(image=photo)
                self.img_qrinvoicelbl.image = photo
            else:
                # Jika tidak ada QR code, tampilkan label kosong dengan ukuran yang sama
                blank_image = Image.new('RGB', self.display_size, color='white')
                photo = ImageTk.PhotoImage(blank_image)
                self.img_qrinvoicelbl.config(image=photo)
                self.img_qrinvoicelbl.image = photo
        except:
            pass