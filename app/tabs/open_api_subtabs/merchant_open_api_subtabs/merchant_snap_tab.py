# app/tabs/open_api_subtabs/merchant_open_api_subtabs/merchant_snap_tab.py
import tkinter as tk
from tkinter import ttk
from src.modules import Modules
import json
from src.jsonParser import jsonParser
import src.snap as Snap
from app.tabs.popup import ResponseOpenAPI
from src.generateSignature import generateSignature
from app.custom.custom_text import CustomText
from app.custom.date_picker import DatePicker
import threading

file_config_location = 'config/config_aggregator.json'

class MerchantSnapTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        
        string_vars = [tk.StringVar() for _ in range(22)]
        self.y1, self.y2, self.y3, self.y4, self.y5, self.y6, self.y7, self.y8, self.y9, self.y10, self.y11, self.y12, self.y13, self.y14, self.y15, self.y16, self.y17, self.y18, self.y19, self.y20, self.y21, self.y22 = string_vars

        variables = [self.y1]
        functions = [self.handle_endpoint_selection]
        for variable, function in zip(variables, functions):
            variable.trace_add('write', lambda *args, func=function: func())

        # Endpoint label and combobox
        self.label_endpoint = tk.Label(self, text="Endpoint")
        self.label_endpoint.place(x=3, y=153)
        self.combo_endpoint = ttk.Combobox(self, textvariable=self.y1, width=55)
        self.combo_endpoint["values"] = ["Access Token", "Create PIN", "Forgot PIN", "Balance Detail", "Merchant Detail", "List Transaction",
                     "Create Invoice", "Create Invoice Transaction", "Get Invoice Transaction", "Merchant Inquiry Withdraw",
                     "Merchant Withdraw Process", "Merchant Withdraw Detail", "Get QRIS Acquirer Trx", "Get Deposit Balance",
                     "Deposit Trx List", "Deduct Deposit & Splitfee", "Deposit Inquiry Withdraw", "Deposit Withdraw Process",
                     "Deposit Withdraw Detail"]
        self.combo_endpoint.config(state="readonly")
        self.combo_endpoint.place(x=110, y=153)

        self.label_environment = tk.Label(self, text="Environment")
        self.label_environment.place(x=750, y=33)

        self.combo_environment = ttk.Combobox(self, textvariable=self.y2)
        self.combo_environment["values"] = ["Staging","Production"]
        self.combo_environment.config(state="readonly")
        self.combo_environment.place(x=840, y=33)

        # AggregatorId label, combobox, and 'Create Curl' button
        self.label_aggregator_id = tk.Label(self, text="AggregatorId")
        self.label_aggregator_id.place(x=3, y=3)
        self.combo_aggregator_id = ttk.Combobox(self, width=55)
        self.combo_aggregator_id['values'] = Modules.getAllAggregatorMerchant()
        self.combo_aggregator_id.config(state='readonly')

        self.combo_aggregator_id.place(x=110, y=3)
        self.create_curl_button = ttk.Button(self, text="Create Curl", command=self.create_curl)
        self.create_curl_button.place(x=650, y=3)
        self.send_button = ttk.Button(self, text="Send", command=self.start_thread_connection)
        self.send_button.place(x=850, y=3)

        # Client Secret label, entry
        self.label_client_secret = tk.Label(self, text="Client Secret")
        self.label_client_secret.place(x=3, y=33)
        self.entry_client_secret = tk.Entry(self, width=55)
        self.entry_client_secret.place(x=110, y=33)

        # Set the initial value for the client secret based on the selected aggregatorId
        self.combo_aggregator_id.bind('<<ComboboxSelected>>', self.update_client_secret)

        # Private Key label and entry
        self.label_private_key = tk.Label(self, text="Private Key")
        self.label_private_key.place(x=3, y=63)
        self.entry_private_key = tk.Entry(self, width=55)
        self.entry_private_key.place(x=110, y=63)

        # X-Callback Token label and entry
        self.label_x_callback_token = tk.Label(self, text="X-Callback Token")
        self.label_x_callback_token.place(x=3, y=93)
        self.entry_x_callback_token = tk.Entry(self, width=55)
        self.entry_x_callback_token.place(x=110, y=93)

        # Auth Token label, entry, and 'Check' button
        self.label_auth_token = tk.Label(self, text="Auth Token")
        self.label_auth_token.place(x=3, y=123)
        self.entry_auth_token = tk.Entry(self, width=55)
        self.entry_auth_token.place(x=110, y=123)
        self.check_button = ttk.Button(self, text="Check")
        self.check_button.place(x=650, y=63)

        # Merchant ID label and entry
        self.label_merchant_id = tk.Label(self, text="Merchant ID")
        self.entry_merchant_id = tk.Entry(self)
        self.entry_merchant_id.bind('<KeyRelease>', self.handle_endpoint_selection)
        
        # Amount label and entry
        self.label_amount = tk.Label(self, text="Amount")
        self.entry_amount = tk.Entry(self)
        self.entry_amount.bind('<KeyRelease>', self.handle_endpoint_selection)

        # Raw Signature Auth label and entry
        self.label_raw_signature_auth = tk.Label(self, text="Raw Signature Auth")
        self.entry_raw_signature_auth = tk.Entry(self, width=55)

        # Raw Signature Service label and entry
        self.label_raw_signature_service = tk.Label(self, text="Raw Signature Service")
        self.entry_raw_signature_service = tk.Entry(self, width=55)

        # Signature Auth label and entry
        self.label_signature_auth = tk.Label(self, text="Signature Auth")
        self.entry_signature_auth = tk.Entry(self, width=55)

        # Signature Service label and entry
        self.label_signature_service = tk.Label(self, text="Signature Service")
        self.entry_signature_service = tk.Entry(self, width=55)

        # Body label and text
        self.label_body = tk.Label(self, text="Body")
        self.label_body.place(x=3, y=343)
        self.text_body = CustomText(self, width=100, height=16)
        self.text_body.place(x=110, y=343)
        #self.text_body.bind('<<TextModified>>',self.set_signature_text)

        # PIN label and entry
        self.label_pin = tk.Label(self, text="PIN")
        self.entry_pin = tk.Entry(self)
        self.entry_pin.bind('<KeyRelease>', self.handle_endpoint_selection)

        # Phone Number label and entry
        self.label_phone_no = tk.Label(self, text="Phone No")
        self.entry_phone_no = tk.Entry(self)
        self.entry_phone_no.bind('<KeyRelease>', self.handle_endpoint_selection)

        self.combo_endpoint.bind("<<ComboboxSelected>>", self.handle_endpoint_selection)

        # payment method
        self.label_payment_method = tk.Label(self,text="Method")
        self.combo_payment_method = ttk.Combobox(self, textvariable=self.y15)
        self.combo_payment_method['values'] = ['BANK_TRANSFER','QRIS','BCA','CREDIT_CARD','RETAIL_OUTLET','INDOMARET','QRIS_DINAMIS_TERMINAL','NETZME','OVO','DANA','DKI',"VA_BCA","VA_CIMB","VA_BRI","VA_BNI","VA_MANDIRI","VA_PERMATA","NETZME_SEAMLESS","VA_BCA_PZ"]
        self.combo_payment_method.config(state='readonly')
        self.combo_payment_method.bind("<<ComboboxSelected>>", self.handle_endpoint_selection)

        # Trx ID
        self.label_trx_id = tk.Label(self,text="Trx ID")
        self.entry_trx_id = tk.Entry(self)
        self.entry_trx_id.bind('<KeyRelease>', self.handle_endpoint_selection)

        self.label_NoRek = tk.Label(self,text="No Rek")
        self.entry_NoRek = tk.Entry(self)
        self.entry_NoRek.bind('<KeyRelease>', self.handle_endpoint_selection)

        self.label_BankCode = tk.Label(self,text="Bank Code")
        self.entry_BankCode = tk.Entry(self)
        self.entry_BankCode.bind('<KeyRelease>', self.handle_endpoint_selection)

        self.label_BankName = tk.Label(self,text="Nama Bank")
        self.entry_BankName = tk.Entry(self)
        self.entry_BankName.bind('<KeyRelease>', self.handle_endpoint_selection)

        self.label_rrn = tk.Label(self,text="RRN")
        self.entry_rrn = tk.Entry(self)
        self.entry_rrn.bind('<KeyRelease>', self.handle_endpoint_selection)

        self.label_fee_type = tk.Label(self, text="Fee Type")
        self.combo_fee_type = ttk.Combobox(self)
        self.combo_fee_type['values'] = ["on_buyer","on_seller"]
        self.combo_fee_type.config(state='readonly')

        self.label_terminal = tk.Label(self, text="Terminal ID")
        self.entry_terminal = tk.Entry(self)
        self.entry_terminal.bind('<KeyRelease>', self.handle_endpoint_selection)

        self.label_date = tk.Label(self, text='Date')
        self.entry_date = tk.Entry(self)
        self.entry_date.bind('<KeyRelease>', self.handle_endpoint_selection)

        self.label_RekName = tk.Label(self,text="Nama Rekening")
        self.entry_RekName = tk.Entry(self)
        self.entry_RekName.bind('<KeyRelease>', self.handle_endpoint_selection)

        self.date_button = ttk.Button(self, text="Open Calendar", command=self.open_calendar)

    def open_calendar(self):
        DatePicker(self, self.set_date)

    def set_date(self, date):
        self.entry_date.delete(0, tk.END)
        self.entry_date.insert(0, date)
        self.handle_endpoint_selection()

    def loadAwal(self):
        self.update_client_secret()
        self.handle_endpoint_selection()

    def update_client_secret(self, event=None):
        selected_aggregator_id = self.combo_aggregator_id.get()
        if not selected_aggregator_id == "":
            getstr = Modules.get_clear_pass_and_token(Modules.get_list_dictionary_config()[0], selected_aggregator_id)
            self.entry_client_secret.delete(0, tk.END)
            self.entry_client_secret.insert(0, getstr[4])
            self.entry_private_key.delete(0, tk.END)
            self.entry_private_key.insert(0, getstr[3])
            self.entry_x_callback_token.delete(0, tk.END)
            self.entry_x_callback_token.insert(0, getstr[2])
            self.handle_endpoint_selection()

    def hide_show_element(self):
        self.hide_all_elements()

        selected_endpoint = self.combo_endpoint.get()
        selected_paymethod = self.combo_payment_method.get()

        if selected_endpoint == "Access Token":
            self.show_elements([
                (self.label_raw_signature_auth, 3, 183),
                (self.entry_raw_signature_auth, 110, 183),
                (self.label_signature_auth, 3, 213),
                (self.entry_signature_auth, 110, 213)
            ])
        else:
            self.show_elements([
                (self.label_raw_signature_service, 3, 183),
                (self.entry_raw_signature_service, 110, 183),
                (self.label_signature_service, 3, 213),
                (self.entry_signature_service, 110, 213)
            ])

            if selected_endpoint in ("Create PIN", "Merchant Withdraw Process", "Deposit Withdraw Process"):
                self.show_elements([
                    (self.label_merchant_id, 750, 63),
                    (self.entry_merchant_id, 840, 63),
                    (self.label_pin, 750, 93),
                    (self.entry_pin, 840, 93)
                ])

                if selected_endpoint in ("Merchant Withdraw Process", "Deposit Withdraw Process"):
                    self.show_elements([
                        (self.label_amount, 750, 123),
                        (self.entry_amount, 840, 123),
                        (self.label_BankCode, 750, 153),
                        (self.entry_BankCode, 840, 153),
                        (self.label_BankName, 750, 183),
                        (self.entry_BankName, 840, 183),
                        (self.label_NoRek, 750, 213),
                        (self.entry_NoRek, 840, 213),
                        (self.label_RekName, 750, 243),
                        (self.entry_RekName, 840, 243)
                    ])

            elif selected_endpoint in ("Forgot PIN", "Balance Detail", "List Transaction", "Merchant Inquiry Withdraw", "Get Deposit Balance", "Deposit Trx List", "Deposit Inquiry Withdraw"):
                self.show_elements([
                    (self.label_merchant_id, 750, 63),
                    (self.entry_merchant_id, 840, 63)
                ])

                if selected_endpoint in ("List Transaction", "Deposit Trx List"):
                    self.show_elements([
                        (self.label_date, 750, 93),
                        (self.entry_date, 840, 93),
                        (self.date_button, 840, 123)
                    ])

            elif selected_endpoint == "Merchant Detail":
                self.show_elements([
                    (self.label_phone_no, 750, 63),
                    (self.entry_phone_no, 840, 63)
                ])

            elif selected_endpoint in ("Create Invoice", "Create Invoice Transaction"):
                self.show_elements([
                    (self.label_merchant_id, 750, 63),
                    (self.entry_merchant_id, 840, 63),
                    (self.label_amount, 750, 93),
                    (self.entry_amount, 840, 93),
                    (self.label_fee_type, 750, 123),
                    (self.combo_fee_type, 840, 123)
                ])

                if selected_endpoint == "Create Invoice Transaction":
                    self.show_elements([
                        (self.label_payment_method, 750, 153),
                        (self.combo_payment_method, 840, 153)
                    ])

                    if selected_paymethod == "QRIS_DINAMIS_TERMINAL":
                        self.show_elements([
                            (self.label_terminal, 750, 183),
                            (self.entry_terminal, 840, 183)
                        ])

            elif selected_endpoint in ("Get Invoice Transaction", "Merchant Withdraw Detail", "Deposit Withdraw Detail"):
                self.show_elements([
                    (self.label_trx_id, 750, 63),
                    (self.entry_trx_id, 840, 63)
                ])

            elif selected_endpoint == "Get QRIS Acquirer Trx":
                self.show_elements([
                    (self.label_rrn, 750, 63),
                    (self.entry_rrn, 840, 63)
                ])

            else:
                self.show_elements([
                    (self.label_merchant_id, 750, 63),
                    (self.entry_merchant_id, 840, 63),
                    (self.label_amount, 750, 93),
                    (self.entry_amount, 840, 93)
                ])

    def hide_all_elements(self):
        self.label_raw_signature_auth.place_forget()
        self.entry_raw_signature_auth.place_forget()
        self.label_signature_auth.place_forget()
        self.entry_signature_auth.place_forget()
        self.label_raw_signature_service.place_forget()
        self.entry_raw_signature_service.place_forget()
        self.label_signature_service.place_forget()
        self.entry_signature_service.place_forget()
        self.label_merchant_id.place_forget()
        self.entry_merchant_id.place_forget()
        self.label_amount.place_forget()
        self.entry_amount.place_forget()
        self.label_pin.place_forget()
        self.entry_pin.place_forget()
        self.label_phone_no.place_forget()
        self.entry_phone_no.place_forget()
        self.label_payment_method.place_forget()
        self.combo_payment_method.place_forget()
        self.label_trx_id.place_forget()
        self.entry_trx_id.place_forget()
        self.label_NoRek.place_forget()
        self.entry_NoRek.place_forget()
        self.label_BankName.place_forget()
        self.entry_BankName.place_forget()
        self.label_BankCode.place_forget()
        self.entry_BankCode.place_forget()
        self.label_RekName.place_forget()
        self.entry_RekName.place_forget()
        self.label_rrn.place_forget()
        self.entry_rrn.place_forget()
        self.label_fee_type.place_forget()
        self.combo_fee_type.place_forget()
        self.label_terminal.place_forget()
        self.entry_terminal.place_forget()
        self.label_date.place_forget()
        self.entry_date.place_forget()
        self.date_button.place_forget()

    def show_elements(self, elements):
        for element, x, y in elements:
            element.place(x=x, y=y)
        
    def handle_endpoint_selection(self, event=None):
        try:
            self.hide_show_element()
            selected_endpoint = self.combo_endpoint.get()
            merchant_id = self.entry_merchant_id.get()
            client_id = self.combo_aggregator_id.get()
            amount = self.entry_amount.get()
            amount = str(amount)
            phone_no = self.entry_phone_no.get()
            partner_ref_no = self.combo_aggregator_id.get() + Modules.RandomDigit(7)
            guid = Modules.generateUUID()
            date_pick = self.entry_date.get()
            ts = Modules.convert_date(date_pick)
            pinraw = self.entry_pin.get()
            hashpin = generateSignature.genPINToko(pinraw, client_id, merchant_id)
            payment_method = self.combo_payment_method.get()
            request_id = self.entry_trx_id.get()
            no_rek = self.entry_NoRek.get()
            bank_name = self.entry_BankName.get()
            bank_code = self.entry_BankCode.get()
            rek_name = self.entry_RekName.get()
            rrn = self.entry_rrn.get()
            fee_type = self.combo_fee_type.get()
            selected_paymentmethod = self.combo_payment_method.get()
            terminal_id = self.entry_terminal.get()
            '''
            ["Access Token", "Create PIN", "Forgot PIN", "Balance Detail", "Merchant Detail", "List Transaction",
                     "Create Invoice", "Create Invoice Transaction", "Get Invoice Transaction", "Merchant Inquiry Withdraw",
                     "Merchant Withdraw Process", "Merchant Withdraw Detail", "Get QRIS Acquirer Trx", "Get Deposit Balance",
                     "Deposit Trx List", "Deduct Deposit & Splitfee", "Deposit Inquiry Withdraw", "Deposit Withdraw Process",
                     "Deposit Withdraw Detail"]
            '''
            if selected_endpoint == "Access Token":
                url = '/api/v1/access-token/b2b'
                bodyreq = {"grantType":"client_credentials","additionalInfo":{}}
                self.set_body_text(bodyreq)
            elif selected_endpoint == "Create PIN":
                url = '/api/v1.0/merchant/create-pin'
                bodyreq = {"custIdMerchant":merchant_id,"partnerReferenceNo":guid,"additionalInfo":{"pin":hashpin,"type":"create_pin"}}
                self.set_body_text(bodyreq)
            elif selected_endpoint == "Forgot PIN":
                url = '/api/v1.0/merchant/forgot-pin'
                bodyreq = {"custIdMerchant":merchant_id,"partnerReferenceNo":guid,"additionalInfo":{"type":"forgot_pin"}}
                self.set_body_text(bodyreq)
            elif selected_endpoint == "Balance Detail":
                url = '/api/v1.0/payment/balance-inquiry'
                bodyreq = {"partnerReferenceNo":guid,"AccountNo":merchant_id}
                self.set_body_text(bodyreq)
            elif selected_endpoint == "Merchant Detail":
                url = '/api/v1.0/registration-account-inquiry'
                bodyreq = {"partnerReferenceNo":guid,"additionalInfo":{"phoneNo":phone_no}}
                self.set_body_text(bodyreq)
            elif selected_endpoint == "List Transaction":
                url = '/api/v1.0/transaction/history-list'
                bodyreq = {"pageNumber":"1","custIdMerchant":merchant_id,"partnerReferenceNo":guid,"fromDateTime":ts[0],"toDateTime":ts[1]}
                self.set_body_text(bodyreq)
            elif selected_endpoint == "Create Invoice":
                url = '/api/v1.0/invoice/create'
                bodyreq = {"custIdMerchant":merchant_id,"partnerReferenceNo":guid,"amount":{"value":amount,"currency":"IDR"},"amountDetail":{"basicAmount":{"value":amount,"currency":"IDR"},"shippingAmount":{"value":"0","currency":"IDR"}},"commissionPercentage":0,"fee_type":fee_type,"additionalInfo":{"email":"purba.jati@netzme.id","notes":"desc","description":"description","phoneNumber":"+6285270427851","imageUrl":"","fullname":"QAN"}}
                self.set_body_text(bodyreq)
            elif selected_endpoint == "Create Invoice Transaction":
                url = '/api/v1.0/invoice/create-transaction'
                if selected_paymentmethod == "QRIS_DINAMIS_TERMINAL":
                    bodyreq = {"custIdMerchant":merchant_id,"partnerReferenceNo":guid,"amount":{"value":amount,"currency":"IDR"},"amountDetail":{"basicAmount":{"value":amount,"currency":"IDR"},"shippingAmount":{"value":"0","currency":"IDR"}},"PayMethod":"QRIS","commissionPercentage":"0","expireInSecond":"3600","feeType":fee_type,"terminal_id": terminal_id,"additionalInfo":{"email":"purba.jati@netzme.id","notes":"desc","description":"description","phoneNumber":"+6285270427851","imageUrl":"a","fullname":"Percobaan"}}
                elif selected_paymentmethod == "CREDIT_CARD":
                    bodyreq = {"custIdMerchant":merchant_id,"partnerReferenceNo":guid,"amount":{"value":amount,"currency":"IDR"},"amountDetail":{"basicAmount":{"value":amount,"currency":"IDR"},"shippingAmount":{"value":"0","currency":"IDR"}},"PayMethod":payment_method,"commissionPercentage":"0","expireInSecond":"3600","feeType":fee_type,"terminal_id": terminal_id,"additionalInfo":{"email":"purba.jati@netzme.id","notes":"desc","address":"test","item_details":[{"name":"hello","item_id":"qwerty","qty":1,"amount":amount}],"description":"description","phoneNumber":"+6285270427851","imageUrl":"a","fullname":"Percobaan"}}
                else:
                    bodyreq = {"custIdMerchant":merchant_id,"partnerReferenceNo":guid,"amount":{"value":amount,"currency":"IDR"},"amountDetail":{"basicAmount":{"value":amount,"currency":"IDR"},"shippingAmount":{"value":"0","currency":"IDR"}},"PayMethod":payment_method,"commissionPercentage":"0","expireInSecond":"3600","feeType":fee_type,"additionalInfo":{"email":"purba.jati@netzme.id","notes":"desc","description":"description","phoneNumber":"+6285270427851","imageUrl":"a","fullname":"Percobaan"}}
                self.set_body_text(bodyreq)
            elif selected_endpoint == "Get Invoice Transaction":
                url = '/api-invoice/v1.0/transaction-history-detail'
                bodyreq = {"originalPartnerReferenceNo":request_id,"additionalInfo":{"partnerReferenceNo":guid}}
                self.set_body_text(bodyreq)
            elif selected_endpoint == "Merchant Inquiry Withdraw":
                url = '/api/v1.0/emoney/bank-account-inquiry'
                bodyreq = {"partnerReferenceNo":guid,"custIdMerchant":merchant_id,"AdditionalInfo":{"type":"withdraw_inquiry"}}
                self.set_body_text(bodyreq)
            elif selected_endpoint == "Merchant Withdraw Process":
                url = '/api/v1.0/emoney/transfer-bank'
                bodyreq = {"partnerReferenceNo":guid,"customerNumber":merchant_id,"amount":{"value":amount,"currency":"IDR"},"beneficiaryAccountName":rek_name,"beneficiaryAccountNumber":no_rek,"beneficiaryBankName":bank_name,"beneficiaryBankCode":bank_code,"additionalInfo":{"type":"submit_withdraw","pin":hashpin}}
                self.set_body_text(bodyreq)
            elif selected_endpoint == "Merchant Withdraw Detail":
                url = '/api/v1.0/debit/status'
                bodyreq = {"referenceNo":request_id,"partnerReferenceNo":guid}
                self.set_body_text(bodyreq)
            elif selected_endpoint == "Get QRIS Acquirer Trx":
                url = '/api-qris/v1.0/transaction-history-detail'
                bodyreq = {"originalPartnerReferenceNo":rrn,"additionalInfo":{"partnerReferenceNo":guid}}
                self.set_body_text(bodyreq)
            elif selected_endpoint == "Get Deposit Balance":
                url = '/api/v1.0/deposit/balance-inquiry'
                bodyreq = {"partnerReferenceNo":guid,"accountNo":merchant_id}
                self.set_body_text(bodyreq)
            elif selected_endpoint == "Deposit Trx List":
                url = '/api/v1.0/deposit/transaction-history-list'
                bodyreq = {"partnerReferenceNo":guid,"fromDateTime":ts[0],"toDateTime":ts[1],"pageNumber":"1","additionalInfo":{"custIdMerchant":merchant_id}}
                self.set_body_text(bodyreq)
            elif selected_endpoint == "Deduct Deposit & Splitfee":
                url = '/api/v1.0/merchant/payment-notif'
                bodyreq = {"referenceNo":guid,"partnerReferenceNo":partner_ref_no,"amount":{"value":amount,"currency":"IDR"},"feeAmount":{"value":"0","currency":"IDR"},"additionalInfo":{"custIdMerchant":merchant_id,"sku":"abc","productName":"Test","paymentStatus":"SUCCESS","payMethod":"BANK_TRANSFER","bankName":"BCA","qty":"1","desc":"testa","type":"payment_notification_to_split_fee"}}
                self.set_body_text(bodyreq)
            elif selected_endpoint == "Deposit Inquiry Withdraw":
                url = '/api/v1.0/emoney/bank-account-inquiry/deposit'
                bodyreq = {"partnerReferenceNo":guid,"custIdMerchant":merchant_id}
                self.set_body_text(bodyreq)
            elif selected_endpoint == "Deposit Withdraw Process":
                url = '/api/v1.0/emoney/transfer-bank/deposit'
                bodyreq = {"partnerReferenceNo":partner_ref_no,"customerNumber":merchant_id,"ReferenceNo":guid,"amount":{"value":amount,"currency":"IDR"},"beneficiaryAccountName":rek_name,"beneficiaryAccountNumber":no_rek,"beneficiaryBankName":bank_name,"beneficiaryBankCode":bank_code,"additionalInfo":{"type":"submit_withdraw","pin":hashpin}}
                self.set_body_text(bodyreq)
            elif selected_endpoint == "Deposit Withdraw Detail":
                url = '/api/v1.0/debit/status-deposit'
                bodyreq = {"partnerReferenceNo":guid,"referenceNo":request_id}
                self.set_body_text(bodyreq)
            
            self.set_signature_text(url)
        except (ValueError) as e:
            print(str(e))
    
    def set_body_text(self, text):
        json_formatted_str = json.dumps(text, indent=2)
        self.text_body.delete('1.0', tk.END)
        self.text_body.insert('1.0', json_formatted_str)

    def set_signature_text(self, url):
        try:
            PrivateKey = self.entry_private_key.get()
            clientId = self.combo_aggregator_id.get()
            clientSecret = self.entry_client_secret.get()
            RequestBody = self.text_body.get("1.0",'end-1c')
            RequestBody = jsonParser.jsonParserLoads(RequestBody)
            AccessToken = self.entry_auth_token.get()
            EndpointUrl = url
            Xsignature = Snap.generate_x_signature(PrivateKey, clientId)
            self.entry_raw_signature_auth.delete(0, tk.END)
            self.entry_raw_signature_auth.insert(0, Xsignature[0])
            self.entry_signature_auth.delete(0, tk.END)
            self.entry_signature_auth.insert(0, Xsignature[1])

            if RequestBody == "":
                method = "GET"
            else:
                method = "POST"
            serviceSignature = Snap.signature_service(clientSecret,method,EndpointUrl,AccessToken,RequestBody)
            self.entry_raw_signature_service.delete(0, tk.END)
            self.entry_raw_signature_service.insert(0, serviceSignature[0])
            self.entry_signature_service.delete(0, tk.END)
            self.entry_signature_service.insert(0, serviceSignature[1])
        except (ValueError) as e:
            print(str(e))
            
    def hit_request(self):
        client_id = self.combo_aggregator_id.get()
        selected_endpoint = self.combo_endpoint.get()
        RequestBody = jsonParser.jsonParserMinify(self.text_body.get("1.0",'end-1c'))
        RequestBody = jsonParser.jsonParserLoads(RequestBody)
        signatureService = self.entry_signature_service.get()
        signatureAuth = self.entry_signature_auth.get()
        getrawSignatureAuth = self.entry_raw_signature_auth.get()
        getrawSignatureService = self.entry_raw_signature_service.get()
        user_id = self.entry_merchant_id.get()
        auth_token = self.entry_auth_token.get()
        xternal_id = Modules.RandomDigit(32)
        selected_environment = self.combo_environment.get()
        if selected_environment == 'Production':
            baseurl = 'https://tokoapisnap.netzme.com'
        else:
            baseurl = 'https://tokoapisnap-stg.netzme.com'

        if selected_endpoint == "Access Token":
            x_timestamp = getrawSignatureAuth.split("|")[1]
            endpoint = '/api/v1/access-token/b2b'
            header = {"X-TIMESTAMP": x_timestamp, "Content-Type":"application/json", "X-CLIENT-KEY": client_id,"X-SIGNATURE": signatureAuth}
        else:
            parts = getrawSignatureService.split(":")
            x_timestamp = ":".join(parts[4:])
            header = {"X-TIMESTAMP": x_timestamp, "Content-Type":"application/json", "X-SIGNATURE": signatureService, "Authorization": "Bearer "+auth_token, "X-PARTNER-ID":client_id, "X-EXTERNAL-ID":xternal_id, "CHANNEL-ID":"44444"}
            if selected_endpoint == "Create PIN":
                endpoint = '/api/v1.0/merchant/create-pin'
            elif selected_endpoint == "Forgot PIN":
                endpoint = '/api/v1.0/merchant/forgot-pin'
            elif selected_endpoint == "Balance Detail":
                endpoint = '/api/v1.0/payment/balance-inquiry'
            elif selected_endpoint == "Merchant Detail":
                endpoint = '/api/v1.0/registration-account-inquiry'
            elif selected_endpoint == "List Transaction":
                endpoint = '/api/v1.0/transaction/history-list'
            elif selected_endpoint == "Create Invoice":
                endpoint = '/api/v1.0/invoice/create'
            elif selected_endpoint == "Create Invoice Transaction":
                endpoint = '/api/v1.0/invoice/create-transaction'
            elif selected_endpoint == "Get Invoice Transaction":
                endpoint = '/api-invoice/v1.0/transaction-history-detail'
            elif selected_endpoint == "Merchant Inquiry Withdraw":
                endpoint = '/api/v1.0/emoney/bank-account-inquiry'
            elif selected_endpoint == "Merchant Withdraw Process":
                endpoint = '/api/v1.0/emoney/transfer-bank'
            elif selected_endpoint == "Merchant Withdraw Detail":
                endpoint = '/api/v1.0/debit/status'
            elif selected_endpoint == "Get QRIS Acquirer Trx":
                endpoint = '/api-qris/v1.0/transaction-history-detail'
            elif selected_endpoint == "Get Deposit Balance":
                endpoint = '/api/v1.0/deposit/balance-inquiry'
            elif selected_endpoint == "Deposit Trx List":
                endpoint = '/api/v1.0/deposit/transaction-history-list'
            elif selected_endpoint == "Deduct Deposit & Splitfee":
                endpoint = '/api/v1.0/merchant/payment-notif'
            elif selected_endpoint == "Deposit Inquiry Withdraw":
                endpoint = '/api/v1.0/emoney/bank-account-inquiry/deposit'
            elif selected_endpoint == "Deposit Withdraw Process":
                endpoint = '/api/v1.0/emoney/transfer-bank/deposit'
            elif selected_endpoint == "Deposit Withdraw Detail":
                endpoint = '/api/v1.0/debit/status-deposit'
        response = Modules.make_http_request(url=baseurl+endpoint, headers=header, body_request=RequestBody)
        self.send_button.config(state=tk.NORMAL)
        if response:
            http_status_code = response[0]
            response_message = response[1]
            response_message = jsonParser.jsonParserBeautify(response_message)
            msgbox = f"HTTP Status Code: {http_status_code}\nResponse Message: {response_message}"
            ResponseOpenAPI(msgbox)
            if selected_endpoint == "Access Token":
                strings = Modules.get_value_from_json(response_message, 'accessToken')
                if strings:
                    self.entry_auth_token.delete(0, tk.END)
                    self.entry_auth_token.insert(0, strings)

    def create_curl(self):
        client_id = self.combo_aggregator_id.get()
        selected_endpoint = self.combo_endpoint.get()
        RequestBody = jsonParser.jsonParserMinify(self.text_body.get("1.0",'end-1c'))
        signatureService = self.entry_signature_service.get()
        signatureAuth = self.entry_signature_auth.get()
        getrawSignatureAuth = self.entry_raw_signature_auth.get()
        getrawSignatureService = self.entry_raw_signature_service.get()
        user_id = self.entry_merchant_id.get()
        auth_token = self.entry_auth_token.get()
        xternal_id = Modules.RandomDigit(32)
        selected_environment = self.combo_environment.get()
        if selected_environment == 'Production':
            baseurl = 'https://tokoapisnap.netzme.com'
        else:
            baseurl = 'https://tokoapisnap-stg.netzme.com'

        if selected_endpoint == "Access Token":
            x_timestamp = getrawSignatureAuth.split("|")[1]
            endpoint = '/api/v1/access-token/b2b'
            header = {"X-TIMESTAMP": x_timestamp, "Content-Type":"application/json", "X-CLIENT-KEY": client_id,"X-SIGNATURE": signatureAuth}
        else:
            parts = getrawSignatureService.split(":")
            x_timestamp = ":".join(parts[4:])
            header = {"X-TIMESTAMP": x_timestamp, "Content-Type":"application/json", "X-SIGNATURE": signatureService, "Authorization": "Bearer "+auth_token, "X-PARTNER-ID":client_id, "X-EXTERNAL-ID":xternal_id, "CHANNEL-ID":"44444"}
            if selected_endpoint == "Create PIN":
                endpoint = '/api/v1.0/merchant/create-pin'
            elif selected_endpoint == "Forgot PIN":
                endpoint = '/api/v1.0/merchant/forgot-pin'
            elif selected_endpoint == "Balance Detail":
                endpoint = '/api/v1.0/payment/balance-inquiry'
            elif selected_endpoint == "Merchant Detail":
                endpoint = '/api/v1.0/registration-account-inquiry'
            elif selected_endpoint == "List Transaction":
                endpoint = '/api/v1.0/transaction/history-list'
            elif selected_endpoint == "Create Invoice":
                endpoint = '/api/v1.0/invoice/create'
            elif selected_endpoint == "Create Invoice Transaction":
                endpoint = '/api/v1.0/invoice/create-transaction'
            elif selected_endpoint == "Get Invoice Transaction":
                endpoint = '/api-invoice/v1.0/transaction-history-detail'
            elif selected_endpoint == "Merchant Inquiry Withdraw":
                endpoint = '/api/v1.0/emoney/bank-account-inquiry'
            elif selected_endpoint == "Merchant Withdraw Process":
                endpoint = '/api/v1.0/emoney/transfer-bank'
            elif selected_endpoint == "Merchant Withdraw Detail":
                endpoint = '/api/v1.0/debit/status'
            elif selected_endpoint == "Get QRIS Acquirer Trx":
                endpoint = '/api-qris/v1.0/transaction-history-detail'
            elif selected_endpoint == "Get Deposit Balance":
                endpoint = '/api/v1.0/deposit/balance-inquiry'
            elif selected_endpoint == "Deposit Trx List":
                endpoint = '/api/v1.0/deposit/transaction-history-list'
            elif selected_endpoint == "Deduct Deposit & Splitfee":
                endpoint = '/api/v1.0/merchant/payment-notif'
            elif selected_endpoint == "Deposit Inquiry Withdraw":
                endpoint = '/api/v1.0/emoney/bank-account-inquiry/deposit'
            elif selected_endpoint == "Deposit Withdraw Process":
                endpoint = '/api/v1.0/emoney/transfer-bank/deposit'
            elif selected_endpoint == "Deposit Withdraw Detail":
                endpoint = '/api/v1.0/debit/status-deposit'
        output = Modules.generate_curl_command(url=baseurl+endpoint, headers = header, payload=RequestBody)
        ResponseOpenAPI(output)

    def start_thread_connection(self):
        self.send_button.config(state=tk.DISABLED)
        # Memulai thread baru untuk koneksi database
        thread = threading.Thread(target=self.hit_request)
        thread.start()