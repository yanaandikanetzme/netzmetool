import base64
import datetime
import math
import random
import string

TIME_DIFF_LIMIT = 300

def get_time():
    now = datetime.datetime.now()
    time = str(int(now.timestamp()))
    return time[:10]

def hash_data(json_data, cid, secret):
    sb = get_time()
    strrevtime = sb[::-1]
    hash_value = double_encrypt(strrevtime + "." + json_data, cid, secret)
    return hash_value

def parse_data(hash_value, cid, secret):
    parsed_string = double_decrypt(hash_value, cid, secret)
    arr = parsed_string.split(".", 1)
    if len(arr) == 2:
        strrevtime = arr[0][::-1]
        _time = int(strrevtime)
        if ts_diff(_time):
            return arr[1]
    return None

def ts_diff(ts):
    return abs(ts - int(get_time())) <= TIME_DIFF_LIMIT

def double_encrypt(string, cid, secret):
    result = encrypt(string.encode(), cid)
    result = encrypt(result, secret)
    base64_encoded = base64.b64encode(result).decode()
    base64_encoded = base64_encoded.rstrip("=").replace("+", "-").replace("/", "_")
    return base64_encoded

def encrypt(str_bytes, key):
    result = bytearray(len(str_bytes))
    for i, char in enumerate(str_bytes):
        keychr = ord(key[(i + len(key) - 1) % len(key)])
        result[i] = (char + keychr) % 128
    return bytes(result)

def double_decrypt(string, cid, secret):
    string = string.replace("-", "+").replace("_", "/")
    padding = b"=" * (4 - len(string) % 4)
    string = (string + padding.decode()).encode()
    result = base64.b64decode(string)
    result = decrypt(result, cid)
    result = decrypt(result, secret)
    return result.decode()

def decrypt(str_bytes, key):
    result = bytearray(len(str_bytes))
    for i, char in enumerate(str_bytes):
        keychr = ord(key[(i + len(key) - 1) % len(key)])
        result[i] = (char - keychr + 128) % 128
    return bytes(result)


bni_client_id = '368'
bni_secret_key = 'e9731d356964eabe8396bf43166e77c2'



rawst = '{"trx_id":"20240520143227239EA8iFeLbM7Ygt","virtual_account":"9883689614810873","customer_name":"NETZME-DONA","payment_amount":50000,"cumulative_payment_amount":50000,"payment_ntb":"975920","datetime_payment":"2024-05-20 08:35:13","datetime_payment_iso8601":"2024-05-20T08:35:13+07:00"}'
bni_encrypt = hash_data(rawst, bni_client_id, bni_secret_key)

hashed_1 = 'IkkgIh0fUhciHxpnDgwJEndXTw4mPEsaHRgcI0odIEobTx4kHRdTMCkkWi9PaXZlVERQZQtEQF1SW11hflZMfEh-YF9XXTkjDyInJhpRUU5RIRonH0VUIxkJGgt-ZF0NWQVUYUVVfVNQECYOOl1rdGUzGDA7aFoMFwZcTxFaVARcfE1aWlkIXwomJhkaTUREP05eXl4Ef1tSX05LDUtmCEoJZUlKVgZeW10RKBxLSUVLHAhfTw4JUVRbTVcPUQxTDFEmJB8ZTAgXEFBNYH0LAwVTSlxNEwZPWVgOKDofH0gcShwiGBZKCxgkKxwfV0VLPxcLVUoMA1tSVk5LDUtmCEoJZUlSXAYhIxkgECE9S0VNJBMfI0JOHDoXJiNOJCRKHUMfJiAXTAho'
hashed_data = 'GkkjKBwfUhciHxpnDgwJEndXTw4mPEsaHRgcI0odIEobTx4kHRdTMCkkWi9PaXZlVERQZQtEQF1SW11hflZMfEh-YF9XXTkjDyEiJB9LUUpSIBYfHkZTIhkJGgt-ZF0NWQVUYUVVfVNQECYOQEVlX2xIODEMXW43NCdBO2EPGzhYfmVaUFIOSklZYF5YETZSTiAZIRlISglMXlZhCUthBFsAUFpKYgROW11OT1QKDgMPEiAkHkVMHBIJXkoUXE8HXnddY0gJVggkJSElHk45RjpSTGBRDgJXUENcTxFaVARcPyYPHRRMHxUcJhYcVTRIVSUcJiNJUQkVC01NEU9hBFIAUFpKYgROW11OV1oKUUtLIQgpEEdMHhoUHh5IISJtGlApIhshTRkWHiMmHEg5Fw'
bni_decrypt = double_decrypt(hashed_1, bni_client_id, bni_secret_key)
#print(bni_decrypt)


