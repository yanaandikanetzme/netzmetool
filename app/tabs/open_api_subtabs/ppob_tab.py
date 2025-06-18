#lokasi /app/tabs/open_api_subtabs/ppob_tab.py
import tkinter as tk
from tkinter import ttk, messagebox
import json
import requests
from uuid import uuid4
from datetime import datetime, timedelta
import base64
import hashlib
import hmac
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from src.jsonParser import jsonParser
from src.modules import Modules
from app.tabs.popup import ResponseOpenAPI
from src.ppob import PPOB
import threading


class PPOBOpenAPITab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.load_config()
        self.create_widgets()
        self.update_request_body()

    def load_config(self):
        with open('config/config_aggregator.json', 'r') as file:
            self.config_data = json.load(file)
        self.ppob_clients = self.config_data[0].get('PPOB', [])
        self.client_ids = [client['clientId'] for client in self.ppob_clients]

    def update_credentials(self, event=None):
        selected_client_id = self.client_id_combo.get()
        client_data = next((client for client in self.ppob_clients if client['clientId'] == selected_client_id), None)
        
        if client_data:
            self.client_key_entry.delete(0, tk.END)
            self.client_key_entry.insert(0, client_data.get('clientKey', ''))
            
            self.client_key_pattern_entry.delete(0, tk.END)
            self.client_key_pattern_entry.insert(0, client_data.get('clientKeyPattern', ''))
            
            self.private_key_entry.delete(0, tk.END)
            self.private_key_entry.insert(0, client_data.get('privateKey', ''))

        self.update_request_body()

    def create_widgets(self):
        self.main_frame = tk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.left_frame = tk.Frame(self.main_frame, width=400)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.right_frame = tk.Frame(self.main_frame, width=400)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.create_credential_frame()
        self.create_request_fields_frame()
        self.create_request_body_frame()
        self.create_signature_frame()
        self.create_button_frame()
    
    def create_credential_frame(self):
        self.credential_frame = ttk.LabelFrame(self.left_frame, text="Credentials")
        self.credential_frame.pack(fill=tk.X, pady=(0, 10))

        self.client_id_frame = tk.Frame(self.credential_frame)
        self.client_id_frame.pack(fill=tk.X, padx=5, pady=2)
        self.client_id_label = tk.Label(self.client_id_frame, text="CLIENT_ID", width=15, anchor='w')
        self.client_id_label.pack(side=tk.LEFT)
        self.client_id_combo = ttk.Combobox(self.client_id_frame, values=self.client_ids, state="readonly")
        self.client_id_combo.pack(side=tk.LEFT, expand=True, fill=tk.X)
        self.client_id_combo.bind("<<ComboboxSelected>>", self.update_credentials)

        self.client_key_frame = tk.Frame(self.credential_frame)
        self.client_key_frame.pack(fill=tk.X, padx=5, pady=2)
        self.client_key_label = tk.Label(self.client_key_frame, text="CLIENT_KEY", width=15, anchor='w')
        self.client_key_label.pack(side=tk.LEFT)
        self.client_key_entry = tk.Entry(self.client_key_frame)
        self.client_key_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)

        self.client_key_pattern_frame = tk.Frame(self.credential_frame)
        self.client_key_pattern_frame.pack(fill=tk.X, padx=5, pady=2)
        self.client_key_pattern_label = tk.Label(self.client_key_pattern_frame, text="CLIENT_KEY_PATTERN", width=15, anchor='w')
        self.client_key_pattern_label.pack(side=tk.LEFT)
        self.client_key_pattern_entry = tk.Entry(self.client_key_pattern_frame)
        self.client_key_pattern_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)

        self.private_key_frame = tk.Frame(self.credential_frame)
        self.private_key_frame.pack(fill=tk.X, padx=5, pady=2)
        self.private_key_label = tk.Label(self.private_key_frame, text="PRIVATE_KEY", width=15, anchor='w')
        self.private_key_label.pack(side=tk.LEFT)
        self.private_key_entry = tk.Entry(self.private_key_frame)
        self.private_key_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)

        self.token_frame = tk.Frame(self.credential_frame)
        self.token_frame.pack(fill=tk.X, padx=5, pady=2)
        self.token_label = tk.Label(self.token_frame, text="Token", width=15, anchor='w')
        self.token_label.pack(side=tk.LEFT)
        self.token_entry = tk.Entry(self.token_frame)
        self.token_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)

        self.token_expired_frame = tk.Frame(self.credential_frame)
        self.token_expired_frame.pack(fill=tk.X, padx=5, pady=2)
        self.token_expired_label = tk.Label(self.token_expired_frame, text="Token Expired", width=15, anchor='w')
        self.token_expired_label.pack(side=tk.LEFT)
        self.token_expired_entry = tk.Entry(self.token_expired_frame)
        self.token_expired_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)

    def create_request_fields_frame(self):
        self.fields_frame = ttk.LabelFrame(self.left_frame, text="Request Fields")
        self.fields_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        self.endpoint_frame = tk.Frame(self.fields_frame)
        self.endpoint_frame.pack(fill=tk.X, padx=5, pady=5)
        self.endpoint_label = tk.Label(self.endpoint_frame, text="Select Endpoint:", width=15, anchor='w')
        self.endpoint_label.pack(side=tk.LEFT)
        self.endpoint_combo = ttk.Combobox(self.endpoint_frame, values=[
            "Get Token PPOB",
            "Get Token Disbursement", 
            "Account Inquiry", 
            "Disburse",
            "Get Balance",
            "Get List Product",
            "Get Detail Product",
            "Web View",
            "Validate Users"
        ], state="readonly")
        self.endpoint_combo.pack(side=tk.LEFT, expand=True, fill=tk.X)
        self.endpoint_combo.bind("<<ComboboxSelected>>", self.update_reqtime_reqid)
        self.endpoint_combo.set("Get Token PPOB")

        self.request_id_frame = tk.Frame(self.fields_frame)
        self.request_id_frame.pack(fill=tk.X, padx=5, pady=2)
        self.request_id_label = tk.Label(self.request_id_frame, text="requestId", width=15, anchor='w')
        self.request_id_label.pack(side=tk.LEFT)
        self.request_id_entry = tk.Entry(self.request_id_frame)
        self.request_id_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)
        self.request_id_entry.bind("<KeyRelease>", self.update_request_body)

        self.request_time_frame = tk.Frame(self.fields_frame)
        self.request_time_frame.pack(fill=tk.X, padx=5, pady=2)
        self.request_time_label = tk.Label(self.request_time_frame, text="requestTime", width=15, anchor='w')
        self.request_time_label.pack(side=tk.LEFT)
        self.request_time_entry = tk.Entry(self.request_time_frame)
        self.request_time_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)
        self.request_time_entry.bind("<KeyRelease>", self.update_request_body)

        self.merchant_id_frame = tk.Frame(self.fields_frame)
        self.merchant_id_frame.pack(fill=tk.X, padx=5, pady=2)
        self.merchant_id_label = tk.Label(self.merchant_id_frame, text="merchantId", width=15, anchor='w')
        self.merchant_id_label.pack(side=tk.LEFT)
        self.merchant_id_entry = tk.Entry(self.merchant_id_frame)
        self.merchant_id_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)
        self.merchant_id_entry.bind("<KeyRelease>", self.update_request_body)

        # partner_trx_id
        self.partner_trx_id_frame = tk.Frame(self.fields_frame)
        self.partner_trx_id_frame.pack(fill=tk.X, padx=5, pady=2)
        self.partner_trx_id_label = tk.Label(self.partner_trx_id_frame, text="partner_trx_id", width=15, anchor='w')
        self.partner_trx_id_label.pack(side=tk.LEFT)
        self.partner_trx_id_entry = tk.Entry(self.partner_trx_id_frame)
        self.partner_trx_id_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)
        self.partner_trx_id_entry.bind("<KeyRelease>", self.update_request_body)

        # account_number
        self.account_number_frame = tk.Frame(self.fields_frame)
        self.account_number_frame.pack(fill=tk.X, padx=5, pady=2)
        self.account_number_label = tk.Label(self.account_number_frame, text="account_number", width=15, anchor='w')
        self.account_number_label.pack(side=tk.LEFT)
        self.account_number_entry = tk.Entry(self.account_number_frame)
        self.account_number_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)
        self.account_number_entry.bind("<KeyRelease>", self.update_request_body)

        # bank_code
        self.bank_code_frame = tk.Frame(self.fields_frame)
        self.bank_code_frame.pack(fill=tk.X, padx=5, pady=2)
        self.bank_code_label = tk.Label(self.bank_code_frame, text="bank_code", width=15, anchor='w')
        self.bank_code_label.pack(side=tk.LEFT)
        self.bank_code_entry = tk.Entry(self.bank_code_frame)
        self.bank_code_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)
        self.bank_code_entry.bind("<KeyRelease>", self.update_request_body)

        # account_holder_name
        self.account_holder_name_frame = tk.Frame(self.fields_frame)
        self.account_holder_name_frame.pack(fill=tk.X, padx=5, pady=2)
        self.account_holder_name_label = tk.Label(self.account_holder_name_frame, text="account_holder_name", width=15, anchor='w')
        self.account_holder_name_label.pack(side=tk.LEFT)
        self.account_holder_name_entry = tk.Entry(self.account_holder_name_frame)
        self.account_holder_name_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)
        self.account_holder_name_entry.bind("<KeyRelease>", self.update_request_body)

        # amount
        self.amount_frame = tk.Frame(self.fields_frame)
        self.amount_frame.pack(fill=tk.X, padx=5, pady=2)
        self.amount_label = tk.Label(self.amount_frame, text="amount", width=15, anchor='w')
        self.amount_label.pack(side=tk.LEFT)
        self.amount_entry = tk.Entry(self.amount_frame)
        self.amount_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)
        self.amount_entry.bind("<KeyRelease>", self.update_request_body)

        # remark
        self.remark_frame = tk.Frame(self.fields_frame)
        self.remark_frame.pack(fill=tk.X, padx=5, pady=2)
        self.remark_label = tk.Label(self.remark_frame, text="remark", width=15, anchor='w')
        self.remark_label.pack(side=tk.LEFT)
        self.remark_entry = tk.Entry(self.remark_frame)
        self.remark_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)
        self.remark_entry.bind("<KeyRelease>", self.update_request_body)

        # beneficiary_email
        self.beneficiary_email_frame = tk.Frame(self.fields_frame)
        self.beneficiary_email_frame.pack(fill=tk.X, padx=5, pady=2)
        self.beneficiary_email_label = tk.Label(self.beneficiary_email_frame, text="beneficiary_email", width=15, anchor='w')
        self.beneficiary_email_label.pack(side=tk.LEFT)
        self.beneficiary_email_entry = tk.Entry(self.beneficiary_email_frame)
        self.beneficiary_email_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)
        self.beneficiary_email_entry.bind("<KeyRelease>", self.update_request_body)

        # Initialize requestId, requestTime
        self.request_id_entry.insert(0, str(uuid4()))
        self.request_time_entry.insert(0, str(int(datetime.now().timestamp() * 1000)))

        # Product ID field
        self.product_id_frame = tk.Frame(self.fields_frame)
        self.product_id_frame.pack(fill=tk.X, padx=5, pady=2)
        self.product_id_label = tk.Label(self.product_id_frame, text="product_id", width=15, anchor='w')
        self.product_id_label.pack(side=tk.LEFT)
        self.product_id_entry = tk.Entry(self.product_id_frame)
        self.product_id_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)
        
        # List Product fields
        self.limit_frame = tk.Frame(self.fields_frame)
        self.limit_frame.pack(fill=tk.X, padx=5, pady=2)
        self.limit_label = tk.Label(self.limit_frame, text="limit", width=15, anchor='w')
        self.limit_label.pack(side=tk.LEFT)
        self.limit_entry = tk.Entry(self.limit_frame)
        self.limit_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)
        
        self.page_frame = tk.Frame(self.fields_frame)
        self.page_frame.pack(fill=tk.X, padx=5, pady=2)
        self.page_label = tk.Label(self.page_frame, text="page", width=15, anchor='w')
        self.page_label.pack(side=tk.LEFT)
        self.page_entry = tk.Entry(self.page_frame)
        self.page_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)
        
        self.search_frame = tk.Frame(self.fields_frame)
        self.search_frame.pack(fill=tk.X, padx=5, pady=2)
        self.search_label = tk.Label(self.search_frame, text="search", width=15, anchor='w')
        self.search_label.pack(side=tk.LEFT)
        self.search_entry = tk.Entry(self.search_frame)
        self.search_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)
        
        self.order_by_frame = tk.Frame(self.fields_frame)
        self.order_by_frame.pack(fill=tk.X, padx=5, pady=2)
        self.order_by_label = tk.Label(self.order_by_frame, text="orderBy", width=15, anchor='w')
        self.order_by_label.pack(side=tk.LEFT)
        self.order_by_entry = tk.Entry(self.order_by_frame)
        self.order_by_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)
        
        self.sort_frame = tk.Frame(self.fields_frame)
        self.sort_frame.pack(fill=tk.X, padx=5, pady=2)
        self.sort_label = tk.Label(self.sort_frame, text="sort", width=15, anchor='w')
        self.sort_label.pack(side=tk.LEFT)
        self.sort_entry = tk.Entry(self.sort_frame)
        self.sort_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)

        # Add new fields for Validate Users
        self.denom_code_frame = tk.Frame(self.fields_frame)
        self.denom_code_frame.pack(fill=tk.X, padx=5, pady=2)
        self.denom_code_label = tk.Label(self.denom_code_frame, text="denomCode", width=15, anchor='w')
        self.denom_code_label.pack(side=tk.LEFT)
        self.denom_code_entry = tk.Entry(self.denom_code_frame)
        self.denom_code_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)
        self.denom_code_entry.bind("<KeyRelease>", self.update_request_body)

        self.user_id_frame = tk.Frame(self.fields_frame)
        self.user_id_frame.pack(fill=tk.X, padx=5, pady=2)
        self.user_id_label = tk.Label(self.user_id_frame, text="userId", width=15, anchor='w')
        self.user_id_label.pack(side=tk.LEFT)
        self.user_id_entry = tk.Entry(self.user_id_frame)
        self.user_id_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)
        self.user_id_entry.bind("<KeyRelease>", self.update_request_body)

        self.zone_id_frame = tk.Frame(self.fields_frame)
        self.zone_id_frame.pack(fill=tk.X, padx=5, pady=2)
        self.zone_id_label = tk.Label(self.zone_id_frame, text="zoneId", width=15, anchor='w')
        self.zone_id_label.pack(side=tk.LEFT)
        self.zone_id_entry = tk.Entry(self.zone_id_frame)
        self.zone_id_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)
        self.zone_id_entry.bind("<KeyRelease>", self.update_request_body)

    def create_request_body_frame(self):
        # URL Display Frame
        self.url_frame = ttk.LabelFrame(self.right_frame, text="URL")
        self.url_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.url_label = tk.Label(self.url_frame, text="Endpoint URL:")
        self.url_label.pack(anchor='w', padx=5, pady=(5, 0))
        
        self.url_entry = tk.Entry(self.url_frame)
        self.url_entry.pack(fill=tk.X, padx=5, pady=(0, 5))
        self.url_entry.config(state='readonly')  # Make it read-only
        
        # Request Body Frame
        self.request_frame = ttk.LabelFrame(self.right_frame, text="Request")
        self.request_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        self.body_label = tk.Label(self.request_frame, text="Request Body:")
        self.body_label.pack(anchor='w', padx=5, pady=(5, 0))

        self.body_text = tk.Text(self.request_frame, height=20, width=60)
        self.body_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def create_signature_frame(self):
        self.signature_frame = ttk.LabelFrame(self.right_frame, text="Signatures")
        self.signature_frame.pack(fill=tk.X, pady=(0, 10))

        self.signature_token_label = tk.Label(self.signature_frame, text="Signature Token:")
        self.signature_token_label.pack(anchor='w', padx=5, pady=(5, 0))
        self.signature_token_entry = tk.Entry(self.signature_frame, width=60)
        self.signature_token_entry.pack(fill=tk.X, padx=5, pady=(0, 5))

        self.signature_transaction_label = tk.Label(self.signature_frame, text="Signature Transaction:")
        self.signature_transaction_label.pack(anchor='w', padx=5, pady=(5, 0))
        self.signature_transaction_entry = tk.Entry(self.signature_frame, width=60)
        self.signature_transaction_entry.pack(fill=tk.X, padx=5, pady=(0, 5))

    def create_button_frame(self):
        self.button_frame = tk.Frame(self.right_frame)
        self.button_frame.pack(fill=tk.X, pady=(0, 10))
        self.generate_curl_button = tk.Button(self.button_frame, text="Generate cURL", command=self.generate_curl)
        self.generate_curl_button.pack(side=tk.LEFT, padx=(0, 5))
        self.send_button = tk.Button(self.button_frame, text="Send Request", command=self.start_thread_connection)
        self.send_button.pack(side=tk.LEFT)

    def update_request_body(self, event=None):
        self.show_or_hide_field()
        private_key = self.private_key_entry.get()
        body_request = self.body_text.get("1.0", "end-1c")

        selected_endpoint = self.endpoint_combo.get()
        if selected_endpoint in ["Get Token Disbursement","Get Token PPOB"]:
            # Generate body for "Get Token Disbursement"
            body = {
                "requestId": self.request_id_entry.get(),
                "requestTime": int(self.request_time_entry.get()),
                "type": "TYPE_GENERATE_TOKEN",
                "body": {
                    "merchantId": self.merchant_id_entry.get(),
                    "webview": False,
                    "additionalInfo": ""
                }
            }
        elif selected_endpoint == "Account Inquiry":
            # Generate body for "Account Inquiry"
            body = {
                "type": "DISBURSEMENT_ACCOUNT_INQUIRY",
                "body": {
                    "merchantId": self.merchant_id_entry.get(),
                    "partner_trx_id": self.partner_trx_id_entry.get(),
                    "account_number": self.account_number_entry.get(),
                    "bank_code": self.bank_code_entry.get()
                }
            }
        elif selected_endpoint == "Disburse":
            # Generate body for "Disburse"
            body = {
                "type": "DISBURSEMENT_DISBURSE",
                "body": {
                    "merchantId": self.merchant_id_entry.get(),
                    "partner_trx_id": self.partner_trx_id_entry.get(),
                    "account_number": self.account_number_entry.get(),
                    "account_holder_name": self.account_holder_name_entry.get(),
                    "bank_code": self.bank_code_entry.get(),
                    "amount": self.amount_entry.get(),
                    "remark": self.remark_entry.get(),
                    "direction": "DOMESTIC_SPECIAL_TRANSFER",
                    "beneficiary_email": self.beneficiary_email_entry.get()
                }
            }
        elif selected_endpoint == "Validate Users":
            body = {
                "type": "VALIDATE_PRODUCT",
                "body": {
                    "merchantId": self.merchant_id_entry.get(),
                    "denomCode": self.denom_code_entry.get(),
                    "fields": {
                        "userid": self.user_id_entry.get(),
                        "zoneid": self.zone_id_entry.get()
                    }
                }
            }
        else:
            body = ""
        
        # Display the request body in the Text widget
        self.body_text.delete(1.0, tk.END)  # Clear current content
        self.body_text.insert(tk.END, json.dumps(body, indent=4))  # Insert new body with proper formatting
        if private_key != '' and body_request != '':
            self.generate_signature()

    def update_reqtime_reqid(self, event=None):
        uuid_value = str(uuid4())
        timestamp_value = str(int(datetime.now().timestamp() * 1000))
        selected_endpoint = self.endpoint_combo.get()
        if selected_endpoint in ["Get Token Disbursement", "Get Token PPOB", "Web View"]:
            # Set UUID for request_id
            self.request_id_entry.delete(0, tk.END)
            self.request_id_entry.insert(0, uuid_value)
            
            # Set timestamp for request_time
            self.request_time_entry.delete(0, tk.END)
            self.request_time_entry.insert(0, timestamp_value)
            
        elif selected_endpoint in ["Account Inquiry", "Disburse"]:
            # Set UUID for partner_trx_id
            self.partner_trx_id_entry.delete(0, tk.END)
            self.partner_trx_id_entry.insert(0, uuid_value)
            
            if selected_endpoint == "Disburse":
                # Set UUID for request_id
                self.request_id_entry.delete(0, tk.END)
                self.request_id_entry.insert(0, uuid_value)
                # Set timestamp for request_time
                self.request_time_entry.delete(0, tk.END)
                self.request_time_entry.insert(0, timestamp_value)
        self.update_request_body()
                
    def show_or_hide_field(self):
        selected_endpoint = self.endpoint_combo.get()
        # Hide all fields initially
        for frame in [
            self.request_id_frame, self.request_time_frame, self.merchant_id_frame, 
            self.partner_trx_id_frame, self.account_number_frame, self.bank_code_frame, 
            self.account_holder_name_frame, self.amount_frame, self.remark_frame, 
            self.beneficiary_email_frame, self.product_id_frame, self.limit_frame,
            self.page_frame, self.search_frame, self.order_by_frame, self.sort_frame,
            self.denom_code_frame, self.user_id_frame, self.zone_id_frame
        ]:
            frame.pack_forget()
            
        # Update the URL display
        
        if selected_endpoint == "Web View":
            baseurl =  'https://toko-web-vgame-stg.netzme.com'
        else:
            baseurl = 'https://tokoapi-stg.netzme.com'
        endpoint_url = self.get_endpoint_url()
        full_url = baseurl + endpoint_url
        
        # Configure the URL entry
        self.url_entry.config(state='normal')  # Temporarily enable for updating
        self.url_entry.delete(0, tk.END)
        self.url_entry.insert(0, full_url)
        self.url_entry.config(state='readonly')  # Make it read-only again
        
        # Show fields based on the selected endpoint
        if selected_endpoint in ["Get Token Disbursement", "Get Token PPOB", "Web View"]:
            self.request_id_frame.pack(fill=tk.X, padx=5, pady=2)
            self.request_time_frame.pack(fill=tk.X, padx=5, pady=2)
            self.merchant_id_frame.pack(fill=tk.X, padx=5, pady=2)
        elif selected_endpoint == "Account Inquiry":
            self.merchant_id_frame.pack(fill=tk.X, padx=5, pady=2)
            self.partner_trx_id_frame.pack(fill=tk.X, padx=5, pady=2)
            self.account_number_frame.pack(fill=tk.X, padx=5, pady=2)
            self.bank_code_frame.pack(fill=tk.X, padx=5, pady=2)
        elif selected_endpoint == "Disburse":
            self.merchant_id_frame.pack(fill=tk.X, padx=5, pady=2)
            self.partner_trx_id_frame.pack(fill=tk.X, padx=5, pady=2)
            self.account_number_frame.pack(fill=tk.X, padx=5, pady=2)
            self.account_holder_name_frame.pack(fill=tk.X, padx=5, pady=2)
            self.bank_code_frame.pack(fill=tk.X, padx=5, pady=2)
            self.amount_frame.pack(fill=tk.X, padx=5, pady=2)
            self.remark_frame.pack(fill=tk.X, padx=5, pady=2)
            self.beneficiary_email_frame.pack(fill=tk.X, padx=5, pady=2)
        elif selected_endpoint == "Get Balance":
            self.merchant_id_frame.pack(fill=tk.X, padx=5, pady=2)
        elif selected_endpoint == "Get List Product":
            self.merchant_id_frame.pack(fill=tk.X, padx=5, pady=2)
            self.limit_frame.pack(fill=tk.X, padx=5, pady=2)
            self.page_frame.pack(fill=tk.X, padx=5, pady=2)
            self.search_frame.pack(fill=tk.X, padx=5, pady=2)
            self.order_by_frame.pack(fill=tk.X, padx=5, pady=2)
            self.sort_frame.pack(fill=tk.X, padx=5, pady=2)
        elif selected_endpoint == "Get Detail Product":
            self.merchant_id_frame.pack(fill=tk.X, padx=5, pady=2)
            self.product_id_frame.pack(fill=tk.X, padx=5, pady=2)
        elif selected_endpoint == "Validate Users":
            self.merchant_id_frame.pack(fill=tk.X, padx=5, pady=2)
            self.denom_code_frame.pack(fill=tk.X, padx=5, pady=2)
            self.user_id_frame.pack(fill=tk.X, padx=5, pady=2)
            self.zone_id_frame.pack(fill=tk.X, padx=5, pady=2)

    def get_endpoint_url(self):
        selected_endpoint = self.endpoint_combo.get()
        if selected_endpoint == "Get Token Disbursement":
            url = '/public/api/disbursement-auth/v1/get-token'
        elif selected_endpoint == "Account Inquiry":
            url = '/public/api/disbursement/v1/account-inquiry'
        elif selected_endpoint == "Disburse":
            url = '/public/api/disbursement/v1/disburse'
        elif selected_endpoint == "Get Token PPOB":
            url = '/public/api/ppob/v1/get-token'
        elif selected_endpoint == "Get Balance":
            merchant_id = self.merchant_id_entry.get()
            url = f'/public/api/ppob/v1/balance?merchantId={merchant_id}'
        elif selected_endpoint == "Get List Product":
            merchant_id = self.merchant_id_entry.get()
            limit = self.limit_entry.get() or "10"
            page = self.page_entry.get() or "1"
            search = self.search_entry.get() or ""
            order_by = self.order_by_entry.get() or "category_name"
            sort = self.sort_entry.get() or "asc"
            url = f'/public/api/ppob/v1/product?limit={limit}&page={page}&search={search}&orderBy={order_by}&merchantId={merchant_id}&sort={sort}'
        elif selected_endpoint == "Get Detail Product":
            merchant_id = self.merchant_id_entry.get()
            product_id = self.product_id_entry.get()
            url = f'/public/api/ppob/v1/product/{product_id}?merchantId={merchant_id}'
        elif selected_endpoint == "Web View":
            merchant_id = self.merchant_id_entry.get()
            token = self.token_entry.get()
            url = f'/game-top-up?token={token}&merchantId={merchant_id}'
        elif selected_endpoint == "Validate Users":
            url = '/public/api/ppob/v1/product/validate'
        return url

    def generate_signature(self, event=None):
        selected_endpoint = self.endpoint_combo.get()
        private_key = self.private_key_entry.get()
        body_request = self.body_text.get("1.0", "end-1c")
        parsed_json = json.loads(body_request)
        minified_json = json.dumps(parsed_json, separators=(',', ':'))
        client_id = self.client_id_combo.get()
        client_patern_key = self.client_key_pattern_entry.get()
        client_key = self.client_key_entry.get()
        endpoint_url = self.get_endpoint_url()
        exp_ts = int(self.token_expired_entry.get()) if self.token_expired_entry.get() else 0
        if selected_endpoint in ["Get Token Disbursement", "Get Token PPOB"]:
            signature_token = PPOB.generate_signature_token(private_key, minified_json)
            self.signature_token_entry.delete(0, tk.END)
            self.signature_token_entry.insert(0, signature_token)
        else:
            if selected_endpoint in ["Get Balance", "Get List Product", "Get Detail Product", "Web View"]:
                signature_trx = PPOB.generate_signature_trx(client_id=client_id, client_key_pattern=client_patern_key, client_key=client_key, path_url=endpoint_url, expired_at=exp_ts)
                self.signature_transaction_entry.delete(0, tk.END)
                self.signature_transaction_entry.insert(0, signature_trx)
            else:
                signature_trx = PPOB.generate_signature_trx(client_id=client_id, client_key_pattern=client_patern_key, client_key=client_key, path_url=endpoint_url, bodyreq=minified_json, expired_at=exp_ts)
                self.signature_transaction_entry.delete(0, tk.END)
                self.signature_transaction_entry.insert(0, signature_trx)

    def start_thread_connection(self):
        self.send_button.config(state=tk.DISABLED)
        # Memulai thread baru untuk koneksi database
        thread = threading.Thread(target=self.send_request)
        thread.start()

    def send_request(self):
        baseurl = 'https://tokoapi-stg.netzme.com'
        selected_endpoint = self.endpoint_combo.get()
        client_id = self.client_id_combo.get()
        timestamp = self.request_time_entry.get()
        request_id = self.request_id_entry.get()
        xsignature_token = self.signature_token_entry.get()
        xsignature_trx = self.signature_transaction_entry.get()
        xtoken = self.token_entry.get()
        endpoint = self.get_endpoint_url()
        
        if selected_endpoint == "Web View":
            get_url = self.url_entry.get()
            signature_trx = self.signature_transaction_entry.get()
            client_id = self.client_id_combo.get()
            timestamp = self.request_time_entry.get()
            request_id = self.request_id_entry.get()
            addition = f'&X-MSG-ID={request_id}&X-TIMESTAMP={timestamp}&X-SIGNATURE={signature_trx}&X-CLIENT-ID={client_id}'
            url = get_url + addition
            ResponseOpenAPI(url)
        else:
            if selected_endpoint in ["Get Token Disbursement", "Get Token PPOB"]:
                header = {
                    'Content-Type':'application/json', 
                    'X-CLIENT-ID':client_id,
                    'X-TIMESTAMP':timestamp,
                    'X-MSG-ID':request_id,
                    'X-SIGNATURE':xsignature_token
                }
            else:
                header = {
                    'Content-Type':'application/json', 
                    'X-CLIENT-ID':client_id,
                    'X-TIMESTAMP':timestamp,
                    'X-MSG-ID':request_id,
                    'X-SIGNATURE':xsignature_trx, 
                    'X-AUTHORIZATION':xtoken
                }

            if selected_endpoint in ["Get Balance", "Get List Product", "Get Detail Product"]:
                body_request = self.body_text.get("1.0", "end-1c")
                print(f'url : {baseurl+endpoint}\nheader : {header}\n')
                response = Modules.make_http_request(url=baseurl+endpoint, headers=header)
            else:
                body_request = self.body_text.get("1.0", "end-1c")
                parsed_json = json.loads(body_request)
                minified_json = json.dumps(parsed_json, separators=(',', ':'))
                print(f'url : {baseurl+endpoint}\nheader : {header}\nbody : {minified_json}')
                response = Modules.make_http_request(url=baseurl+endpoint, headers=header, body_request=minified_json)

            if response:
                http_status_code = response[0]
                response_message = response[1]
                response_message = jsonParser.jsonParserBeautify(response_message)
                msgbox = f"HTTP Status Code: {http_status_code}\nResponse Message: {response_message}"
                ResponseOpenAPI(msgbox)
                if selected_endpoint in ["Get Token Disbursement", "Get Token PPOB"] and Modules.get_value_from_json(response_message, 'status') == '100':
                    strings = Modules.get_value_from_json(response_message, 'body.token')
                    expired_token_ts = Modules.get_value_from_json(response_message, 'body.expiredToken')
                    if strings:
                        self.token_entry.delete(0, tk.END)
                        self.token_entry.insert(0, strings)
                    if expired_token_ts:
                        self.token_expired_entry.delete(0, tk.END)
                        self.token_expired_entry.insert(0, expired_token_ts)
        self.send_button.config(state=tk.NORMAL)

    def generate_curl(self):
        """
        Generate cURL command based on current request parameters and print to console
        """
        baseurl = 'https://tokoapi-stg.netzme.com'
        selected_endpoint = self.endpoint_combo.get()
        client_id = self.client_id_combo.get()
        timestamp = self.request_time_entry.get()
        request_id = self.request_id_entry.get()
        xsignature_token = self.signature_token_entry.get()
        xsignature_trx = self.signature_transaction_entry.get()
        xtoken = self.token_entry.get()
        body_request = self.body_text.get("1.0", "end-1c")
        
        # Format the body request as valid JSON
        try:
            parsed_json = json.loads(body_request)
            formatted_body = json.dumps(parsed_json, separators=(',', ':'))
        except json.JSONDecodeError:
            print("Error: Invalid JSON in request body")
            return
        
        # Start building the cURL command
        endpoint = self.get_endpoint_url()
        curl_cmd = f'curl -X POST "{baseurl}{endpoint}" \\\n'
        curl_cmd += '  -H "Content-Type: application/json" \\\n'
        curl_cmd += f'  -H "X-CLIENT-ID: {client_id}" \\\n'
        curl_cmd += f'  -H "X-TIMESTAMP: {timestamp}" \\\n'
        curl_cmd += f'  -H "X-MSG-ID: {request_id}" \\\n'
        
        # Add appropriate signature and token headers based on endpoint
        if selected_endpoint == "Get Token Disbursement":
            curl_cmd += f'  -H "X-SIGNATURE: {xsignature_token}" \\\n'
        elif selected_endpoint in ["Account Inquiry", "Disburse"]:
            curl_cmd += f'  -H "X-SIGNATURE: {xsignature_trx}" \\\n'
            curl_cmd += f'  -H "X-AUTHORIZATION: {xtoken}" \\\n'
        
        # Add the request body
        curl_cmd += f'  -d \'{formatted_body}\''
        ResponseOpenAPI(curl_cmd)
        