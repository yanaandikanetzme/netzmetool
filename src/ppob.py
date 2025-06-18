import tkinter as tk
from tkinter import ttk
import json
import requests
from uuid import uuid4
from datetime import datetime, timedelta
import base64
import hashlib
import hmac
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa

class PPOB:
    # Constants
    '''
    CLIENT_ID = "purbastg"
    CLIENT_KEY = "PhE87h!<_M]_>6Uqsv1i7ivzWK385?MfnL2uE8j0OIp<u@V<tnVQRW(^mZo[Buas"
    CLIENT_KEY_PATTERN = "||-"
    PRIVATE_KEY = "MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCsQR/LmD4sCo9vdW9CpMwYyJp/9rJ3iFrpKBMm+cyUZX5Jd/OnfM7MLDJ28u9+c1T/XhDaV34YJe5T5IZ+RDWFAJBqAzqWiLfzH/Xr0sqDgJGTNiyqSOBtADEnRBSVykMmSEM5j0xGPWpiqdRcp/lPjQtI6VCqAIMP/5mBoncfcI/E8547Hc3SZHPSWazU6i0yRnQCG1aySQRqKhFgh20keYwBOlRS9ve5LS2ZhsNJzRUN0GChj/UWHQOgANT1aFvO209XRYfPjiy5iOiLHG6huBdcoUoRXpOTqezpMLYT5FkT03Ipf8pfbccPuVOGMRxPtS489CThMQ3Pk/RAX61dAgMBAAECggEAEJTzqhuIP0tu87RS1xAFLmI/7o9Bg9yQ9SlB8A++SrobIO3BUKoPlZEFn0oTQFF66QWq9VHUgMpEpI0hs02pTJnkIl3C3z3fCLJWxUeqmLkg370ofztPu2ki0jGtZ56rvdIurSpRwIs7Tq8kPcfVFKbdDhJDt8cf1sOXXpF/X9EY3mLbbmZwmxuZhqOl+9D3PCT8anTzks9H7h0jMvQYUEp5/rRwiv6hnUZsYiQaz4pwnkRhtzPZbebW/XQyQAuer+RKeWsLP70ybBun0j4DEoOJh6IPo/9YHARtkNoeg+JFj/9ZLJPkmrAy7KaLpWivkAbQXIKji9DHjK3niJ92UwKBgQDVjHtC7Ri0E8QyW2ClwjDRPXTxM8+UX40YiNbTkvBhao/Jeq8/K9JR6EbR12si6ZeGHXJOQ1rOPyzxoTk3U+DKsK48F04ZxYhBOZE/+eSF0iEwIu37jLJygQ0MFTFYPah2QucTAstC/GXcZ4CqlTIiiDwiZEtsdgxYhrXWaLIuhwKBgQDOfysOYPD3g9/LpLzaKVW3wLv7W9SpTZD3cv2i2in+u3vgYjVUyea8GN7FStRMjJrcmMzSytbQ5FTE4NiMfY/6NS2N1ZjlhDSsO62etgCb7ZJ6e59bt55jog+17rsepKm545YI8/PwK2ZRG/U1C67QoZdsaKujxCNY9TDcLDA5+wKBgFB+TmvwsPIXzUlp9ikk5H/KWY0diW4VAjswQUGozmD56M76Jpp6KyHimuc3+tNDF3FfIhnr+4todslxiv6W6FGefV57Ll46fdyQFXb2+7ORfB8H24qJAy50BHX8ewgW3awOFcmtsO5D8yU8AlzKNgacMYaJJYDxkj/AL0RtXFR7AoGAGzn3MlkjzG7N1irtX5Jto+G8p2KvQndgss+tk4hSWyzbI3WvdHN+gbSBwt+f6Evtq0JWV0C5XCeO6bp/st5nWmUikX3lP/XTgBYKSU/T+rszQgUEuPIX5ykaCzHj6CFr43+Xa6zGsBb40Z7vEMRuk0GLFpcicmBNDNCfVZhZ73sCgYEAyS2JRw9vOyzAIxSqlUIlSBRaK/DUZ26P3WQgGYCTZRisTSuLE+B9hN1aRQOg1gEbM3ut/AzkDKY8PJTjP7yEydz4gHo7k7PBOY3feExzWevI6NwH0zooSziy+DWMe6XcE17NJMvHHyIY8H+llpQ5VT/2MpljTNx10W8jWYDWTHk="
    REQUEST_ID = "ed3f6763-b1bd-40e3-aecb-ddaa2c3a9776"
    REQUEST_TIME = 1865907223554
    MERCHANT_ID = "M_TB1NMLig"
    
    def __init__(self):
        self.bodyreq = '{"type":"DISBURSEMENT_ACCOUNT_INQUIRY","body":{"merchantId":"M_TB1NMLig","partner_trx_id":"makanbakso1313","account_number":"5465327020","bank_code":"014"}}'
        self.path_url = '/public/api/disbursement/v1/account-inquiry'
    '''

    @staticmethod
    def compute_hmac256(hex_output, secret, data):
        key = secret.encode('utf-8')
        message = data.encode('utf-8')
        h = hmac.new(key, message, hashlib.sha256)
        if hex_output:
            return h.hexdigest()
        return base64.b64encode(h.digest()).decode('utf-8')

    @staticmethod
    def generate_signature_token(private_key_str, data):
        private_key_bytes = base64.b64decode(private_key_str)
        private_key = serialization.load_der_private_key(private_key_bytes, password=None)
        
        if isinstance(data, dict):
            message = json.dumps(data)
        else:
            message = data
        message = message.encode('utf-8')
        
        signature = private_key.sign(
            message,
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        return base64.b64encode(signature).decode('utf-8')

    @staticmethod
    def generate_signature_trx(client_id, client_key_pattern, client_key, path_url, expired_at, bodyreq=None):
        token_model = {
            "userId": client_id,
            "expiredTs": expired_at,
            "roles": ["ppob.game_topup_in_game"]
        }
        json_token_model = json.dumps(token_model, separators=(',', ':'))
        signature = PPOB.compute_hmac256(True, f"{client_id}{client_key_pattern}{client_key}", json_token_model)
        # Jika bodyreq None, gunakan string kosong
        minify_json_body = json.dumps(json.loads(bodyreq), separators=(',', ':')) if bodyreq else ""
        key = f"{client_id}{client_key_pattern}{client_key}{path_url}{client_key_pattern}{signature}".encode()
        h = hmac.new(key, minify_json_body.encode(), hashlib.sha256)
        signature_transaction = h.hexdigest()
        return signature_transaction

    def generate_token_ppob(client_id, client_key_pattern, client_key):
        expired_at = int((datetime.now() + timedelta(hours=1)).timestamp() * 1000)
        token_model = {
            "userId": client_id,
            "expiredTs": expired_at,
            "roles": ["ppob.game_topup_in_game"]
        }
        json_token_model = json.dumps(token_model, separators=(',', ':'))

        signature = PPOB.compute_hmac256(True, f"{client_id}{client_key_pattern}{client_key}", json_token_model)
        
        user_signature_response = {
            "signature": signature,
            "tokenPpobUserResponse": token_model
        }
        json_user_signature_response = json.dumps(user_signature_response)
        token_response = {
            "expiredToken": expired_at,
            "token": base64.b64encode(json_user_signature_response.encode()).decode()
        }
        return token_response

'''
if __name__ == "__main__":
    ppob = PPOB()
    klien = "purbastg"
    CLIENT_KEY_PATTERNs = "||-"
    CLIENT_KEYs = "PhE87h!<_M]_>6Uqsv1i7ivzWK385?MfnL2uE8j0OIp<u@V<tnVQRW(^mZo[Buas"
    path_url = '/public/api/disbursement/v1/account-inquiry'
    bodyreq = '{"type":"DISBURSEMENT_ACCOUNT_INQUIRY","body":{"merchantId":"M_TB1NMLig","partner_trx_id":"makanbakso1313","account_number":"5465327020","bank_code":"014"}}'
    exp = 1729856792651
    
    # Call the static method correctly
    signature = PPOB.generate_signature_trx(
        client_id=klien,
        client_key_pattern=CLIENT_KEY_PATTERNs,
        client_key=CLIENT_KEYs,
        path_url=path_url,
        bodyreq=bodyreq,
        expired_at=exp
    )
    print(signature)
'''
