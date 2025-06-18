# app/tabs/qr_subtabs/merchant_tab.py
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import json
import yaml
import threading
import qrcode
from datetime import datetime, date, timedelta, timezone
from app.custom.custom_text import CustomText
from app.custom.custom_treeview import CustomTreeview
from src.modules import Modules
from src.jsonParser import jsonParser
from src.QRGenerate import QRGenerate
from app.tabs.popup import ResponseOpenAPI

class MerchantTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.create_widgets()
        self.layout_widgets()
        self.key_url = []
        self.on_mode_change(None)

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
        self.create_qris_merchant_listbox()
        self.create_treeview()
        self.create_input_fields()
        self.create_buttons()
        self.create_text_area()
        
        # Add shamacQRISMerc
        self.shamacQRISMerc = ttk.Entry(self.right_frame)

        # Add aggregatorId entry
        self.aggregator_id_var = tk.StringVar()
        self.aggregator_id_entry = ttk.Entry(self.right_frame, textvariable=self.aggregator_id_var)
        self.aggregator_id_var.trace_add("write", self.update_qr_content)

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
        
        self.Mtree.grid(row=0, column=0, sticky="nsew", pady=10)
        self.shamacQRISMerc.grid(row=1, column=0, sticky="ew", pady=5)

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
        self.QRISMerchantlistbox.grid(row=1, column=0, pady=5, sticky="ew")

        # Add aggregator_id_entry to the layout
        self.aggregator_id_entry.grid(row=4, column=1, sticky="ew", padx=5, pady=2)
        tk.Label(self.right_frame, text="Aggregator ID").grid(row=4, column=0, sticky="e", padx=5, pady=2)

        # Right frame layout
        self.right_frame.columnconfigure(0, weight=1)
        self.right_frame.columnconfigure(1, weight=1)
        self.right_frame.rowconfigure(9, weight=1)  # Memberikan weight pada row textbodyQrisMerc
        
        self.layout_input_fields()
        self.layout_buttons()
        
        # Adjust the row number for textbodyQrisMerc
        self.textbodyQrisMerc.grid(row=10, column=0, columnspan=2, sticky="nsew", pady=10)
        self.shamacQRISMerc.grid(row=11, column=0, columnspan=2, sticky="ew", pady=5)

        # Menyesuaikan ukuran right_frame
        self.right_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

    def create_treeview(self):
        columns = ('merchant_pan', 'nmid', 'merchant_id', 'qr_content_static',
                   'merchant_type', 'merchant_city', 'postal_code', 'merchant_name_long',
                   'merchant_name', 'merchant_criteria', 'country_code', 'rev_domain', 'created_by',
                   'created_date', 'updated_by', 'updated_date', 'active', 'qr_static_path',
                   'global_unique', 'status', 'ms_user_id', 'ms_user_id_lt', 'nmid_lt', 'merchant_name_lt')
        self.Mtree = CustomTreeview(self.left_frame, columns=columns, show='headings', height=10)
        self.Mtree["displaycolumns"] = ('merchant_pan', 'nmid', 'merchant_id', 'merchant_name', 'qr_content_static', 'qr_static_path')
        for col in columns:
            self.Mtree.heading(col, text=col)
            self.Mtree.column(col, width=100, anchor=tk.W)
        self.Mtree.bind("<<TreeviewSelect>>", self.on_treeview_select)

    def create_qris_merchant_listbox(self):
        self.qris_merchant_var = tk.StringVar(value='Domestik')
        self.QRISMerchantlistbox = ttk.Combobox(self.frame_A2, textvariable=self.qris_merchant_var, 
                                                values=['Domestik', 'Cross Border', 'ArtaJasa', 
                                                        'Check Status Domestik', 'Check Status Cross Border', 
                                                        'Check Status ArtaJasa'],
                                                state="readonly")
        self.QRISMerchantlistbox.bind("<<ComboboxSelected>>", self.update_qr_content)

    def validate_pin(self, P):
        if len(P) <= 6 and P.isdigit() or P == "":
            return True
        return False

    def create_qr_display(self):
        self.qr_size = (195, 195)
        self.display_size = (200, 200)
        self.img_frame = ttk.Frame(self.frame_A1, width=self.display_size[0], height=self.display_size[1])
        self.img_qrlbl = tk.Label(self.img_frame)
        self.img_qrlbl.grid(row=0, column=0, sticky="nsew")
        self.img_frame.grid_propagate(False)

    def create_mode_selector(self):
        self.mode_var = tk.StringVar(value='Off Us')
        self.OnOffusCombobox = ttk.Combobox(self.frame_A2, textvariable=self.mode_var, values=['Off Us', 'On Us'], state="readonly")
        self.OnOffusCombobox.bind("<<ComboboxSelected>>", self.on_mode_change)

    def create_input_fields(self):
        self.amount_var = tk.StringVar()
        self.terminal_var = tk.StringVar()
        self.user_id_var = tk.StringVar()
        self.pin_var = tk.StringVar()

        self.amount_entry = ttk.Entry(self.right_frame, textvariable=self.amount_var)
        self.terminal_entry = ttk.Entry(self.right_frame, textvariable=self.terminal_var)
        self.user_id_entry = ttk.Entry(self.right_frame, textvariable=self.user_id_var)
        vcmd = (self.register(self.validate_pin), '%P')
        self.pin_entry = ttk.Entry(self.right_frame, textvariable=self.pin_var, show="*", validate="key", validatecommand=vcmd)
            
        for var in (self.amount_var, self.terminal_var, self.user_id_var, self.pin_var):
            var.trace_add("write", self.update_qr_content)

    def layout_input_fields(self):
        fields = [
            ("Amount", self.amount_entry),
            ("Terminal ID", self.terminal_entry),
            ("User ID", self.user_id_entry),
            ("PIN", self.pin_entry)
        ]
        for i, (label, entry) in enumerate(fields):
            tk.Label(self.right_frame, text=label).grid(row=i, column=0, sticky="e", padx=5, pady=2)
            entry.grid(row=i, column=1, sticky="ew", padx=5, pady=2)

    def create_buttons(self):
        self.load_qr_button = ttk.Button(self.right_frame, text="Load QR", command=self.start_thread_connection)
        self.save_qr_code_button = ttk.Button(self.right_frame, text="Save QR Code", command=self.GenerateQRCode, state='disabled')
        self.save_qr_image_button = ttk.Button(self.right_frame, text="Save QR Image", command=self.imageQRSave, state='disabled')
        self.pay_qr_button = ttk.Button(self.right_frame, text="Pay QR", command=self.payQRISMerchant, state='disabled')

    def layout_buttons(self):
        buttons = [self.load_qr_button, self.save_qr_code_button, self.save_qr_image_button, self.pay_qr_button]
        for i, button in enumerate(buttons):
            button.grid(row=i+6, column=0, columnspan=2, sticky="ew", padx=5, pady=2)

    def create_text_area(self):
        self.textbodyQrisMerc = CustomText(self.right_frame, width=40, height=20)  # Meningkatkan height
        self.textbodyQrisMerc.bind("<<TextModified>>", self.generateHMACQRIS)

    def on_mode_change(self, event):
        mode = self.mode_var.get()
        if mode == 'On Us':
            self.user_id_entry.grid()
            self.pin_entry.grid()
            self.aggregator_id_entry.grid()
            self.QRISMerchantlistbox.grid_remove()
            self.shamacQRISMerc.grid_remove()
        else:
            self.user_id_entry.grid_remove()
            self.pin_entry.grid_remove()
            self.aggregator_id_entry.grid_remove()
            self.QRISMerchantlistbox.grid()
            self.shamacQRISMerc.grid()
        self.update_qr_content()

    def update_qr_content(self, *args):
        try:
            selectedItem = self.Mtree.selection()[0]
            mode = self.mode_var.get()
            if mode == 'On Us':
                self.generate_body_on_us()
            else:
                self.generate_QR()
        except IndexError:
            pass

    def on_treeview_select(self, event):
        self.update_qr_content()
        self.generate_image_qr()

    def start_thread_connection(self):
        self.load_qr_button.config(state=tk.DISABLED)
        thread = threading.Thread(target=self.onLoadQRMerchant)
        thread.start()

    def onLoadQRMerchant(self):
        try:
            quiru = "SELECT * FROM qris_merchant order by nmid desc;"
            ans = Modules.ConnectDBMerchant(quiru)

            self.save_qr_code_button.config(state='normal')
            self.save_qr_image_button.config(state='normal')

            self.Mtree.delete(*self.Mtree.get_children())

            for row in ans:
                self.Mtree.insert('', tk.END, values=row)

            self.load_qr_button.config(state=tk.NORMAL)
            self.pay_qr_button.config(state='normal')
        except IndexError as err:
            ResponseOpenAPI(str(err))
        except ValueError as error:
            ResponseOpenAPI(str(error))

    def GenerateQRCode(self):
        try:
            selectedItem = self.Mtree.selection()[0]
            selectedMerch = self.Mtree.item(selectedItem)['values'][2]
            messagebox.showinfo('Response', str(QRGenerate.update_qr(selectedMerch)))
            self.onLoadQRMerchant()
        except IndexError:
            messagebox.showinfo('Response', 'Please select data first')

    def imageQRSave(self):
        try:
            selectedItem = self.Mtree.selection()[0]
            selectedMerch = self.Mtree.item(selectedItem)['values'][2]
            nmid = str(self.Mtree.item(selectedItem)['values'][1]) + '_A01'
            f = filedialog.asksaveasfile(mode='w', defaultextension=".jpg", initialfile=nmid)
            if f is None:
                return
            QRGenerate.saveQR(selectedMerch, f)
            f.close()
        except IndexError:
            messagebox.showinfo('Response', 'Please select data first')

    def payQRISMerchant(self):
        try:
            mode = self.mode_var.get()
            if mode == 'On Us':
                pin = self.pin_var.get()
                if len(pin) < 6:
                    messagebox.showwarning('Warning', 'PIN harus 6 digit!')
                    return
                header = {"Authorization": "Basic c2t5ZmVlZDpza3lmZWVkKio="}
                urls = 'https://api-stg.netzme.com/internal/payment/aggregator/qr/pay'
                body = jsonParser.jsonParserMinify(self.textbodyQrisMerc.get("1.0", 'end-1c'))
                response = Modules.make_http_request(url=urls, headers=header, body_request=body)
                if response:
                    http_status_code, response_message = response
                    response_message = jsonParser.jsonParserBeautify(response_message)
                    msgbox = f"HTTP Status Code: {http_status_code}\nResponse Message: {response_message}"
                    ResponseOpenAPI(msgbox)
            else:
                NetzmeKeyMerc, urllinkQRInvMerc = self.key_url
                getbd = json.loads(self.textbodyQrisMerc.get("1.0", 'end-1c'))
                selection = str(self.QRISMerchantlistbox.get())
                print(f'{selection}\n{urllinkQRInvMerc}\n{getbd}\n{NetzmeKeyMerc}')
                if selection == 'ArtaJasa' or selection == 'Check Status ArtaJasa':
                    post_response = Modules.POSThttpHeadersQRISAJ(urllinkQRInvMerc, getbd, NetzmeKeyMerc)
                else:
                    post_response = Modules.POSThttpHeadersQRIS(urllinkQRInvMerc, getbd, NetzmeKeyMerc)
                messagebox.showinfo('Response', str(post_response))
        except IndexError:
            messagebox.showinfo('Response', 'Please select data first')

    def generate_QR(self):
        try:
            with open("config/config.yaml", "r") as yamlfile:
                data = yaml.load(yamlfile, Loader=yaml.FullLoader)
                selection = self.qris_merchant_var.get()
                if selection == 'Domestik':
                    NetzmeKeyMerc = data[0]['Details']['QRIS']['KeyDomestik']
                    urllinkQRInvMerc = 'https://tokoapi-stg.netzme.com/qr/payment'
                elif selection == 'Cross Border':
                    NetzmeKeyMerc = data[0]['Details']['QRIS']['KeyCrossBorder']
                    urllinkQRInvMerc = 'https://tokoapi-stg.netzme.com/qr/cb/payment'
                elif selection == 'Check Status Domestik':
                    NetzmeKeyMerc = data[0]['Details']['QRIS']['KeyDomestik']
                    urllinkQRInvMerc = 'https://tokoapi-stg.netzme.com/qr/check'
                elif selection == 'Check Status Cross Border':
                    NetzmeKeyMerc = data[0]['Details']['QRIS']['KeyCrossBorder']
                    urllinkQRInvMerc = 'https://tokoapi-stg.netzme.com/qr/cb/check'
                elif selection == 'ArtaJasa':
                    NetzmeKeyMerc = data[0]['Details']['QRIS']['KeyCrossBorder']
                    urllinkQRInvMerc = 'https://tokoapi-stg.netzme.com/api/kare-aj/qr/payment/generic'
                elif selection == 'Check Status ArtaJasa':
                    NetzmeKeyMerc = data[0]['Details']['QRIS']['KeyCrossBorder']
                    urllinkQRInvMerc = 'https://tokoapi-stg.netzme.com/api/kare-aj/qr/check/generic'
                self.key_url = [NetzmeKeyMerc, urllinkQRInvMerc]

            selectedItem = self.Mtree.selection()[0]
            bdy = self.getQRISMerchantContent()
            bdyString = jsonParser.jsonParserBeautify(bdy)
            self.textbodyQrisMerc.delete('1.0', tk.END)
            self.textbodyQrisMerc.insert(tk.END, str(bdyString))
            self.generate_image_qr()
        except Exception as e:
            print(f"Error in generate_QR: {e}")

    def generate_image_qr(self):
        try:
            selectedItem = self.Mtree.selection()[0]
            qrcodes2 = self.Mtree.item(selectedItem)['values'][3]  # qr_content
            if qrcodes2:
                qr = qrcode.QRCode(version=1, box_size=1, border=0)
                qr.add_data(qrcodes2)
                qr.make(fit=True)

                img = qr.make_image(fill_color="black", back_color="white")

                img_resized = Image.new('RGB', self.display_size, color='white')
                qr_img = img.resize(self.qr_size, Image.NEAREST)
                paste_pos = ((self.display_size[0] - self.qr_size[0]) // 2,
                            (self.display_size[1] - self.qr_size[1]) // 2)
                img_resized.paste(qr_img, paste_pos)

                photo = ImageTk.PhotoImage(img_resized)

                self.img_qrlbl.config(image=photo)
                self.img_qrlbl.image = photo
            else:
                blank_image = Image.new('RGB', self.display_size, color='white')
                photo = ImageTk.PhotoImage(blank_image)
                self.img_qrlbl.config(image=photo)
                self.img_qrlbl.image = photo
        except:
            pass

    def generateHMACQRIS(self, events=None):
        try:
            NetzmeKeyMerc = self.key_url[0]
            bodyjson = self.textbodyQrisMerc.get("1.0", "end-1c")
            bdy2 = json.loads(bodyjson)
            jsonString = json.dumps(bdy2)
            hash = Modules.HashSHA256(str(jsonString), NetzmeKeyMerc).upper()
            self.shamacQRISMerc.delete(0, tk.END)
            self.shamacQRISMerc.insert(tk.END, str(hash))
        except:
            pass

    def getQRISMerchantContent(self):
        try:
            selectedItem = self.Mtree.selection()[0]
            values = self.Mtree.item(selectedItem)['values']
            mpan, nmid, mercId, qcs, mtype, mcity, mposcode, mnamelong, mname, mcrits, countrycode, revdom, creatby, createdate, updateby, updatedat, act, qrsp, globun, stats, muserid, museridlt, nmidlt, mnamelt = values[:24]

            mcriteria = str(mcrits)
            invoiceAmount = self.amount_var.get()
            terminals = self.terminal_var.get()
            uuid = Modules.generateUUID()
            rrn = Modules.random_string(12).upper()
            costumerdata = f"Payment QRIS statis {mercId} using Tools Off Us"
            costumerdataCS = f"CheckStatus QRIS statis {mercId} using Tools Off Us"
            datesec = Modules.DateNowSec()
            datenowtgl = Modules.generate_date()
            datenowtgl_aj = datenowtgl[4:]

            date_obj = datetime.strptime(datenowtgl, '%Y%m%d')
            new_date_obj = date_obj + timedelta(days=1)
            formatted_value_aj = new_date_obj.strftime('%m%d')

            customerPan = '93600911' + Modules.RandomDigit(11)

            selection = self.qris_merchant_var.get()
            if selection == 'Domestik':
                bodyreq = {"pan": str(mpan),"processingCode": "260000","transactionAmount": str(invoiceAmount),"transmissionDateTime": str(datesec),"systemTraceAuditNumber": "123456","localTransactionDateTime": str(datesec),"settlementDate": str(datenowtgl),"captureDate": str(datenowtgl),"merchantType": str(mtype),"posEntryMode": "011","feeType": "C","feeAmount": 0,"acquirerId": "93600814","issuerId": "93600911","forwardingId": "008","rrn": str(rrn),"approvalCode": "121212","terminalId": str(terminals),"merchantId": str(nmid),"merchantName": str(mname),"merchantCity": str(mcity),"merchantCountry": "62","productIndicator": "Q001","customerData": str(costumerdata),"merchantCriteria": str(mcriteria),"currencyCode": "360","postalCode": str(mposcode),"additionalField": "","customerPan": str(customerPan)}
            elif selection == 'Cross Border':
                bodyreq = {"msgId": datesec + "123456360004123456233459","pan": str(mpan),"processingCode": "260000","transactionAmount": str(invoiceAmount),"settlementAmount": str(invoiceAmount),"cardholderAmount": str(invoiceAmount),"transmissionDateTime": str(datesec),"settlementRate": "1","cardholderRate": "500","systemTraceAuditNumber": "123456","localTransactionDateTime": str(datesec),"settlementDate": str(datenowtgl),"captureDate": str(datenowtgl),"merchantType": str(mtype),"posEntryMode": "011","feeType": "C","feeAmount": 0,"acquirerId": "93600814","issuerId": "97640922","forwardingId": "008","rrn": str(rrn),"approvalCode": "121212","terminalId": str(terminals),"merchantId": str(nmid),"merchantName":str(mname),"merchantCity": str(mcity),"merchantCountry": "62","productIndicator": "Q001","customerData": str(costumerdataCS),"merchantCriteria": str(mcriteria),"currencyCode": "764","settlementCurrCode": "764","cardholderCurrCode": "360","postalCode": str(mposcode),"additionalField": "","customerPan": str(customerPan),"additionalData": "0002010102122654000200011893600153019"}
            elif selection == 'Check Status Domestik':
                bodyreq = {"pan": str(mpan), "processingCode":"360000", "transactionAmount": str(invoiceAmount),"transmissionDateTime": str(datesec),"systemTraceAuditNumber": "123456","localTransactionDateTime": str(datesec),"settlementDate": str(datenowtgl),"captureDate": str(datenowtgl),"merchantType": str(mtype),"posEntryMode": "011","feeType": "C","feeAmount": 0,"acquirerId": "93600814","issuerId": "93600911","forwardingId": "008","rrn":str(rrn),"approvalCode": "121212","terminalId": str(terminals),"merchantId": str(nmid),"merchantName": str(mname),"merchantCity": str(mcity),"merchantCountry": "62","productIndicator": "Q001","customerData": str(costumerdata),"merchantCriteria": str(mcriteria),"currencyCode": "360","postalCode": str(mposcode),"additionalField": "","customerPan": str(customerPan)}
            elif selection == 'Check Status Cross Border':
                bodyreq = {"msgId": datesec + "123456360004123456233459","pan": str(mpan),"processingCode": "360000","transactionAmount": str(invoiceAmount),"settlementAmount": str(invoiceAmount),"cardholderAmount": str(invoiceAmount),"transmissionDateTime": str(datesec),"settlementRate": "1","cardholderRate": "500","systemTraceAuditNumber": "123456","localTransactionDateTime": str(datesec),"settlementDate": str(datenowtgl),"captureDate": str(datenowtgl),"merchantType": str(mtype),"posEntryMode": "011","feeType": "C","feeAmount": 0,"acquirerId": "93600814","issuerId": "97640922","forwardingId": "008","rrn": str(rrn),"approvalCode": "121212","terminalId": str(terminals),"merchantId": str(nmid),"merchantName": str(mname),"merchantCity": str(mcity),"merchantCountry": "62","productIndicator": "Q001","customerData": str(costumerdataCS),"merchantCriteria": str(mcriteria),"currencyCode": "764","settlementCurrCode": "764","cardholderCurrCode": "360","postalCode": str(mposcode),"additionalField": "","customerPan": str(customerPan),"additionalData": "0002010102122654000200011893600153019"}
            elif selection == 'ArtaJasa':
                bodyreq = {"acquirerId":"93600814","additionalField":"0703A01","approvalCode":"069547","captureDate":str(datenowtgl_aj),"currencyCode":"360","customerData":str(costumerdata),"cardholderAmount": 0,"cardholderCurrCode": "","cardholderRate":0,"conversionDate":"","customerPan":str(customerPan),"feeAmount":0,"feeType":"C","forwardingId":"360001","issuerId":"93600987","localTransactionDateTime":str(datesec),"merchantCity":str(mcity),"merchantCountry":"ID","merchantCriteria":str(mcriteria),"merchantId":str(nmid),"merchantName":str(mname),"merchantType":str(mtype),"msgId":str(uuid),"pan":str(mpan),"posEntryMode":"011","postalCode":str(mposcode),"processingCode":"262000","productIndicator":"Q001","rrn":str(rrn),"settlementDate":str(formatted_value_aj),"settlementRate": 0,"settlementAmount": 0,"settlementCurrCode": "","systemTraceAuditNumber":"033462","terminalId":str(terminals),"transactionAmount":str(invoiceAmount),"transmissionDateTime":str(datesec)}
            elif selection == 'Check Status ArtaJasa':
                bodyreq = {"acquirerId":"93600814","additionalField":"0703A01","approvalCode":"069547","captureDate":str(datenowtgl_aj),"currencyCode":"360","customerData":str(costumerdataCS),"cardholderAmount": 0,"cardholderCurrCode": "","cardholderRate":0,"conversionDate":"","customerPan":str(customerPan),"feeAmount":0,"feeType":"C","forwardingId":"360001","issuerId":"93600987","localTransactionDateTime":str(datesec),"merchantCity":str(mcity),"merchantCountry":"ID","merchantCriteria":str(mcriteria),"merchantId":str(nmid),"merchantName":str(mname),"merchantType":str(mtype),"msgId":str(uuid),"pan":str(mpan),"posEntryMode":"011","postalCode":str(mposcode),"processingCode":"362000","productIndicator":"Q001","rrn":str(rrn),"settlementDate":str(formatted_value_aj),"settlementRate": 0,"settlementAmount": 0,"settlementCurrCode": "","systemTraceAuditNumber":"033462","terminalId":str(terminals),"transactionAmount":str(invoiceAmount),"transmissionDateTime":str(datesec)}
            bodyreqstr = json.dumps(bodyreq)
            return bodyreqstr
        except IndexError:
            return "{}"

    def generate_body_on_us(self):
        try:
            selectedItem = self.Mtree.selection()[0]
            qrcodes = self.Mtree.item(selectedItem)['values'][3]  # qr_content
            invoiceAmount = self.amount_var.get()
            uuid = Modules.generateUUID()
            user_id = self.user_id_var.get()
            pin = self.pin_var.get()
            aggregator_id = self.aggregator_id_var.get()
            s = 'R!we8~#2K*6PYf{y'
            rawpin = Modules.HashSHA256(pin + s)
            body = {
                "requestId": uuid,
                "type": "aggregator_pay_qr",
                "body": {
                    "userId": user_id,
                    "qrContent": qrcodes,
                    "amount": invoiceAmount,
                    "aggregatorId": aggregator_id,
                    "hashPin": rawpin
                }
            }
            bdyString = jsonParser.jsonParserBeautify(body)
            self.textbodyQrisMerc.delete('1.0', tk.END)
            self.textbodyQrisMerc.insert(tk.END, str(bdyString))
            self.generate_image_qr()
        except IndexError:
            pass

    def update_qr_content(self, *args):
        try:
            selectedItem = self.Mtree.selection()[0]
            mode = self.mode_var.get()
            
            if mode == 'On Us':
                self.generate_body_on_us()
            else:
                self.generate_QR()
        except IndexError:
            pass

    def on_treeview_select(self, event):
        self.update_qr_content()
        self.generate_image_qr()