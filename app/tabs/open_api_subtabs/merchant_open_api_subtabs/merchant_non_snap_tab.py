# app/tabs/open_api_subtabs/merchant_open_api_subtabs/merchant_non_snap_tab.py
from tkinter import *
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from src.modules import Modules
from app.tabs.popup import ResponseOpenAPI
import json
from app.custom.custom_text import CustomText
from src.generateSignature import generateSignature
from app.custom.custom_treeview import CustomTreeview
from src.jsonParser import jsonParser
from app.custom.date_picker import DatePicker
import threading

class MerchantNonSnapTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        #self.sets_configs = Sets(parent)
        self.create_widgets()
        self.MerchantOpenAPIBody()
        self.getClearPasswordMerchant()

    def create_widgets(self):
        string_vars = [tk.StringVar() for _ in range(16)]
        (self.y1, self.y2, *other_vars) = string_vars
        self.y1.trace_add('write', lambda *args: self.on_field_MOAcbEndpointchange())

        self.MOABtnSend = ttk.Button(self, text="Send", command=self.start_thread_connection)
        self.MOABtnCheck = ttk.Button(self, text="Check", command=self.CheckTokenMerchant)
        self.MOABtnTest = ttk.Button(self, text="Test", command=self.MerchantOpenAPISign)
        self.MOABtnCreateCurl = ttk.Button(self, text="Create Curl", command=self.generate_curl)

        # Add your elements here
        self.MOAlblAggregatorId = tk.Label(self,text="AggregatorId")
        self.MOAcbAggregatorId = ttk.Combobox(self, width=55)
        self.MOAcbAggregatorId['values'] = Modules.getAllAggregatorMerchant()

        self.MOAcbAggregatorId.config(state='readonly')
        self.MOAcbAggregatorId.bind("<<ComboboxSelected>>", self.getClearPasswordMerchant)
    
        self.MOAlblClearPassword = tk.Label(self,text="ClearPassword")
        self.MOAEnClearPassword = tk.Entry(self)
        self.MOAEnClearPassword.config(state='normal')

        self.MOAlblAuthToken = tk.Label(self,text="Auth Token")
        self.MOAEnAuthToken = tk.Entry(self, width=55)
        self.MOAEnAuthToken.config(state='normal')

        self.MOAlblMerchantId = tk.Label(self,text="Merchant ID")
        self.MOAEnMerchantId = tk.Entry(self)
        self.MOAEnMerchantId.bind('<KeyRelease>', self.MerchantOpenAPIBody)

        self.MOAlblEndpoint = tk.Label(self,text="Endpoint")
        self.MOAcbEndpoint = ttk.Combobox(self, textvariable=self.y1, width=55)
        self.MOAcbEndpoint['values'] = ['Authorization','Merchant Detail', 'Get Transaction', 'Get Balance', 'Inquiry Withdraw',
                            'Submit Withdraw', 'Create PIN', 'Forgot PIN', 'Create Invoice', 'Create Invoice Transaction',
                            'Create Validated Invoice', 'Get Invoice Transaction', 'Get Qris Acquire Transaction',
                            'Create Invoice Topup Deposit', 'Get Balance Deposit', 'Get Deposit Transaction',
                            'Inquiry Withdraw Deposit', 'Submit Withdraw Deposit', 'Get Withdraw Deposit Detail',
                            'Deduct Deposit & Split Fee', 'Get Deduct Deposit Transaction', 'Send receipt']
        self.MOAcbEndpoint.config(state='readonly')

        self.MOAEnvLbl = tk.Label(self,text="Environment")
        self.MOAcbEnvironment = ttk.Combobox(self, textvariable=self.y2)
        self.MOAcbEnvironment['values'] = ['Staging','Production']
        self.MOAcbEnvironment.config(state='readonly')
        
        self.MOAlbl6 = tk.Label(self,text="Output")
        self.MOAlblRawKey = tk.Label(self,text="Raw Key")
        self.MOAEnRawKey = tk.Entry(self, width=55)
        self.MOAEnRawKey.config(state='normal')

        self.MOAlblRawSignature = tk.Label(self,text="Raw Signature")
        self.MOAEnRawSignature = tk.Entry(self, width=55)
        self.MOAEnRawSignature.config(state='normal')

        self.MOAlblSource = tk.Label(self,text="Source")
        self.MOAEnSource = tk.Entry(self, width=55)
        self.MOAEnSource.config(state='normal')
        
        self.MOAlblSignature = tk.Label(self,text="Signature")
        self.MOAEnSignature = tk.Entry(self, width=55)
        self.MOAEnSignature.config(state='normal')

        self.MOAlblRequestTime = tk.Label(self,text="Request Time")
        self.MOAEnRequestTime = tk.Entry(self, width=55)
        self.MOAEnRequestTime.config(state='normal')

        self.MOAlblAuthorization = tk.Label(self,text="Authorization")
        self.MOAEnAuthorization = tk.Entry(self, width=55)
        self.MOAEnAuthorization.config(state='normal')

        self.MOAlblBody = tk.Label(self,text="Body")
        self.MOATxtBody = CustomText(self, width=100, height=16)
        #self.MOATxtBody.bind("<<TextModified>>", self.testsign)

        self.MOAlblPhoneNumber = tk.Label(self,text="Phone No")
        self.MOAEnPhoneNumber = tk.Entry(self)
        self.MOAEnPhoneNumber.bind('<KeyRelease>', self.MerchantOpenAPIBody)

        self.MOAlblPIN = tk.Label(self,text="PIN")
        self.MOAEnPIN = tk.Entry(self)
        self.MOAEnPIN.bind('<KeyRelease>', self.MerchantOpenAPIBody)

        self.MOAlblAmountWithdraw = tk.Label(self,text="Amount")
        self.MOAEnAmountWithdraw = tk.Entry(self)
        self.MOAEnAmountWithdraw.bind('<KeyRelease>', self.MerchantOpenAPIBody)

        self.MOAlblNoRek = tk.Label(self,text="No Rek")
        self.MOAEnNoRek = tk.Entry(self)
        self.MOAEnNoRek.bind('<KeyRelease>', self.MerchantOpenAPIBody)

        self.MOAlblBankCode = tk.Label(self,text="Bank Code")
        self.MOAEnBankCode = tk.Entry(self)
        self.MOAEnBankCode.bind('<KeyRelease>', self.MerchantOpenAPIBody)

        self.MOAlblBankName = tk.Label(self,text="Nama Bank")
        self.MOAEnBankName = tk.Entry(self)
        self.MOAEnBankName.bind('<KeyRelease>', self.MerchantOpenAPIBody)

        self.MOAlblTrxId = tk.Label(self,text="Trx ID")
        self.MOAEnTrxId = tk.Entry(self)
        self.MOAEnTrxId.bind('<KeyRelease>', self.MerchantOpenAPIBody)

        self.MOAlblInvMethod = tk.Label(self,text="Method")
        self.MOAcbInvMethod = ttk.Combobox(self)
        self.MOAcbInvMethod['values'] = ['BANK_TRANSFER','QRIS','BCA','CREDIT_CARD','RETAIL_OUTLET','INDOMARET','QRIS_DINAMIS_TERMINAL','NETZME','OVO','DANA','DKI',"VA_BCA","VA_CIMB","VA_BRI","VA_BNI","VA_MANDIRI","VA_PERMATA","NETZME_SEAMLESS","VA_BCA_PZ"]
        self.MOAcbInvMethod.config(state='readonly')
        self.MOAcbInvMethod.bind("<<ComboboxSelected>>", self.MerchantOpenAPIBody)

        self.MOAlblFeeType = tk.Label(self,text="Fee Type")
        self.MOAcbFeeType = ttk.Combobox(self)
        self.MOAcbFeeType['values'] = ['on_seller','on_buyer']
        self.MOAcbFeeType.config(state='readonly')
        self.MOAcbFeeType.bind("<<ComboboxSelected>>", self.MerchantOpenAPIBody)

        self.MOAlblRRN = tk.Label(self,text="RRN")
        self.MOAEnRRN = tk.Entry(self)
        self.MOAEnRRN.bind('<KeyRelease>', self.MerchantOpenAPIBody)

        self.MOAlblToken = tk.Label(self,text="Token Callback")
        self.MOAEnToken = tk.Entry(self, width=55)
        self.MOAEnToken.bind('<KeyRelease>', self.MerchantOpenAPIBody)

        self.MOAlblTerminal = tk.Label(self,text="Terminal Id")
        self.MOAEnTerminal = tk.Entry(self)
        self.MOAEnTerminal.bind('<KeyRelease>', self.MerchantOpenAPIBody)

        self.MOAlblDate = tk.Label(self, text='Date')
        self.MOAEnDate = tk.Entry(self)
        self.MOAEnDate.bind('<KeyRelease>', self.MerchantOpenAPIBody)

        self.MOADateBtn = ttk.Button(self, text="Open Calendar", command=lambda: DatePicker(self, self.set_date))

        self.MOAcbEndpoint.bind("<<ComboboxSelected>>", self.MerchantOpenAPIBody)

        self.MOAlblRekName = tk.Label(self,text="Nama Rekening")
        self.MOAEnRekName = tk.Entry(self)
        self.MOAEnRekName.bind('<KeyRelease>', self.MerchantOpenAPIBody)

    def set_date(self, date):
        self.MerchantOpenAPIBody()
        self.MOAEnDate.delete(0, tk.END)
        self.MOAEnDate.insert(0, date)

    def getClearPasswordMerchant(self, *args):
        aggId = self.MOAcbAggregatorId.get()
        #print(aggId)
        if not self.MOAcbAggregatorId.get() == "":
            self.MOAEnClearPassword.config(state='normal')
            getstr = Modules.searchclearPassByaggregatorMerchant(aggId)[0]
            #print(getstr)
            self.MOAEnClearPassword.delete(0, END)
            self.MOAEnClearPassword.insert(tk.END, str(getstr))

    def MerchantOpenAPIBody(self, *args):
        try:
            self.showhideMerchantOpenAPIElement()
            clientId = self.MOAcbAggregatorId.get()
            selectedItem = self.MOAcbEndpoint.get() # --> selected combobox
            PhoneNumber = self.MOAEnPhoneNumber.get()
            MerchantId = self.MOAEnMerchantId.get()
            tanggalskrg = self.MOAEnDate.get()
            TrxId = self.MOAEnTrxId.get()
            requestId = Modules.generateUUID()
            rrn = self.MOAEnRRN.get()
            pinraw = self.MOAEnPIN.get()
            pin = generateSignature.genPINToko(pinraw,clientId,MerchantId)
            pmethod = str(self.MOAcbInvMethod.get())
            feetype = str(self.MOAcbFeeType.get())
            amount = self.MOAEnAmountWithdraw.get()
            NoRekening = self.MOAEnNoRek.get()
            NamaBank = self.MOAEnBankName.get()
            BankKode = self.MOAEnBankCode.get()
            NamaRekening = self.MOAEnRekName.get()
            random12num = Modules.RandomDigit(12)
            randomTrxId = Modules.generateUUID()
            terminal = self.MOAEnTerminal.get()
            if selectedItem == 'Authorization':
                #Auth token
                source = '/oauth/merchant/accesstoken'
                method = "POST"
                body = {"grant_type":"client_credentials"}
                json_formatted_str = json.dumps(body, indent=4)
                self.MOATxtBody.delete('1.0', tk.END)
                self.MOATxtBody.insert(tk.END, str(json_formatted_str))
            elif selectedItem == 'Merchant Detail':
                #Merchant Detail
                source = "/api/aggregator/merchant/qr/merchant_detail?phoneNo=" + PhoneNumber
                method = "GET"
                body = ''
                self.MOATxtBody.delete('1.0', tk.END)
                self.MOATxtBody.insert(tk.END, str(body))
            elif selectedItem == 'Get Transaction':
                #Get Transaction
                source = "/api/aggregator/merchant/qr/transaction/list?userId=" + MerchantId + "&startdate=" + tanggalskrg + "&enddate=" + tanggalskrg + ""
                method = "GET"
                body = ''
                self.MOATxtBody.delete('1.0', tk.END)
                self.MOATxtBody.insert(tk.END, str(body))
            elif selectedItem == 'Get Balance':
                #Get Balance
                source = "/api/aggregator/merchant/qr/balance/detail?userId=" + MerchantId
                method = "GET"
                body = ''
                self.MOATxtBody.delete('1.0', tk.END)
                self.MOATxtBody.insert(tk.END, str(body))
            elif selectedItem == 'Inquiry Withdraw':
                #Withdraw inquiry
                source = "/api/aggregator/merchant/qr/withdraw/inquiry"
                method = "POST"
                body = {"requestId":requestId,"type":"withdraw_inquiry","body":{"userId":MerchantId}}
                json_formatted_str = json.dumps(body, sort_keys=True, indent=4)
                tbody = json.dumps(body,separators=(',', ":"))
                self.MOATxtBody.delete('1.0', tk.END)
                self.MOATxtBody.insert(tk.END, str(json_formatted_str))
            elif selectedItem == 'Submit Withdraw':
                #withdraw process
                source = "/api/aggregator/merchant/qr/withdraw"
                method = "POST"
                body = {"requestId":requestId,"type":"submit_withdraw","body":{"userId":MerchantId,"withdrawalAmount":amount,"accountHolderName":NamaRekening,"bankAccountNumber":NoRekening,"bankName":NamaBank,"bankCode":BankKode,"pin":pin}}
                json_formatted_str = json.dumps(body, indent=2)
                self.MOATxtBody.delete('1.0', tk.END)
                self.MOATxtBody.insert(tk.END, str(json_formatted_str))
            elif selectedItem == 'Create PIN':
                #Create Pin
                source = "/api/aggregator/merchant/pin/create_pin"
                method = "POST"
                body = {"requestId":requestId,"type":"create_pin","body":{"username":MerchantId,"pin":pin}}
                json_formatted_str = json.dumps(body, indent=2)
                self.MOATxtBody.delete('1.0', tk.END)
                self.MOATxtBody.insert(tk.END, str(json_formatted_str))
            elif selectedItem == 'Forgot PIN':
                #Forgot Pin
                source = "/api/aggregator/merchant/pin/forgot_pin"
                method = "POST"
                body = {"requestId":requestId,"type":"forgot_pin","body":{"username":MerchantId}}
                json_formatted_str = json.dumps(body, indent=2)
                self.MOATxtBody.delete('1.0', tk.END)
                self.MOATxtBody.insert(tk.END, str(json_formatted_str))
            elif selectedItem == 'Create Invoice':
                #Create Invoice
                source = "/api/v1/invoice/create"
                method = "POST"
                body = {"request":{"type":"single","payment_methods":["INDOMARET","RETAIL_OUTLET","QRIS","BANK_TRANSFER","OVO","DANA","NETZME","CREDIT_CARD","DKI","VA_CIMB", "VA_BRI", "VA_BNI", "VA_MANDIRI", "VA_PERMATA"],
                                   "fee_type":feetype,"merchant":MerchantId,"amount":int(amount),"email":"purba.jati@netzme.id",
                                   "notes":"QA invoice","description":"Mencoba membuat invoice1","phone_number":"081326262654",
                                   "image_url":"","fullname":"Percobaan","expire_in_second":9000,"amount_detail":
                                   {"basicAmount":int(amount),"shippingAmount":0},"commission_percentage":0,"item_details":
                                   [{"item_id":randomTrxId,"name":"Sepatu Nike","amount":int(amount),"qty":1}]}}
                json_formatted_str = json.dumps(body, indent=2)
                self.MOATxtBody.delete('1.0', tk.END)
                self.MOATxtBody.insert(tk.END, str(json_formatted_str))
            elif selectedItem == 'Create Validated Invoice':
                #Create Validated Invoice
                source = "/api/v1/invoice/create/validated"
                method = "POST"
                body = {"request":{"merchant":MerchantId,"amount":amount,"email":"purba.jati@netzme.id","notes":"desc",
                                   "description":"description","phone_number":"+62817345545","image_url":"","fullname":"Percoba QA",
                                   "amount_detail":{"basicAmount":amount,"shippingAmount":0},
                                   "payment_method":pmethod,"commission_percentage":0,"expire_in_second":3600,"fee_type":feetype,
                                   "partner_transaction_id":clientId + "-" + random12num}}
                json_formatted_str = json.dumps(body, indent=2)
                self.MOATxtBody.delete('1.0', tk.END)
                self.MOATxtBody.insert(tk.END, str(json_formatted_str))
            elif selectedItem == 'Create Invoice Transaction':
                source = "/api/v1/invoice/createTransaction"
                method = "POST"
                paymentSelection = self.MOAcbInvMethod.get()
                if paymentSelection == 'QRIS_DINAMIS_TERMINAL':
                    body = {"request":{"merchant":MerchantId,"amount":amount,"email":"purba.jati@netzme.id",
                                    "notes":"desc","description":"description","phone_number":"+62817345545",
                                    "image_url":"","fullname":"Percoba QA",
                                    "amount_detail":{"basicAmount":amount,"shippingAmount":0},
                                    "payment_method":"QRIS","commission_percentage":0,
                                    "expire_in_second":3600,"fee_type":feetype,"terminal_id":terminal,
                                    "partner_transaction_id":clientId + "-" + random12num}}
                    json_formatted_str = json.dumps(body, indent=2)
                    self.MOATxtBody.delete('1.0', tk.END)
                    self.MOATxtBody.insert(tk.END, str(json_formatted_str))
                elif paymentSelection == 'CREDIT_CARD':
                    body = {"request":{"merchant":MerchantId,"amount":amount,"email":"purba.jati@netzme.id",
                                    "notes":"desc","description":"description","phone_number":"+62817345545",
                                    "image_url":"","fullname":"Percoba QA",
                                    "amount_detail":{"basicAmount":amount,"shippingAmount":0},
                                    "payment_method":pmethod,"commission_percentage":0,
                                    "expire_in_second":3600,"fee_type":feetype,
                                    "address":"test",
                                    "item_details":[{"name":"hello","item_id":"qwerty","qty":1,"amount":amount}],
                                    "partner_transaction_id":clientId + "-" + random12num}}
                    json_formatted_str = json.dumps(body, indent=2)
                    self.MOATxtBody.delete('1.0', tk.END)
                    self.MOATxtBody.insert(tk.END, str(json_formatted_str))
                else:
                    body = {"request":{"merchant":MerchantId,"amount":amount,"email":"purba.jati@netzme.id",
                                    "notes":"desc","description":"description","phone_number":"+62817345545",
                                    "image_url":"","fullname":"Percoba QA",
                                    "amount_detail":{"basicAmount":amount,"shippingAmount":0},
                                    "payment_method":pmethod,"commission_percentage":0,
                                    "expire_in_second":3600,"fee_type":feetype,
                                    "partner_transaction_id":clientId + "-" + random12num}}
                    json_formatted_str = json.dumps(body, indent=2)
                    self.MOATxtBody.delete('1.0', tk.END)
                    self.MOATxtBody.insert(tk.END, str(json_formatted_str))
            elif selectedItem == 'Create Invoice Topup Deposit':
                source = "/api/v1/invoice/createTransaction"
                method = "POST"
                body = {"request":{"merchant":MerchantId,"amount":amount,"email":"tetabc@gmail.com","notes":"desc",
                                   "description":"description","phone_number":"+62813293333333","image_url":"",
                                   "fullname":"TQA","amount_detail":{"basicAmount":amount,"shippingAmount":0},
                                   "payment_method":"BANK_TRANSFER","commission_percentage":0,"expire_in_second":600,
                                   "fee_type":feetype,"apiSource":"topup_deposit","partner_transaction_id":clientId + "-" + random12num}}
                json_formatted_str = json.dumps(body, indent=2)
                self.MOATxtBody.delete('1.0', tk.END)
                self.MOATxtBody.insert(tk.END, str(json_formatted_str))
            elif selectedItem == 'Get Invoice Transaction':
                #Get Invoice Transaction
                source = "/api/aggregator/merchant/invoice/transaction/" + TrxId
                method = "GET"
                body = ''
                self.MOATxtBody.delete('1.0', tk.END)
                self.MOATxtBody.insert(tk.END, str(body))
            elif selectedItem == 'Get Qris Acquire Transaction':
                #QRISacquirerTrx
                source = "/api/aggregator/merchant/qris/acquire/transaction/" + rrn
                method = "GET"
                body = ''
                self.MOATxtBody.delete('1.0', tk.END)
                self.MOATxtBody.insert(tk.END, str(body))
            elif selectedItem == 'Get Balance Deposit':
                #Get Balance Deposit
                source = '/api/aggregator/merchant/institution/balance/' + MerchantId
                method = "GET"
                body = ''
                self.MOATxtBody.delete('1.0', tk.END)
                self.MOATxtBody.insert(tk.END, str(body))
            elif selectedItem == 'Get Deposit Transaction':
                #Get Deposit Transaction
                source = "/api/aggregator/merchant/deposit/transaction/list?userId=" + MerchantId + "&startdate=" + tanggalskrg + "&enddate=" + tanggalskrg + "&page=1"
                method = "GET"
                body = ''
                self.MOATxtBody.delete('1.0', tk.END)
                self.MOATxtBody.insert(tk.END, str(body))
            elif selectedItem == 'Inquiry Withdraw Deposit':
                #Deposit Withdraw Inquiry
                source = "/api/aggregator/merchant/deposit/withdraw/inquiry?userId=" + MerchantId
                method = "GET"
                body = ''
                self.MOATxtBody.delete('1.0', tk.END)
                self.MOATxtBody.insert(tk.END, str(body))
            elif selectedItem == 'Submit Withdraw Deposit':
                #Submit Withdraw Deposit
                source = "/api/aggregator/merchant/deposit/withdraw"
                method = "POST"
                body = {"requestId":requestId,"type":"submit_withdraw","body":{"userId":MerchantId,"withdrawalAmount":amount,"accountHolderName":NamaRekening,"bankAccountNumber":NoRekening,"bankName":NamaBank,"bankCode":BankKode,"pin":pin}}
                json_formatted_str = json.dumps(body, indent=2)
                self.MOATxtBody.delete('1.0', tk.END)
                self.MOATxtBody.insert(tk.END, str(json_formatted_str))
            elif selectedItem == 'Get Withdraw Deposit Detail':
                #Get Withdraw Deposit Detail
                source = "/api/aggregator/merchant/withdraw/deposit/" + TrxId
                method = "GET"
                body = ''
                self.MOATxtBody.delete('1.0', tk.END)
                self.MOATxtBody.insert(tk.END, str(body))
            elif selectedItem == 'Deduct Deposit & Split Fee':
                #Deduct Deposit & Split Fee
                source = "/api/aggregator/merchant/payment/notif"
                method = "POST"
                body = {"requestId":requestId,"type":"payment_notification_to_split_fee","body":{"merchantId":MerchantId,"transactionId": clientId + "-" + random12num,"sku":"TIKET-" + clientId + "-" + random12num,"productName":"Tiket-" + clientId + "-" + random12num,"paymentStatus":"paid","paymentMethod":"BANK_TRANSFER","bankName":"BCA","paidAmount":"IDR "+str(amount)+".00","mdrFeeAmount":"IDR 0.00","additionals":{"desc":"beli 1 " + clientId + "-" + random12num}}}
                json_formatted_str = json.dumps(body, indent=2)
                self.MOATxtBody.delete('1.0', tk.END)
                self.MOATxtBody.insert(tk.END, str(json_formatted_str))
            elif selectedItem == 'Get Deduct Deposit Transaction':
                #Get Deduct Deposit Transaction
                source = '/public/api/v1/payment/notif/trx?request_id=' + TrxId + '&type=requestId'
                method = "GET"
                body = ''
                self.MOATxtBody.delete('1.0', tk.END)
                self.MOATxtBody.insert(tk.END, str(body))
            elif selectedItem == 'Send receipt':
                #Send receipt
                source = '/public/api/v1/createReceipt/' + MerchantId
                method = 'POST'
                body = {"requestId":requestId,"type":"create_e-receipt","body":{"language":"en","logo_url":"https://odenktools.com/wp-content/uploads/2016/09/odenktools-logos.png","receipt_send_type":"wa.me","cashier_name":"null","payment_method_name":"qris","buyer_name":"null","buyer_email":"null","buyer_phone_number":"081386860046","order_number":"89878674434","invoice_number":"null","buyer_payment_status":"paid","buyer_payment":10000,"buyer_change":0,"created_at":"2023-02-07T05:48:43.336Z","merchant_id":MerchantId,"order_items":[{"product_name":"Product Satu","quantity":2,"product_price":5000},{"product_name":"Product Dua","quantity":1,"product_price":5000}]}}
                json_formatted_str = json.dumps(body, indent=2)
                self.MOATxtBody.delete('1.0', tk.END)
                self.MOATxtBody.insert(tk.END, str(json_formatted_str))
            self.MerchantOpenAPISign()
            #self.updateFileConfig()
        except ValueError as e:
            print(str(e))

    def MerchantOpenAPISign(self, *args):
        try:
            #print('MerchantOpenAPISign')
            selected_environment = self.MOAcbEnvironment.get()
            if selected_environment == 'Production':
                baseurl = 'https://tokoapi.netzme.com'
                baseurltokonetzmeweb = 'https://pay.netzme.com'
            else:
                baseurl = 'https://tokoapi-stg.netzme.com'
                baseurltokonetzmeweb = 'https://pay-stg.netzme.com'
            clientId = self.MOAcbAggregatorId.get()
            clearPassword = self.MOAEnClearPassword.get()
            token = self.MOAEnAuthToken.get()
            tokenBearer = "Bearer " + token
            reqtime = Modules.current_milli_time()
            selectedItem = self.MOAcbEndpoint.get() # --> selected combobox
            PhoneNumber = self.MOAEnPhoneNumber.get()
            MerchantId = self.MOAEnMerchantId.get()
            tanggalskrg = self.MOAEnDate.get()
            TrxId = self.MOAEnTrxId.get()
            requestId = Modules.generateUUID()
            rrn = self.MOAEnRRN.get()
            pinraw = self.MOAEnPIN.get()
            pin = generateSignature.genPINToko(pinraw,clientId,MerchantId)
            pmethod = str(self.MOAcbInvMethod.get())
            feetype = str(self.MOAcbFeeType.get())
            amount = self.MOAEnAmountWithdraw.get()
            NoRekening = self.MOAEnNoRek.get()
            NamaBank = self.MOAEnBankName.get()
            BankKode = self.MOAEnBankCode.get()
            bod = str(self.MOATxtBody.get("1.0",'end-1c'))
            #['Authorization','Merchant Detail', 'Get Transaction', 'Get Balance', 'Inquiry Withdraw',
            #                   'Submit Withdraw', 'Create PIN', 'Forgot PIN', 'Create Invoice', 'Create Invoice Transaction',
            #                  'Create Validated Invoice', 'Get Invoice Transaction', 'Get Qris Acquire Transaction',
            #                 'Create Invoice Topup Deposit', 'Get Balance Deposit', 'Get Deposit Transaction',
                #                'Inquiry Withdraw Deposit', 'Submit Withdraw Deposit', 'Get Withdraw Deposit Detail',
                #               'Deduct Deposit & Split Fee', 'Get Deduct Deposit Transaction', 'Send receipt']
            if selectedItem == 'Merchant Detail':
                #Merchant Detail
                source = "/api/aggregator/merchant/qr/merchant_detail?phoneNo=" + PhoneNumber
                method = "GET"
                body = ''
                #plains = generateSignature.genPlainSign(source,token,reqtime,method,body)
                #signature = generateSignature.genSignatureGET(source, token, reqtime, clearPassword)
                #key = generateSignature.genKey(clearPassword,reqtime,token)
                
                lista = generateSignature.FunGenerateSignature('Merchant Detail',token,clearPassword,PhoneNumber)
                plains = lista[0]
                key = lista[1]
                signature = lista[5]
                self.changeOpenAPImerchantEntry(key, plains, source, signature, reqtime, tokenBearer)
            elif selectedItem == 'Get Transaction':
                #Get Transaction
                source = "/api/aggregator/merchant/qr/transaction/list?userId=" + MerchantId + "&startdate=" + tanggalskrg + "&enddate=" + tanggalskrg + ""
                method = "GET"
                body = ''
                self.MOATxtBody.delete('1.0', tk.END)
                self.MOATxtBody.insert(tk.END, str(body))
                signature = generateSignature.genSignatureGET(source, token, reqtime, clearPassword)
                plains = generateSignature.genPlainSign(source,token,reqtime,method,body)
                key = generateSignature.genKey(clearPassword,reqtime,token)
                self.changeOpenAPImerchantEntry(key, plains, source, signature, reqtime, tokenBearer)
            elif selectedItem == 'Get Balance':
                #Get Balance
                source = "/api/aggregator/merchant/qr/balance/detail?userId=" + MerchantId
                method = "GET"
                body = ''
                self.MOATxtBody.delete('1.0', tk.END)
                self.MOATxtBody.insert(tk.END, str(body))
                signature = generateSignature.genSignatureGET(source, token, reqtime, clearPassword)
                plains = generateSignature.genPlainSign(source,token,reqtime,method,body)
                key = generateSignature.genKey(clearPassword,reqtime,token)
                self.changeOpenAPImerchantEntry(key, plains, source, signature, reqtime, tokenBearer)
            elif selectedItem == 'Inquiry Withdraw':
                #Withdraw inquiry
                source = "/api/aggregator/merchant/qr/withdraw/inquiry"
                method = "POST"
                tbody = Modules.JsonRemoveWhitespace(bod)
                
                signature = generateSignature.genSignaturePOST(source, token, reqtime, clearPassword, tbody)
                plains = generateSignature.genPlainSign(source,token,reqtime,method,tbody)
                key = generateSignature.genKey(clearPassword,reqtime,token)
                
                self.changeOpenAPImerchantEntry(key, plains, source, signature, reqtime, tokenBearer)
            elif selectedItem == 'Submit Withdraw':
                #withdraw process
                source = "/api/aggregator/merchant/qr/withdraw"
                method = "POST"
                tbody = Modules.JsonRemoveWhitespace(bod)
                signature = generateSignature.genSignaturePOST(source, token, reqtime, clearPassword, tbody)
                plains = generateSignature.genPlainSign(source,token,reqtime,method,tbody)
                key = generateSignature.genKey(clearPassword,reqtime,token)
                self.changeOpenAPImerchantEntry(key, plains, source, signature, reqtime, tokenBearer)
            elif selectedItem == 'Create PIN':
                #Create Pin
                source = "/api/aggregator/merchant/pin/create_pin"
                method = "POST"
                tbody = Modules.JsonRemoveWhitespace(bod)
                signature = generateSignature.genSignaturePOST(source, token, reqtime, clearPassword, tbody)
                plains = generateSignature.genPlainSign(source,token,reqtime,method,tbody)
                key = generateSignature.genKey(clearPassword,reqtime,token)
                self.changeOpenAPImerchantEntry(key, plains, source, signature, reqtime, tokenBearer)
            elif selectedItem == 'Forgot PIN':
                #Forgot Pin
                source = "/api/aggregator/merchant/pin/forgot_pin"
                method = "POST"
                tbody = Modules.JsonRemoveWhitespace(bod)
                signature = generateSignature.genSignaturePOST(source, token, reqtime, clearPassword, tbody)
                plains = generateSignature.genPlainSign(source,token,reqtime,method,tbody)
                key = generateSignature.genKey(clearPassword,reqtime,token)
                self.changeOpenAPImerchantEntry(key, plains, source, signature, reqtime, tokenBearer)
            elif selectedItem == 'Get Invoice Transaction':
                #Get Invoice Transaction
                source = "/api/aggregator/merchant/invoice/transaction/" + TrxId
                method = "GET"
                body = ''
                self.MOATxtBody.delete('1.0', tk.END)
                self.MOATxtBody.insert(tk.END, str(body))
                signature = generateSignature.genSignatureGET(source, token, reqtime, clearPassword)
                plains = generateSignature.genPlainSign(source,token,reqtime,method,body)
                key = generateSignature.genKey(clearPassword,reqtime,token)
                self.changeOpenAPImerchantEntry(key, plains, source, signature, reqtime, tokenBearer)
            elif selectedItem == 'Get Qris Acquire Transaction':
                #QRISacquirerTrx
                source = "/api/aggregator/merchant/qris/acquire/transaction/" + rrn
                method = "GET"
                body = ''
                self.MOATxtBody.delete('1.0', tk.END)
                self.MOATxtBody.insert(tk.END, str(body))
                signature = generateSignature.genSignatureGET(source, token, reqtime, clearPassword)
                plains = generateSignature.genPlainSign(source,token,reqtime,method,body)
                key = generateSignature.genKey(clearPassword,reqtime,token)
                self.changeOpenAPImerchantEntry(key, plains, source, signature, reqtime, tokenBearer)
            elif selectedItem == 'Get Balance Deposit':
                #Get Balance Deposit
                source = '/api/aggregator/merchant/institution/balance/' + MerchantId
                method = "GET"
                body = ''
                self.MOATxtBody.delete('1.0', tk.END)
                self.MOATxtBody.insert(tk.END, str(body))
                signature = generateSignature.genSignatureGET(source, token, reqtime, clearPassword)
                plains = generateSignature.genPlainSign(source,token,reqtime,method,body)
                key = generateSignature.genKey(clearPassword,reqtime,token)
                self.changeOpenAPImerchantEntry(key, plains, source, signature, reqtime, tokenBearer)
            elif selectedItem == 'Get Deposit Transaction':
                #Get Deposit Transaction
                source = "/api/aggregator/merchant/deposit/transaction/list?userId=" + MerchantId + "&startdate=" + tanggalskrg + "&enddate=" + tanggalskrg + "&page=1"
                method = "GET"
                body = ''
                self.MOATxtBody.delete('1.0', tk.END)
                self.MOATxtBody.insert(tk.END, str(body))
                signature = generateSignature.genSignatureGET(source, token, reqtime, clearPassword)
                plains = generateSignature.genPlainSign(source,token,reqtime,method,body)
                key = generateSignature.genKey(clearPassword,reqtime,token)
                self.changeOpenAPImerchantEntry(key, plains, source, signature, reqtime, tokenBearer)
            elif selectedItem == 'Inquiry Withdraw Deposit':
                #Deposit Withdraw Inquiry
                source = "/api/aggregator/merchant/deposit/withdraw/inquiry?userId=" + MerchantId
                method = "GET"
                body = ''
                self.MOATxtBody.delete('1.0', tk.END)
                self.MOATxtBody.insert(tk.END, str(body))
                signature = generateSignature.genSignatureGET(source, token, reqtime, clearPassword)
                plains = generateSignature.genPlainSign(source,token,reqtime,method,body)
                key = generateSignature.genKey(clearPassword,reqtime,token)
                self.changeOpenAPImerchantEntry(key, plains, source, signature, reqtime, tokenBearer)
            elif selectedItem == 'Submit Withdraw Deposit':
                #Submit Withdraw Deposit
                source = "/api/aggregator/merchant/deposit/withdraw"
                method = "POST"
                tbody = Modules.JsonRemoveWhitespace(bod)
                signature = generateSignature.genSignaturePOST(source, token, reqtime, clearPassword, tbody)
                plains = generateSignature.genPlainSign(source,token,reqtime,method,tbody)
                key = generateSignature.genKey(clearPassword,reqtime,token)
                self.changeOpenAPImerchantEntry(key, plains, source, signature, reqtime, tokenBearer)
            elif selectedItem == 'Get Withdraw Deposit Detail':
                #Get Withdraw Deposit Detail
                source = "/api/aggregator/merchant/withdraw/deposit/" + TrxId
                method = "GET"
                body = ''
                self.MOATxtBody.delete('1.0', tk.END)
                self.MOATxtBody.insert(tk.END, str(body))
                signature = generateSignature.genSignatureGET(source, token, reqtime, clearPassword)
                plains = generateSignature.genPlainSign(source,token,reqtime,method,body)
                key = generateSignature.genKey(clearPassword,reqtime,token)
                self.changeOpenAPImerchantEntry(key, plains, source, signature, reqtime, tokenBearer)
            elif selectedItem == 'Deduct Deposit & Split Fee':
                #Deduct Deposit & Split Fee
                source = "/api/aggregator/merchant/payment/notif"
                method = "POST"
                tbody = Modules.JsonRemoveWhitespace(bod)
                signature = generateSignature.genSignaturePOST(source, token, reqtime, clearPassword, tbody)
                plains = generateSignature.genPlainSign(source,token,reqtime,method,tbody)
                key = generateSignature.genKey(clearPassword,reqtime,token)
                self.changeOpenAPImerchantEntry(key, plains, source, signature, reqtime, tokenBearer)
            elif selectedItem == 'Get Deduct Deposit Transaction':
                #Get Deduct Deposit Transaction
                source = '/public/api/v1/payment/notif/trx?request_id=' + TrxId + '&type=requestId'
                method = "GET"
                body = ''
                self.MOATxtBody.delete('1.0', tk.END)
                self.MOATxtBody.insert(tk.END, str(body))
                signature = generateSignature.genSignatureGET(source, token, reqtime, clearPassword)
                plains = generateSignature.genPlainSign(source,token,reqtime,method,body)
                key = generateSignature.genKey(clearPassword,reqtime,token)
                self.changeOpenAPImerchantEntry(key, plains, source, signature, reqtime, tokenBearer)
            elif selectedItem == 'Send receipt':
                #Send receipt
                source = '/public/api/v1/createReceipt/' + MerchantId
                method = 'POST'
                tbody = Modules.JsonRemoveWhitespace(bod)
                signature = generateSignature.genSignaturePOST(source, token, reqtime, clearPassword, tbody)
                plains = generateSignature.genPlainSign(source,token,reqtime,method,tbody)
                key = generateSignature.genKey(clearPassword,reqtime,token)
                self.changeOpenAPImerchantEntry(key, plains, source, signature, reqtime, tokenBearer)
        except ValueError as e:
            print(str(e))

    def hit_request(self, event=None):
        selected_environment = self.MOAcbEnvironment.get()
        if selected_environment == 'Production':
            baseurl = 'https://tokoapi.netzme.com'
            baseurltokonetzmeweb = 'https://pay.netzme.com'
        else:
            baseurl = 'https://tokoapi-stg.netzme.com'
            baseurltokonetzmeweb = 'https://pay-stg.netzme.com'
        clientId = self.MOAcbAggregatorId.get()
        clearPassword = self.MOAEnClearPassword.get()
        token = self.MOAEnAuthToken.get()
        tokenBearer = "Bearer " + token
        signature = str(self.MOAEnSignature.get())
        reqtime = str(self.MOAEnRequestTime.get())
        selected_endpoint = self.MOAcbEndpoint.get() # --> selected combobox
        PhoneNumber = self.MOAEnPhoneNumber.get()
        MerchantId = self.MOAEnMerchantId.get()
        tanggalskrg = self.MOAEnDate.get()
        TrxId = self.MOAEnTrxId.get()
        requestId = Modules.generateUUID()
        rrn = self.MOAEnRRN.get()
        pinraw = self.MOAEnPIN.get()
        pin = generateSignature.genPINToko(pinraw,clientId,MerchantId)
        pmethod = str(self.MOAcbInvMethod.get())
        feetype = str(self.MOAcbFeeType.get())
        bod = jsonParser.jsonParserMinify(self.MOATxtBody.get("1.0",'end-1c'))
        tokenAuth = str('custom ' + self.MOAEnToken.get())

        if selected_endpoint == 'Authorization':
            #Auth token
            source = '/oauth/merchant/accesstoken'
            authtoken = 'Basic ' + generateSignature.getautBasic(clientId,clearPassword)
            headerreq = {"Content-Type": "application/json","Authorization":authtoken}
        elif selected_endpoint in ('Create Invoice','Create Validated Invoice','Create Invoice Transaction','Create Invoice Topup Deposit'):
            useragen = clientId + ';' + MerchantId
            headerreq = {"Content-Type": "application/json","Authorization":tokenAuth,"User-Agent":useragen}
            if selected_endpoint == 'Create Invoice':
                source = "/api/v1/invoice/create"
            elif selected_endpoint == 'Create Validated Invoice':
                source = "/api/v1/invoice/create/validated"
            elif selected_endpoint == 'Create Invoice Transaction':
                source = "/api/v1/invoice/createTransaction"
            elif selected_endpoint == 'Create Invoice Topup Deposit':
                source = "/api/v1/invoice/createTransaction"
        else:
            headerreq = {"Content-Type": "application/json","Signature":signature,"Request-Time":reqtime,"Authorization":tokenBearer,"Client-Id":clientId}
            if selected_endpoint == 'Merchant Detail':
                source = "/api/aggregator/merchant/qr/merchant_detail?phoneNo=" + PhoneNumber
            elif selected_endpoint == 'Get Transaction':
                source = "/api/aggregator/merchant/qr/transaction/list?userId=" + MerchantId + "&startdate=" + tanggalskrg + "&enddate=" + tanggalskrg + ""
            elif selected_endpoint == 'Get Balance':
                source = "/api/aggregator/merchant/qr/balance/detail?userId=" + MerchantId
            elif selected_endpoint == 'Inquiry Withdraw':
                source = "/api/aggregator/merchant/qr/withdraw/inquiry"
            elif selected_endpoint == 'Submit Withdraw':
                source = "/api/aggregator/merchant/qr/withdraw"
            elif selected_endpoint == 'Create PIN':
                source = "/api/aggregator/merchant/pin/create_pin"
            elif selected_endpoint == 'Forgot PIN':
                source = "/api/aggregator/merchant/pin/forgot_pin"
            elif selected_endpoint == 'Get Invoice Transaction':
                source = "/api/aggregator/merchant/invoice/transaction/" + TrxId
            elif selected_endpoint == 'Get Qris Acquire Transaction':
                source = "/api/aggregator/merchant/qris/acquire/transaction/" + rrn
            elif selected_endpoint == 'Get Balance Deposit':
                source = '/api/aggregator/merchant/institution/balance/' + MerchantId
            elif selected_endpoint == 'Get Deposit Transaction':
                source = "/api/aggregator/merchant/deposit/transaction/list?userId=" + MerchantId + "&startdate=" + tanggalskrg + "&enddate=" + tanggalskrg + "&page=1"
            elif selected_endpoint == 'Inquiry Withdraw Deposit':
                source = "/api/aggregator/merchant/deposit/withdraw/inquiry?userId=" + MerchantId
            elif selected_endpoint == 'Submit Withdraw Deposit':
                source = "/api/aggregator/merchant/deposit/withdraw"
            elif selected_endpoint == 'Get Withdraw Deposit Detail':
                source = "/api/aggregator/merchant/withdraw/deposit/" + TrxId
            elif selected_endpoint == 'Deduct Deposit & Split Fee':
                source = "/api/aggregator/merchant/payment/notif"
            elif selected_endpoint == 'Get Deduct Deposit Transaction':
                source = '/public/api/v1/payment/notif/trx?request_id=' + TrxId + '&type=requestId'
            elif selected_endpoint == 'Send receipt':
                source = '/public/api/v1/createReceipt/' + MerchantId

        if selected_endpoint in ('Create Invoice','Create Validated Invoice','Create Invoice Transaction','Create Invoice Topup Deposit'):
            response = Modules.make_http_request(url=baseurltokonetzmeweb+source, headers=headerreq, body_request=bod)
        else:
            response = Modules.make_http_request(url=baseurl+source, headers=headerreq, body_request=bod)
        self.MOABtnSend.config(state=tk.NORMAL)
        if response:
            http_status_code = response[0]
            response_message = response[1]
            #print(response_message)
            response_message = jsonParser.jsonParserBeautify(response_message)
            msgbox = f"HTTP Status Code: {http_status_code}\nResponse Message: {response_message}"
            ResponseOpenAPI(msgbox)
            if selected_endpoint == "Authorization":
                strings = Modules.get_value_from_json(response_message, 'access_token')
                if strings:
                    self.MOAEnAuthToken.delete(0, tk.END)
                    self.MOAEnAuthToken.insert(0, strings)

    def generate_curl(self, event=None):
        selected_environment = self.MOAcbEnvironment.get()
        if selected_environment == 'Production':
            baseurl = 'https://tokoapi.netzme.com'
            baseurltokonetzmeweb = 'https://pay.netzme.com'
        else:
            baseurl = 'https://tokoapi-stg.netzme.com'
            baseurltokonetzmeweb = 'https://pay-stg.netzme.com'
        clientId = self.MOAcbAggregatorId.get()
        clearPassword = self.MOAEnClearPassword.get()
        token = self.MOAEnAuthToken.get()
        tokenBearer = "Bearer " + token
        signature = str(self.MOAEnSignature.get())
        reqtime = str(self.MOAEnRequestTime.get())
        selected_endpoint = self.MOAcbEndpoint.get() # --> selected combobox
        PhoneNumber = self.MOAEnPhoneNumber.get()
        MerchantId = self.MOAEnMerchantId.get()
        tanggalskrg = self.MOAEnDate.get()
        TrxId = self.MOAEnTrxId.get()
        requestId = Modules.generateUUID()
        rrn = self.MOAEnRRN.get()
        pinraw = self.MOAEnPIN.get()
        pin = generateSignature.genPINToko(pinraw,clientId,MerchantId)
        pmethod = str(self.MOAcbInvMethod.get())
        feetype = str(self.MOAcbFeeType.get())
        bod = str(self.MOATxtBody.get("1.0",'end-1c'))
        tokenAuth = str('custom ' + self.MOAEnToken.get())

        if selected_endpoint == 'Authorization':
            #Auth token
            source = '/oauth/merchant/accesstoken'
            authtoken = 'Basic ' + generateSignature.getautBasic(clientId,clearPassword)
            headerreq = {"Content-Type": "application/json","Authorization":authtoken}
        elif selected_endpoint in ('Create Invoice','Create Validated Invoice','Create Invoice Transaction','Create Invoice Topup Deposit'):
            useragen = clientId + ';' + MerchantId
            headerreq = {"Content-Type": "application/json","Authorization":tokenAuth,"User-Agent":useragen}
            if selected_endpoint == 'Create Invoice':
                source = "/api/v1/invoice/create"
            elif selected_endpoint == 'Create Validated Invoice':
                source = "/api/v1/invoice/create/validated"
            elif selected_endpoint == 'Create Invoice Transaction':
                source = "/api/v1/invoice/createTransaction"
            elif selected_endpoint == 'Create Invoice Topup Deposit':
                source = "/api/v1/invoice/createTransaction"
        else:
            headerreq = {"Content-Type": "application/json","Signature":signature,"Request-Time":reqtime,"Authorization":tokenBearer,"Client-Id":clientId}
            if selected_endpoint == 'Merchant Detail':
                source = "/api/aggregator/merchant/qr/merchant_detail?phoneNo=" + PhoneNumber
            elif selected_endpoint == 'Get Transaction':
                source = "/api/aggregator/merchant/qr/transaction/list?userId=" + MerchantId + "&startdate=" + tanggalskrg + "&enddate=" + tanggalskrg + ""
            elif selected_endpoint == 'Get Balance':
                source = "/api/aggregator/merchant/qr/balance/detail?userId=" + MerchantId
            elif selected_endpoint == 'Inquiry Withdraw':
                source = "/api/aggregator/merchant/qr/withdraw/inquiry"
            elif selected_endpoint == 'Submit Withdraw':
                source = "/api/aggregator/merchant/qr/withdraw"
            elif selected_endpoint == 'Create PIN':
                source = "/api/aggregator/merchant/pin/create_pin"
            elif selected_endpoint == 'Forgot PIN':
                source = "/api/aggregator/merchant/pin/forgot_pin"
            elif selected_endpoint == 'Get Invoice Transaction':
                source = "/api/aggregator/merchant/invoice/transaction/" + TrxId
            elif selected_endpoint == 'Get Qris Acquire Transaction':
                source = "/api/aggregator/merchant/qris/acquire/transaction/" + rrn
            elif selected_endpoint == 'Get Balance Deposit':
                source = '/api/aggregator/merchant/institution/balance/' + MerchantId
            elif selected_endpoint == 'Get Deposit Transaction':
                source = "/api/aggregator/merchant/deposit/transaction/list?userId=" + MerchantId + "&startdate=" + tanggalskrg + "&enddate=" + tanggalskrg + "&page=1"
            elif selected_endpoint == 'Inquiry Withdraw Deposit':
                source = "/api/aggregator/merchant/deposit/withdraw/inquiry?userId=" + MerchantId
            elif selected_endpoint == 'Submit Withdraw Deposit':
                source = "/api/aggregator/merchant/deposit/withdraw"
            elif selected_endpoint == 'Get Withdraw Deposit Detail':
                source = "/api/aggregator/merchant/withdraw/deposit/" + TrxId
            elif selected_endpoint == 'Deduct Deposit & Split Fee':
                source = "/api/aggregator/merchant/payment/notif"
            elif selected_endpoint == 'Get Deduct Deposit Transaction':
                source = '/public/api/v1/payment/notif/trx?request_id=' + TrxId + '&type=requestId'
            elif selected_endpoint == 'Send receipt':
                source = '/public/api/v1/createReceipt/' + MerchantId
        if selected_endpoint in ('Create Invoice','Create Validated Invoice','Create Invoice Transaction','Create Invoice Topup Deposit'):
            output = Modules.generate_curl_command(url=baseurltokonetzmeweb+source, headers=headerreq, payload=bod)
        else:
            output = Modules.generate_curl_command(url=baseurl+source, headers=headerreq, payload=bod)
        ResponseOpenAPI(output)

    def CheckTokenMerchant(self):
        try:
            aggregatorId = self.MOAcbAggregatorId.get()
            SQL = "select*from user_token_auth where user_name = '" + aggregatorId + "'"
            exeQuery = Modules.ConnectDBMerchant(SQL)
            for row in exeQuery:
                self.MOAEnAuthToken.config(state='normal')
                self.MOAEnAuthToken.delete(0, tk.END)
                self.MOAEnAuthToken.insert(tk.END, str(row[4]))
        except ValueError as e:
            ResponseOpenAPI(str(e))

    def showhideMerchantOpenAPIElement(self, *args):
        def place_widget(name, x, y, normal=False):
            widget = getattr(self, name)
            widget.place(x=x, y=y)
            if normal and name.startswith('MOAEn'):
                widget.config(state='normal')

        # Tempatkan semua widget di posisi default
        for name in ['MOAlblAggregatorId', 'MOAcbAggregatorId', 'MOABtnCreateCurl', 'MOABtnSend', 'MOAlblClearPassword', 'MOAEnClearPassword', 'MOAlblAuthToken', 'MOAEnAuthToken',
                    'MOAlblMerchantId', 'MOAEnMerchantId', 'MOAlblEndpoint', 'MOAcbEndpoint', 'MOAlbl6', 'MOAlblRawKey', 'MOAEnRawKey',
                    'MOAlblRawSignature', 'MOAEnRawSignature', 'MOAlblSource', 'MOAEnSource', 'MOAlblSignature', 'MOAEnSignature', 'MOAlblRequestTime', 'MOAEnRequestTime',
                    'MOAlblAuthorization', 'MOAEnAuthorization', 'MOAlblBody', 'MOATxtBody', 'MOABtnCheck', 'MOAlblPhoneNumber', 'MOAEnPhoneNumber',
                    'MOAlblPIN', 'MOAEnPIN', 'MOAlblAmountWithdraw', 'MOAEnAmountWithdraw', 'MOAlblNoRek', 'MOAEnNoRek',
                    'MOAlblBankCode', 'MOAEnBankCode', 'MOAlblBankName', 'MOAEnBankName', 'MOAlblRekName', 'MOAEnRekName',
                    'MOAlblTrxId', 'MOAEnTrxId', 'MOAlblInvMethod', 'MOAcbInvMethod', 'MOAlblFeeType', 'MOAcbFeeType',
                    'MOAlblRRN', 'MOAEnRRN', 'MOAEnToken', 'MOAlblToken', 'MOAlblTerminal', 'MOAEnTerminal',
                    'MOAlblDate', 'MOAEnDate', 'MOADateBtn', 'MOAEnvLbl', 'MOAcbEnvironment']:
            place_widget(name, 17500, 3, True)

        place_widget('MOABtnCreateCurl', 650, 3)
        selection = str(self.MOAcbEndpoint.get())
        selectionPaymethod = str(self.MOAcbInvMethod.get())

        common_widgets = [
            ('MOAlblAggregatorId', 3, 3), ('MOAcbAggregatorId', 110, 3), ('MOABtnSend', 850, 3),
            ('MOAlblClearPassword', 3, 33), ('MOAEnClearPassword', 110, 33), ('MOAlblAuthToken', 3, 63),
            ('MOAEnAuthToken', 110, 63), ('MOABtnCheck', 650, 63), ('MOAlblEndpoint', 3, 93),
            ('MOAcbEndpoint', 110, 93), ('MOAlblBody', 3, 343), ('MOATxtBody', 110, 343),
            ('MOAEnvLbl', 750, 33), ('MOAcbEnvironment', 840, 33)
        ]
        for name, x, y in common_widgets:
            place_widget(name, x, y, True)

        if selection == 'Authorization':
            place_widget('MOAlblMerchantId', 750, 63)
            place_widget('MOAEnMerchantId', 840, 63, True)
        elif selection in ['Create Invoice', 'Create Validated Invoice', 'Create Invoice Transaction', 'Create Invoice Topup Deposit']:
            additional_widgets = [
                ('MOAlblMerchantId', 750, 63), ('MOAEnMerchantId', 840, 63),
                ('MOAlblToken', 3, 123), ('MOAEnToken', 110, 123),
                ('MOAlblAmountWithdraw', 750, 93), ('MOAEnAmountWithdraw', 840, 93)
            ]
            for name, x, y in additional_widgets:
                place_widget(name, x, y, True)

            if selection == 'Create Invoice':
                place_widget('MOAlblFeeType', 750, 153)
                place_widget('MOAcbFeeType', 840, 153, True)
            elif selection in ['Create Invoice Transaction', 'Create Validated Invoice']:
                place_widget('MOAlblInvMethod', 750, 123)
                place_widget('MOAcbInvMethod', 840, 123, True)
                place_widget('MOAlblFeeType', 750, 153)
                place_widget('MOAcbFeeType', 840, 153, True)
                if selectionPaymethod == "QRIS_DINAMIS_TERMINAL":
                    place_widget('MOAlblTerminal', 750, 183)
                    place_widget('MOAEnTerminal', 840, 183, True)
        else:
            additional_widgets = [
                ('MOAlbl6', 3, 123), ('MOAlblRawKey', 3, 153), ('MOAEnRawKey', 110, 153),
                ('MOAlblRawSignature', 3, 183), ('MOAEnRawSignature', 110, 183), ('MOAlblSource', 3, 213),
                ('MOAEnSource', 110, 213), ('MOAlblSignature', 3, 243), ('MOAEnSignature', 110, 243),
                ('MOAlblRequestTime', 3, 283), ('MOAEnRequestTime', 110, 283), ('MOAlblAuthorization', 3, 313),
                ('MOAEnAuthorization', 110, 313), ('MOAlblMerchantId', 750, 63), ('MOAEnMerchantId', 840, 63)
            ]
            for name, x, y in additional_widgets:
                place_widget(name, x, y, True)

            specific_widgets = {
                'Merchant Detail': [('MOAlblPhoneNumber', 750, 93), ('MOAEnPhoneNumber', 840, 93)],
                'Get Transaction': [('MOAlblDate', 750, 93), ('MOAEnDate', 840, 93), ('MOADateBtn', 840, 123)],
                'Create PIN': [('MOAlblPIN', 750, 93), ('MOAEnPIN', 840, 93)],
                'Get Invoice Transaction': [('MOAlblTrxId', 750, 93), ('MOAEnTrxId', 840, 93)],
                'Get Deduct Deposit Transaction': [('MOAlblTrxId', 750, 93), ('MOAEnTrxId', 840, 93)],
                'Get Withdraw Deposit Detail': [('MOAlblTrxId', 750, 93), ('MOAEnTrxId', 840, 93)],
                'Get Qris Acquire Transaction': [('MOAlblRRN', 750, 93), ('MOAEnRRN', 840, 93)],
                'Deduct Deposit & Split Fee': [('MOAlblAmountWithdraw', 750, 93), ('MOAEnAmountWithdraw', 840, 93)],
                'Submit Withdraw': [
                    ('MOAlblPIN', 750, 93), ('MOAEnPIN', 840, 93),
                    ('MOAlblAmountWithdraw', 750, 123), ('MOAEnAmountWithdraw', 840, 123),
                    ('MOAlblNoRek', 750, 153), ('MOAEnNoRek', 840, 153),
                    ('MOAlblBankCode', 750, 183), ('MOAEnBankCode', 840, 183),
                    ('MOAlblBankName', 750, 213), ('MOAEnBankName', 840, 213),
                    ('MOAlblRekName', 750, 243), ('MOAEnRekName', 840, 243)
                ],
                'Submit Withdraw Deposit': [
                    ('MOAlblPIN', 750, 93), ('MOAEnPIN', 840, 93),
                    ('MOAlblAmountWithdraw', 750, 123), ('MOAEnAmountWithdraw', 840, 123),
                    ('MOAlblNoRek', 750, 153), ('MOAEnNoRek', 840, 153),
                    ('MOAlblBankCode', 750, 183), ('MOAEnBankCode', 840, 183),
                    ('MOAlblBankName', 750, 213), ('MOAEnBankName', 840, 213),
                    ('MOAlblRekName', 750, 243), ('MOAEnRekName', 840, 243)
                ],
                'Get Deposit Transaction': [('MOAlblDate', 750, 93), ('MOAEnDate', 840, 93), ('MOADateBtn', 840, 123)]
            }

            if selection in specific_widgets:
                for name, x, y in specific_widgets[selection]:
                    place_widget(name, x, y, True)

    def changeOpenAPImerchantEntry(self, *values):
        for entry, value in zip([self.MOAEnRawKey, self.MOAEnRawSignature, self.MOAEnSource, self.MOAEnSignature, self.MOAEnRequestTime, self.MOAEnAuthorization], values):
            entry.config(state='normal')
            entry.delete(0, tk.END)
            entry.insert(tk.END, str(value))

    def on_field_MOAcbEndpointchange(self):
        self.MerchantOpenAPIBody()
    
    def start_thread_connection(self):
        self.MOABtnSend.config(state=tk.DISABLED)
        thread = threading.Thread(target=self.hit_request)
        thread.start()