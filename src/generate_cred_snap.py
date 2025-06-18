import random
import string
from src.modules import Modules
from datetime import datetime
import base64
import hashlib

class AuthHelper:
    def __init__(self, salt: str):
        self.salt = salt

    def hash_password(self, plain_pass: str) -> str:
        return hashlib.md5(self.enriched_password_with_salt(plain_pass, self.salt).encode()).hexdigest()

    def enriched_password_with_salt(self, plain_pass: str, salt: str) -> str:
        return f"{salt}{plain_pass}"

    def get_auth_pair(self, authorization: str):
        splited_auth = authorization.split(" ")
        decoded_auth = base64.b64decode(splited_auth[1]).decode("utf-8")
        return decoded_auth.split(":")

class TokenUtil:
    def generate_token(self) -> str:
        random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=100))
        encoded_string = base64.b64encode(random_string.encode()).decode('utf-8')
        return encoded_string
    

class OAuth2GenerateTokoNetzmeRequestHelper():
    ACTIVE = True
    token = "acbe7051db18b8cfc8b44efd5d2a9ca4a67192cc8ed742589981e6dba036613f"
    encryption_key = "./n37tMe%^4geNt*"
    password_hash_salt = "v2rU4w7HjC"

    def __init__(self):
        self.auth_helper = AuthHelper(self.password_hash_salt)

    def generate_toko_netzme_aggregator_user_snap(self, id, name):
        if self.ACTIVE:
            aggregator_id = id
            aggregator_name = name
            clear_password = ''.join(random.choices(string.ascii_letters + string.digits, k=16))

            base_url_notify = "https://run.mocky.io"
            endpoint_notify = "/v3/1214bbdc-663f-40c0-8f81-7da54482194d"
            base_url_create_invoice = "https://run.mocky.io"
            endpoint_create_invoice = "/v3/1214bbdc-663f-40c0-8f81-7da54482194d"
            base_url_withdraw = "https://run.mocky.io"
            endpoint_withdraw = "/v3/1214bbdc-663f-40c0-8f81-7da54482194d"

            base_url_notify_snap = "https://run.mocky.io"
            endpoint_notify_snap = "/snap/v1/v3/1214bbdc-663f-40c0-8f81-7da54482194d"
            base_url_create_invoice_snap = "https://run.mocky.io"
            endpoint_create_invoice_snap = "/snap/v1/v3/1214bbdc-663f-40c0-8f81-7da54482194d"
            base_url_withdraw_snap = "https://run.mocky.io"
            endpoint_withdraw_snap = "/snap/v1/v3/1214bbdc-663f-40c0-8f81-7da54482194d"

            encrypted_password = Modules.AES128Encrypt(clear_password, self.encryption_key)
            hashed_password = self.auth_helper.hash_password(clear_password)
            x_callback_token = encrypted_password

            base_query = f"""
            insert into ms_api_client(id, name, token, is_active, created_at, updated_at, callback, label, api_type, delete_locked, token_hash, notify_qris_trx, api_version, allow) 
            values (
                (select coalesce(max(id)+1,1) from ms_api_client), 
                '{aggregator_id}', 
                '{encrypted_password}', 
                true, 
                now(), 
                now(), 
                cast('
                {{
                    "notify": {{
                        "url": "{base_url_notify}{endpoint_notify}",
                        "name": "notify",
                        "headers": [],
                        "base_url": "{base_url_notify}",
                        "endpoint": "{endpoint_notify}"
                    }},
                    "create_invoice": {{
                        "url": "{base_url_create_invoice}{endpoint_create_invoice}",
                        "name": "create_invoice",
                        "headers": [],
                        "base_url": "{base_url_create_invoice}",
                        "endpoint": "{endpoint_create_invoice}"
                    }},
                    "withdraw": {{
                        "url": "{base_url_withdraw}{endpoint_withdraw}",
                        "name": "withdraw",
                        "headers": [],
                        "base_url": "{base_url_notify}",
                        "endpoint": "{endpoint_notify}"
                    }},
                    "notify_vsnap": {{
                        "url": "{base_url_notify_snap}{endpoint_notify_snap}",
                        "name": "notify",
                        "headers": ["x-callback-token: {x_callback_token}"],
                        "base_url": "{base_url_notify_snap}",
                        "endpoint": "{endpoint_notify_snap}"
                    }},
                    "create_invoice_vsnap": {{
                        "url": "{base_url_create_invoice_snap}{endpoint_create_invoice_snap}",
                        "name": "create_invoice",
                        "headers": ["x-callback-token: {x_callback_token}"],
                        "base_url": "{base_url_create_invoice_snap}",
                        "endpoint": "{endpoint_create_invoice_snap}"
                    }},
                    "withdraw_vsnap": {{
                        "url": "{base_url_withdraw_snap}{endpoint_withdraw_snap}",
                        "name": "withdraw",
                        "headers": ["x-callback-token: {x_callback_token}"],
                        "base_url": "{base_url_notify_snap}",
                        "endpoint": "{endpoint_notify_snap}"
                    }}
                }}
                ' as jsonb), 
                '{aggregator_name}', 
                'aggregator', 
                true, 
                '{hashed_password}', 
                true, 
                'v3',
                '[
                  {{
                    "path": "v1/invoice/create",
                    "method": "post"
                  }},
                  {{
                    "path": "v1/invoice/payment/success",
                    "method": "post"
                  }},
                  {{
                    "path": "v1/invoice/createTransaction",
                    "method": "post"
                  }}
                ]'::jsonb::jsonb
            );
            """
            
            #print(f"aggregatorId : {aggregator_id}")
            #print(f"aggregatorName : {aggregator_name}")
            #print(f"clearPassword : {clear_password}")
            #print(f"createInvoiceToken : {encrypted_password}")
            #print(f"createInvoiceTokenHash : {hashed_password}")
            #print(f"x-callback-token : {x_callback_token}")
            #print(f"QUERY INSERT : {base_query}")

            output_generator = (
                f"aggregatorId: {aggregator_id}\n"
                f"aggregatorName: {aggregator_name}\n"
                f"clearPassword: {clear_password}\n"
                f"createInvoiceToken: {encrypted_password}\n"
                f"createInvoiceTokenHash: {hashed_password}\n"
                f"x-callback-token: {x_callback_token}\n"
                f"QUERY INSERT: {base_query}"
            )

            return output_generator


class OAuth2GenerateNetzmeRequestHelper():
    ACTIVE = True
    client_id = "xplorin"
    password = "5RjMRpOKc4Bujxsr"
    # Token dari database
    token = "248822f29e39e6ab0eca0f51f3a9a009d2e170e0806658ee2d1901b476733a5a"
    encryption_key = "./n37tMe%^4geNt*"
    password_hash_salt = "ECJBZOXdh1"

    def __init__(self):
        self.auth_helper = AuthHelper(self.password_hash_salt)
        self.token_util = TokenUtil()

    def generate_netzme_aggregator_user_snap(self, id, name):
        if self.ACTIVE:
            aggregator_id = id
            aggregator_name = name
            clear_password = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
            encrypted_password = Modules.AES128Encrypt(clear_password, self.encryption_key)
            hash_password = self.auth_helper.hash_password(clear_password)
            x_callback_token = self.token_util.generate_token()

            base_url_topup = "https://s3qotr3yxo.api.quickmocker.com"
            endpoint_topup = "/callback/topup-notification"

            base_url_notify = "https://s3qotr3yxo.api.quickmocker.com"
            endpoint_notify = "/v3/1214bbdc-663f-40c0-8f81-7da54482194d"

            base_url_cdd = "https://s3qotr3yxo.api.quickmocker.com"
            endpoint_cdd = "/v3/1214bbdc-663f-40c0-8f81-7da54482194d"

            base_url_bill = "https://s3qotr3yxo.api.quickmocker.com"
            endpoint_bill = "/v3/1214bbdc-663f-40c0-8f81-7da54482194d"

            base_url_cdd_snap = "https://s3qotr3yxo.api.quickmocker.com"
            endpoint_cdd_snap = "/v1/account/upgrade"

            base_url_bill_snap = "https://s3qotr3yxo.api.quickmocker.com"
            endpoint_bill_snap = "/v1/debit/notify"

            base_url_notif_snap = "https://s3qotr3yxo.api.quickmocker.com"
            endpoint_notif_snap = "/v1/qr/qr-cpm-notify"

            query = f"""
            INSERT INTO ms_api_client (
                id, name, token, is_active, created_at, updated_at, callback,
                label, notify_qris_trx, token_hash, api_type, is_template, api_version
            )
            VALUES (
                (SELECT COALESCE(MAX(id)+1, 1) FROM ms_api_client),
                '{aggregator_id}',
                '{encrypted_password}',
                TRUE,
                NOW(),
                NOW(),
                CAST(
                    '{{
                        "cdd": {{
                            "url": "{base_url_cdd}{endpoint_cdd}",
                            "name": "cdd",
                            "headers": [],
                            "base_url": "{base_url_cdd}",
                            "endpoint": "{endpoint_cdd}"
                        }},
                        "bill": {{
                            "url": "{base_url_bill}{endpoint_bill}",
                            "name": "bill",
                            "headers": [],
                            "base_url": "{base_url_bill}",
                            "endpoint": "{endpoint_bill}"
                        }},
                        "topup": {{
                            "url": "{base_url_topup}{endpoint_topup}",
                            "name": "topup",
                            "headers": [],
                            "base_url": "{base_url_topup}",
                            "endpoint": "{endpoint_topup}"
                        }},
                        "notify": {{
                            "url": "{base_url_notify}{endpoint_notify}",
                            "name": "notify",
                            "headers": [],
                            "base_url": "{base_url_notify}",
                            "endpoint": "{endpoint_notify}"
                        }},
                        "cdd_vsnap": {{
                            "url": "{base_url_cdd_snap}{endpoint_cdd_snap}",
                            "name": "cdd",
                            "headers": ["x-callback-token: {x_callback_token}"],
                            "base_url": "{base_url_cdd_snap}",
                            "endpoint": "{endpoint_cdd_snap}"
                        }},
                        "bill_vsnap": {{
                            "url": "{base_url_bill_snap}{endpoint_bill_snap}",
                            "name": "bill",
                            "headers": ["x-callback-token: {x_callback_token}"],
                            "base_url": "{base_url_bill_snap}",
                            "endpoint": "{endpoint_bill_snap}"
                        }},
                        "notify_vsnap": {{
                            "url": "{base_url_notif_snap}{endpoint_notif_snap}",
                            "name": "notify",
                            "headers": ["x-callback-token: {x_callback_token}"],
                            "base_url": "{base_url_notif_snap}",
                            "endpoint": "{endpoint_notif_snap}"
                        }}
                    }}' AS JSONB
                ), 
                '{aggregator_name}', 
                TRUE, 
                '{hash_password}', 
                'aggregator', 
                TRUE, 
                'v3'
            );
            """

            #print(f"aggregatorId: {aggregator_id}")
            #print(f"aggregatorName: {aggregator_name}")
            #print(f"clearPassword: {clear_password}")
            #print(f"token: {encrypted_password}")
            #print(f"token_hash: {hash_password}")
            #print(f"x-callback-token: {x_callback_token}")
            #print(f"QUERY INSERT: \n{query}")

            output_generator = (
                f"aggregatorId: {aggregator_id}\n"
                f"aggregatorName: {aggregator_name}\n"
                f"clearPassword: {clear_password}\n"
                f"token: {encrypted_password}\n"
                f"token_hash: {hash_password}\n"
                f"x-callback-token: {x_callback_token}\n"
                f"QUERY INSERT: {query}"
            )

            return output_generator


# Penggunaan
'''
if __name__ == "__main__":
    ids = 'testaggregator'
    names = 'testaggregator'
    helper_toko = OAuth2GenerateTokoNetzmeRequestHelper()
    output_toko = helper_toko.generate_toko_netzme_aggregator_user_snap(id=ids, name=names)
    print(output_toko)
    helper = OAuth2GenerateNetzmeRequestHelper()
    output = helper.generate_netzme_aggregator_user_snap(id=ids, name=names)
    print(output_toko)
'''

