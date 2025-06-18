# app/tabs/open_api_subtabs/netzme_open_api_subtabs/netzme_snap_tab.py
import tkinter as tk
from tkinter import ttk
from src.modules import Modules
import json
from src.jsonParser import jsonParser
import src.snap as Snap
from app.tabs.popup import ResponseOpenAPI
from app.custom.custom_text import CustomText
import threading

file_config_location = 'config/config_aggregator.json'

class NetzmeSnapTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        string_vars = [tk.StringVar() for _ in range(2)]
        self.y1, self.y16 = string_vars

        variables = [self.y1]
        functions = [self.handle_endpoint_selection]
        for variable, function in zip(variables, functions):
            variable.trace_add('write', lambda *args, func=function: func())

        # Endpoint label and combobox
        self.label_endpoint = tk.Label(self, text="Endpoint")
        self.label_endpoint.place(x=3, y=153)
        self.combo_endpoint = ttk.Combobox(self, textvariable=self.y1, width=55)
        self.combo_endpoint["values"] = ["Access Token", "Get Account Status", "Get Fixed Topup VA", "Get Detail QRIS",
                     "Get Balance", "Get History Transaksi"]
        self.combo_endpoint.config(state="readonly")
        self.combo_endpoint.place(x=110, y=153)


        # AggregatorId label, combobox, and 'Create Curl' button
        self.label_aggregator_id = tk.Label(self, text="AggregatorId")
        self.label_aggregator_id.place(x=3, y=3)
        self.combo_aggregator_id = ttk.Combobox(self, width=55)
        self.combo_aggregator_id['values'] = Modules.getAllAggregatorNetzme()
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

        # Frame User ID & QR Content
        # self.user_content_frame = tk.Frame(self)
        # self.user_content_frame.grid(row=4, column=3, padx=5, pady=5, sticky="w")

        # User ID label and entry
        self.label_user_id = tk.Label(self, text="User ID")
        self.entry_user_id = tk.Entry(self)
        
        # QR Content label and entry
        self.label_qr_content = tk.Label(self, text="QR Content")
        self.entry_qr_content = tk.Entry(self)

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

        self.combo_endpoint.bind("<<ComboboxSelected>>", self.handle_endpoint_selection)
        self.entry_user_id.bind('<KeyRelease>', self.handle_endpoint_selection)
        self.entry_qr_content.bind('<KeyRelease>', self.handle_endpoint_selection)
        #self.loadAwal()

    def loadAwal(self):
        self.update_client_secret()
        self.handle_endpoint_selection()
    
    def update_client_secret(self, event=None):
        selected_aggregator_id = self.combo_aggregator_id.get()
        if not selected_aggregator_id == "":
            getstr = Modules.get_clear_pass_and_token(Modules.get_list_dictionary_config()[1], selected_aggregator_id)
            self.entry_client_secret.delete(0, tk.END)
            self.entry_client_secret.insert(0, getstr[4])
            self.entry_private_key.delete(0, tk.END)
            self.entry_private_key.insert(0, getstr[3])
            self.entry_x_callback_token.delete(0, tk.END)
            self.entry_x_callback_token.insert(0, getstr[2])
            self.handle_endpoint_selection()

    def hide_show_element(self):
        self.label_raw_signature_auth.place(x=17500, y=3)
        self.entry_raw_signature_auth.place(x=17500, y=3)
        self.label_signature_auth.place(x=17500, y=3)
        self.entry_signature_auth.place(x=17500, y=3)
        self.label_raw_signature_service.place(x=17500, y=3)
        self.entry_raw_signature_service.place(x=17500, y=3)
        self.label_signature_service.place(x=17500, y=3)
        self.entry_signature_service.place(x=17500, y=3)
        self.label_user_id.place(x=17500, y=3)
        self.entry_user_id.place(x=17500, y=3)
        self.label_qr_content.place(x=17500, y=3)
        self.entry_qr_content.place(x=17500, y=3)
        
        selected_endpoint = self.combo_endpoint.get()
        if selected_endpoint == "Access Token":
            self.label_raw_signature_auth.place(x=3, y=183)
            self.entry_raw_signature_auth.place(x=110, y=183)
            self.label_signature_auth.place(x=3, y=213)
            self.entry_signature_auth.place(x=110, y=213)
        else:
            self.label_raw_signature_service.place(x=3, y=183)
            self.entry_raw_signature_service.place(x=110, y=183)
            self.label_signature_service.place(x=3, y=213)
            self.entry_signature_service.place(x=110, y=213)
            if selected_endpoint in ("Get Account Status", "Get Fixed Topup VA", "Get Balance", "Get History Transaksi"):
                self.label_user_id.place(x=750, y=63)
                self.entry_user_id.place(x=840, y=63)
            else:
                self.label_user_id.place(x=750, y=63)
                self.entry_user_id.place(x=840, y=63)
                self.label_qr_content.place(x=750, y=93)
                self.entry_qr_content.place(x=840, y=93)

    def handle_endpoint_selection(self, event=None):
        try:
            self.hide_show_element()
            selected_endpoint = self.combo_endpoint.get()
            user_id = self.entry_user_id.get()
            qr_content = self.entry_qr_content.get()
            partner_ref_no = self.combo_aggregator_id.get() + Modules.RandomDigit(7)
            if selected_endpoint == "Access Token":
                url = '/api/v1/access-token/b2b'
                bodyreq = {"grantType":"client_credentials","additionalInfo":{}}
                self.set_body_text(bodyreq)
            elif selected_endpoint == "Get Detail QRIS":
                url = '/api/v1.0/payment/qr'
                bodyreq = {"partnerReferenceNo":partner_ref_no,"qrContent":qr_content,"amount":{"value":"199990","currency":"IDR"},"scanTime":"2020-12-01T08:40:11+07:00","additionalInfo":{"type":"aggregator_scan_qr","custId":user_id}}
                self.set_body_text(bodyreq)
            elif selected_endpoint == "Get Account Status":
                url = '/api/v1.0/account/registration-account-inquiry'
                bodyreq = {"partnerReferenceNo":partner_ref_no,"additionalInfo":{"custId":user_id}}
                self.set_body_text(bodyreq)
            elif selected_endpoint == "Get Fixed Topup VA":
                url = '/api/v1.0/payment/fixed-va?custId=' + user_id
                self.text_body.delete('1.0', tk.END)
            elif selected_endpoint == "Get Balance":
                url = '/api/v1.0/payment/balance-inquiry'
                bodyreq = {"accountNo":user_id,"partnerReferenceNo":partner_ref_no}
                self.set_body_text(bodyreq)
            elif selected_endpoint == "Get History Transaksi":
                url = '/api/v1.0/transaction/history-list'
                bodyreq = {"partnerReferenceNo":partner_ref_no,"pageSize":1,"additionalInfo":{"seqId":0,"custId":user_id,"type":"aggregator_transaction_history"}}
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
        signatureService = self.entry_signature_service.get()
        signatureAuth = self.entry_signature_auth.get()
        getrawSignatureAuth = self.entry_raw_signature_auth.get()
        getrawSignatureService = self.entry_raw_signature_service.get()
        user_id = self.entry_user_id.get()
        auth_token = self.entry_auth_token.get()
        xternal_id = Modules.RandomDigit(32)
        baseurl = 'https://apisnap-stg.netzme.com'
        if selected_endpoint == "Access Token":
            x_timestamp = getrawSignatureAuth.split("|")[1]
            endpoint = '/api/v1/access-token/b2b'
            header = {"X-TIMESTAMP": x_timestamp, "Content-Type":"application/json", "X-CLIENT-KEY": client_id,"X-SIGNATURE": signatureAuth}
        else:
            parts = getrawSignatureService.split(":")
            x_timestamp = ":".join(parts[4:])
            header = {"X-TIMESTAMP": x_timestamp, "Content-Type":"application/json", "X-SIGNATURE": signatureService, "Authorization": "Bearer "+auth_token, "X-PARTNER-ID":client_id, "X-EXTERNAL-ID":xternal_id, "CHANNEL-ID":"44444"}
            if selected_endpoint == "Get Detail QRIS":
                endpoint = '/api/v1.0/payment/qr'
            elif selected_endpoint == "Get Account Status":
                endpoint = '/api/v1.0/account/registration-account-inquiry'
            elif selected_endpoint == "Get Fixed Topup VA":
                endpoint = '/api/v1.0/payment/fixed-va?custId=' + user_id
            elif selected_endpoint == "Get Balance":
                endpoint = '/api/v1.0/payment/balance-inquiry'
            elif selected_endpoint == "Get History Transaksi":
                endpoint = '/api/v1.0/transaction/history-list'
        response = Modules.make_http_request(url=baseurl+endpoint, headers=header, body_request=RequestBody)
        self.send_button.config(state=tk.NORMAL)
        if response:
            http_status_code, response_message = response
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
        user_id = self.entry_user_id.get()
        auth_token = self.entry_auth_token.get()
        xternal_id = Modules.RandomDigit(32)
        baseurl = 'https://apisnap-stg.netzme.com'
        if selected_endpoint == "Access Token":
            x_timestamp = getrawSignatureAuth.split("|")[1]
            endpoint = '/api/v1/access-token/b2b'
            header = {"X-TIMESTAMP": x_timestamp, "Content-Type":"application/json", "X-CLIENT-KEY": client_id,"X-SIGNATURE": signatureAuth}
        else:
            parts = getrawSignatureService.split(":")
            x_timestamp = ":".join(parts[4:])
            header = {"X-TIMESTAMP": x_timestamp, "Content-Type":"application/json", "X-SIGNATURE": signatureService, "Authorization": "Bearer "+auth_token, "X-PARTNER-ID":client_id, "X-EXTERNAL-ID":xternal_id, "CHANNEL-ID":"44444"}
            if selected_endpoint == "Get Detail QRIS":
                endpoint = '/api/v1.0/payment/qr'
            elif selected_endpoint == "Get Account Status":
                endpoint = '/api/v1.0/account/registration-account-inquiry'
            elif selected_endpoint == "Get Fixed Topup VA":
                endpoint = '/api/v1.0/payment/fixed-va?custId=' + user_id
            elif selected_endpoint == "Get Balance":
                endpoint = '/api/v1.0/payment/balance-inquiry'
            elif selected_endpoint == "Get History Transaksi":
                endpoint = '/api/v1.0/transaction/history-list'
        output = Modules.generate_curl_command(url=baseurl+endpoint, headers = header, payload=RequestBody)
        ResponseOpenAPI(output)

    def start_thread_connection(self):
        self.send_button.config(state=tk.DISABLED)
        # Memulai thread baru untuk koneksi database
        thread = threading.Thread(target=self.hit_request)
        thread.start()
