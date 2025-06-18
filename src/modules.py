#lokasi file src/modules.py
import time
import random
import logging
import math
from datetime import datetime, date, timedelta, timezone
import hashlib
import uuid
import json
import requests
import re
import psycopg2
import psycopg2.extras
import hmac
import base64
import phonenumbers
import string
import rsa
import ast
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.padding import PKCS7
import os
import shutil
import pyasn1
from json.decoder import JSONDecodeError
import numpy
import cv2
import time
from functools import wraps

class Modules():
    def __init__(self, parent):
        super().__init__(parent)

    def get_list_dictionary_config():
        with open('config/config_aggregator.json', 'r') as file:
            data = json.load(file)
        outer_dictionary = data[0]
        list_of_dictionaries_merchant = outer_dictionary['Merchant']
        list_of_dictionaries_netzme = outer_dictionary['Netzme']
        return [list_of_dictionaries_merchant, list_of_dictionaries_netzme]
    
    def hapus_pycache():
        path_proyek = os.getcwd()
        for root, dirs, files in os.walk(path_proyek):
            for directory in dirs:
                if directory == '__pycache__':
                    pycache_path = os.path.join(root, directory)
                    shutil.rmtree(pycache_path)

    def AES128Encrypt(plain_text, encryption_key=None):
        try:
            if encryption_key == None:
                encryption_key = './n37tMe%^4geNt*'
        
            backend = default_backend()
            cipher = Cipher(algorithms.AES(encryption_key.encode('UTF-8')), modes.CBC(encryption_key.encode('utf-8')), backend=backend)
            encryptor = cipher.encryptor()
            padder = PKCS7(algorithms.AES.block_size).padder()
            padded_plaintext = padder.update(plain_text.encode("UTF8")) + padder.finalize()
            ct_bytes = encryptor.update(padded_plaintext) + encryptor.finalize()
            encrypted_text = base64.b64encode(ct_bytes).decode()
        except Exception as ex:
            print("Encrypt Exception : {}".format(ex))
        return encrypted_text

    def AES128Decrypt(encrypted_text, encryption_key=None):
        try:
            if encryption_key == None:
                encryption_key = './n37tMe%^4geNt*'

            backend = default_backend()
            cipher = Cipher(algorithms.AES(encryption_key.encode('utf-8')), modes.CBC(encryption_key.encode('utf-8')), backend=backend)
            decryptor = cipher.decryptor()
            unpadder = PKCS7(algorithms.AES.block_size).unpadder()
            decoded_encrypted_text = base64.b64decode(encrypted_text.encode('utf-8'))
            decrypted_bytes = decryptor.update(decoded_encrypted_text) + decryptor.finalize()
            decrypted_text = unpadder.update(decrypted_bytes).decode('utf-8')
        except Exception as ex:
            print(f"decrypt Exception : {ex}")
        return decrypted_text
    
    def base64Encode(string):
        string_bytes = string.encode("utf-8")
        output = base64.b64encode(string_bytes)
        return output.decode('utf-8')

    def base64Decode(string):
        output = base64.b64decode(string)
        return output.decode('utf-8')

    def HashMD5(string):
        results = hashlib.md5(string.encode('utf-8')).hexdigest()
        return str(results)

    def HashSHA1(string):
        results = hashlib.sha1(string.encode('utf-8')).hexdigest()
        return str(results)

    def HashSHA256(string, key=None):
        if key is None:
            output = hashlib.sha256(string.encode('utf-8')).hexdigest()
        else:
            if not isinstance(key, bytes):
                keybit = str(key).encode('utf-8')
            else:
                keybit = key
            if not isinstance(string, bytes):
                msgbit = str(string).encode('utf-8')
            else:
                msgbit = string
            output = hmac.new(keybit, msgbit, hashlib.sha256).hexdigest()
        return output

    def HashSHA512(string, key=None):
        if key is None:
            output = hashlib.sha512(string.encode('utf-8')).hexdigest()
        else:
            if not isinstance(key, bytes):
                keybit = str(key).encode('utf-8')
            else:
                keybit = key
            if not isinstance(string, bytes):
                msgbit = str(string).encode('utf-8')
            else:
                msgbit = string
            output = hmac.new(keybit, msgbit, hashlib.sha512).hexdigest()
        return output

    def Get_Signature_Top_Up(user, password, nomorHP):
        data = (user + password + str(nomorHP) + '2').encode()
        md5_hash = hashlib.md5(data).hexdigest()
        return hashlib.sha1(md5_hash.encode()).hexdigest()

    def ValidatePhoneNumber(input):
        try:
            # Try to parse the number
            my_number = phonenumbers.parse(input, "ID")  # "ID" is ISO Alpha-2 code for Indonesia
            
            # Check if the number is valid
            if not phonenumbers.is_valid_number(my_number):
                return None
            
            # Format the number
            international_f = phonenumbers.format_number(my_number, phonenumbers.PhoneNumberFormat.E164)
            return international_f
        except phonenumbers.NumberParseException:
            # If parsing fails, return None
            return None

    def checkvalidNumber(phone_number):
        T = {"-": 0, "+": 0, "_": 0}
        for i in str(phone_number):
            if i in T:
                if (i == "_" or i == "-") and (T["-"] >= 1 or T['_'] >= 1):
                    return str(phone_number)
                elif i == "+" and T[i] >= 1:
                    return str(phone_number)
                else:
                    T[i] += 1
            elif not i.isdigit():
                return str(phone_number)
        
        convertPhoneCode = Modules.ValidatePhoneNumber(phone_number)
        return convertPhoneCode if convertPhoneCode is not None else str(phone_number)

    # Example usage:
    # result = checkvalidNumber("+62123456789")
    # if result:
    #     print(f"Valid phone number: {result}")
    # else:
    #     print("Invalid phone number")

    def generateUUID():
        return str(uuid.uuid4())

    def RandomDigit(number):
        total = int('9' * number)
        output = str(random.randint(0,total)).rjust(number, "0")
        return output
    
    def DateNowSec():
        """
        Mengembalikan tanggal dan waktu saat ini dalam format "YYYYMMDDHHMMSS".
        
        Contoh output return:
        # Misalkan tanggal dan waktu saat ini adalah 2024-04-19 10:30:45
        return "20240419103045"
        """
        dtn = datetime.today().strftime("%Y%m%d%H%M%S")
        return dtn

    def get_current_date_topup():
        """
        Mengembalikan tanggal dan waktu saat ini dalam format "YYYY-MM-DD HH:MM:SS".
        
        Contoh output return:
        # Misalkan tanggal dan waktu saat ini adalah 2024-04-19 10:30:00
        return "2024-04-19 10:30:00"
        """
        now = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
        return str(now)

    def getXtimestamp():
        """
        Mengembalikan timestamp saat ini dalam format ISO 8601 dengan zona waktu "+07:00".
        
        Contoh output return:
        # Misalkan timestamp saat ini adalah 2024-04-19T10:30:00+07:00
        return "2024-04-19T10:30:00+07:00"
        """
        now = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')+'+07:00'
        return str(now)

    def current_milli_time():
        """
        Mengembalikan waktu saat ini dalam milidetik sejak epoch.
        
        Contoh output return:
        # Misalkan waktu saat ini adalah 1621048954236 milidetik setelah epoch
        return "1621048954236"
        """
        return str(round(time.time() * 1000))
    
    def generate_random_string(length):
        """
        Generate a random string of specified length.
        Args:
            length (int): The length of the random string to generate.
        Returns:
            str: A random string of the specified length.
        """
        # Kombinasi huruf dan angka
        characters = string.ascii_letters + string.digits
        # Membuat string acak
        random_string = ''.join(random.choice(characters) for _ in range(length))
        return random_string

    def generate_custom_string():
        now = datetime.datetime.now()
        date_time_str = now.strftime("%Y%m%d%H%M%S%f")[:-3]  # Menghilangkan 3 digit terakhir dari microseconds
        # Menghasilkan 13 karakter acak
        random_str = ''.join(random.choices(string.ascii_letters + string.digits, k=13))
        # Menggabungkan semuanya
        custom_string = date_time_str + random_str
        # contoh output 20240528132819410qmVA3Zwe2Hac1
        return custom_string

    def generate_timestamp_expired():
        # Contoh output:
        # Output: "2022-04-20T10:15:30.123Z"
        now = datetime.now()
        later = now + timedelta(hours=12)
        return later.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"

    def replaceDateToTZ(datetime_str):
        # Contoh output:
        # Input: "2022-04-19 10:30:00.000000+0700"
        # Output: "2022-04-19T10:30:00.000Z"
        dt = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S.%f%z")
        return dt.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"

    def replaceDateToTsDispute(ts):
        # Contoh output:
        # Input: "2022-04-19T10:30:00.000+07:00"
        # Output: "2022-04-19 11:30:00"
        dt = datetime.fromisoformat(ts)
        wib = dt.astimezone(timezone(timedelta(hours=7)))
        return wib.strftime("%Y-%m-%d %H:%M:%S")

    def replaceDateToTsDisputeSave(ts):
        # Contoh output:
        # Input: "2022-04-19T10:30:00.000+07:00"
        # Output: "19/04/22    03:30:00"
        dt = datetime.fromisoformat(ts)
        wib = dt.astimezone(timezone(timedelta(hours=7)))
        return wib.strftime("%d/%m/%y    %H:%M:%S")

    def generate_date(base_date=None, days=0):
        """
        Menghasilkan tanggal dalam format YYYYMMDD.

        Args:
            base_date (str): Tanggal dasar dalam berbagai format (misalnya, YYYYMMDD, YYYY-MM-DD, DD-MM-YYYY, YYYYDDMM, YYYYDDMMHHMMSS, dll.). 
                            Default adalah None, yang berarti tanggal sekarang.
            days (int): Jumlah hari yang akan ditambahkan ke tanggal dasar. Default adalah 0.

        Returns:
            str: Tanggal dalam format YYYYMMDD.
        """
        if base_date:
            date_formats = [
                '%Y%m%d',         # Format YYYYMMDD
                '%Y-%m-%d',       # Format YYYY-MM-DD
                '%d-%m-%Y',       # Format DD-MM-YYYY
                '%d/%m/%Y',       # Format DD/MM/YYYY
                '%Y/%m/%d',       # Format YYYY/MM/DD
                '%d %b %Y',       # Format 01 Jan 2024
                '%d %B %Y',       # Format 01 January 2024
                '%Y%d%m',         # Format YYYYDDMM
                '%Y%d%m%H%M%S',   # Format YYYYDDMMHHMMSS
            ]
            
            for date_format in date_formats:
                try:
                    date = datetime.strptime(base_date, date_format)
                    break
                except ValueError:
                    continue
            else:
                raise ValueError("base_date harus dalam format yang valid.")
        else:
            # Mengambil tanggal sekarang jika base_date tidak diberikan
            date = datetime.now()

        new_date = date + timedelta(days=days)
        # Mengembalikan tanggal dalam format YYYYMMDD
        return new_date.strftime('%Y%m%d')

    def POSThttp(url, bodyreq):
        try:
            if isinstance(bodyreq, str):
                bodyreq = json.loads(bodyreq)
            jsonString = json.dumps(bodyreq, indent=4)
            post_response = requests.post(url, json=bodyreq)
            post_response_json = post_response.json()
            return str(post_response_json)
        except (IndexError, ValueError) as e:
            return f"{e}"
        except requests.exceptions.HTTPError as error:
            return f"{error}"
        except requests.exceptions.ConnectionError as b:
            return f"{b}"

    def POSThttpHeadersWithoutHeaders(url, bodyreq):
        try:
            if isinstance(bodyreq, str):
                bodyreq = json.loads(bodyreq)
            jsonString = json.dumps(bodyreq, indent=4)
            post_response = requests.post(url, json=bodyreq)
            if post_response.status_code == 200:
                aaa = post_response.json()
                return aaa
            else:
                a = str(post_response.status_code) + ' ' + str(post_response.reason)
                return a
        except (IndexError, ValueError) as e:
            return f"{e}"
        except requests.exceptions.HTTPError as error:
            return f"{error}"
        except requests.exceptions.ConnectionError as b:
            return f"{b}"
        
    def POSThttpHeaders(url, headerreq, bodyreq):
        try:
            # Konversi headerreq ke dictionary jika berupa string
            if isinstance(headerreq, str):
                headerreq = json.loads(headerreq)

            # Konversi bodyreq ke dictionary jika berupa string
            if isinstance(bodyreq, str):
                bodyreq = json.loads(bodyreq)

            jsonString = json.dumps(bodyreq, indent=4)
            post_response = requests.post(url, json=bodyreq, headers=headerreq)
            if post_response.status_code == 200:
                aaa = post_response.json()
                return aaa
            else:
                a = str(post_response.status_code) + ' ' + str(post_response.reason)
                return a
        except (IndexError, ValueError) as e:
            return f"{e}"
        except requests.exceptions.HTTPError as error:
            return f"{error}"
        except requests.exceptions.ConnectionError as b:
            return f"{b}"

    def POSThttpNotJSONHeaders(url, headerreq, bodyreq):
        try:
            if isinstance(headerreq, str):
                headerreq = json.loads(headerreq)
            post_response = requests.post(url, data=bodyreq, headers=headerreq)
            if post_response.status_code == 200:
                return post_response
            else:
                a = str(post_response.status_code) + ' ' + str(post_response.reason)
                return a
        except (IndexError, ValueError) as e:
            return f"{e}"
        except requests.exceptions.HTTPError as error:
            return f"{error}"
        except requests.exceptions.ConnectionError as b:
            return f"{b}"

    def POSThttpHeadersQRIS(url, bodyreq, key):
        try:
            if isinstance(bodyreq, str):
                bodyreq = json.loads(bodyreq)
            jsonString = json.dumps(bodyreq)
            hash = Modules.HashSHA256(str(jsonString), key).upper()
            headerreq = {"mac": hash}
            post_response = requests.post(url, json=bodyreq, headers=headerreq)
            if post_response.status_code == 200:
                post_response_json = post_response.json()
                return post_response_json
            else:
                a = str(post_response.status_code) + ' ' + str(post_response.reason)
                return a
        except (IndexError, ValueError) as e:
            return f"{e}"
        except requests.exceptions.HTTPError as error:
            return f"{error}"
        except requests.exceptions.ConnectionError as b:
            return f"{b}"
        
    def POSThttpHeadersQRISAJ(url, bodyreq, key):
        try:
            if isinstance(bodyreq, str):
                bodyreq = json.loads(bodyreq)
            jsonString = json.dumps(bodyreq)
            hash = Modules.HashSHA256(str(jsonString), key).upper()

            headerreq = {"mac": hash, "Authorization": "Basic a2FyZTpkZGUyOGM3ZWRiOWQ4MDQ2OTcyYzVjMzI3N2Q5OTlhMg=="}
            post_response = requests.post(url, json=bodyreq, headers=headerreq)
            if post_response.status_code == 200:
                post_response_json = post_response.json()
                return post_response_json
            else:
                a = str(post_response.status_code) + ' ' + str(post_response.reason)
                return a
        except (IndexError, ValueError) as e:
            return f"{e}"
        except requests.exceptions.HTTPError as error:
            return f"{error}"
        except requests.exceptions.ConnectionError as b:
            return f"{b}"

    def connect_db(connection_key):
        with open('config/cred_database.json', 'r') as f:
            credentials = json.load(f)

        connection_info = credentials[connection_key][0]

        conn = psycopg2.connect(
            host=connection_info['host'],
            database=connection_info['database'],
            user=connection_info['user'],
            password=connection_info['password']
        )
        return conn

    def retry_connection(max_attempts=3, delay=60):
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                attempts = 0
                while attempts < max_attempts:
                    try:
                        return func(*args, **kwargs)
                    except psycopg2.OperationalError as e:
                        attempts += 1
                        if attempts == max_attempts:
                            raise
                        print(f"Connection failed. Retrying in {delay} seconds... (Attempt {attempts}/{max_attempts})")
                        time.sleep(delay)
                return None
            return wrapper
        return decorator

    @retry_connection(max_attempts=3, delay=60)

    def execute_query(conn, query, is_dml=False):
        try:
            cur = conn.cursor(cursor_factory = psycopg2.extras.DictCursor)
            cur.execute(query)
            if is_dml:
                rows_affected = cur.rowcount
                conn.commit()
                cur.close()
                conn.close()
                return f'Success execute {rows_affected} row'
            else:
                result = cur.fetchall()
                cur.close()
                conn.close()
                return result
        except (Exception, psycopg2.DatabaseError) as error:
            return str(error)

    def ConnectDMLNetzreg(query):
        conn = Modules.connect_db('NetzmeNetzreg')
        return Modules.execute_query(conn, query, is_dml=True)

    def ConnectDMLMerchant(query):
        conn = Modules.connect_db('Merchant')
        return Modules.execute_query(conn, query, is_dml=True)

    def ConnectDBNetzreg(query):
        conn = Modules.connect_db('NetzmeNetzreg')
        return Modules.execute_query(conn, query)

    def ConnectDBMerchant(query):
        conn = Modules.connect_db('Merchant')
        return Modules.execute_query(conn, query)

    def ConnectDBLenjer(query):
        conn = Modules.connect_db('NetzmeLenjer')
        return Modules.execute_query(conn, query)
            
    def getAllAggregatorMerchant():
        return [agget['aggregatorId'] for agget in Modules.get_list_dictionary_config()[0]]

    def get_clear_pass_and_token(list_of_dictionaries, key_agg):
        for dictionary in list_of_dictionaries:
            if dictionary["aggregatorId"] == key_agg and "clearPassword" in dictionary:
                return [dictionary["clearPassword"], dictionary["aggregatorId"], dictionary["aggregatorToken"], dictionary["privateKey"], dictionary["clientSecret"]]

    def searchclearPassByaggregatorMerchant(key_agg):
        return Modules.get_clear_pass_and_token(Modules.get_list_dictionary_config()[0], key_agg)

    def searchclearPassByaggregatorNetzme(key_agg):
        return Modules.get_clear_pass_and_token(Modules.get_list_dictionary_config()[1], key_agg)

    def getAllAggregatorNetzme():
        return [agget['aggregatorId'] for agget in Modules.get_list_dictionary_config()[1]]

    def JsonRemoveWhitespace(json_string):
        try:
            json_object = json.loads(json_string.replace("\'", '"').replace("False", "false"))
            return json.dumps(json_object, separators=(',', ':'))
        except (ValueError, JSONDecodeError):
            return json_string

    def is_json(myjson):
        try:
            json.loads(myjson)
        except (ValueError, JSONDecodeError):
            return False
        return True

    def generate_curl_command(url, headers=None, payload=None):
        curl_command = f"curl --location '{url}'"

        if headers:
            if isinstance(headers, str):
                headers = json.loads(headers)
            for key, value in headers.items():
                curl_command += f" \\\n--header '{key}: {value}'"

        if payload:
            try:
                payload = json.loads(payload)
                payload_data = json.dumps(payload, indent=4)
            except ValueError:
                payload_data = payload
            curl_command += f" \\\n--data-raw '{payload_data}'"
        return curl_command

    def random_string(total_count):  
        letter_count = round(total_count/2)
        digit_count = total_count - letter_count
        str1 = ''.join((random.choice(string.ascii_letters) for x in range(letter_count)))  
        str1 += ''.join((random.choice(string.digits) for x in range(digit_count)))  
        sam_list = list(str1) # it converts the string to list.  
        random.shuffle(sam_list) # It uses a random.shuffle() function to shuffle the string.  
        final_string = ''.join(sam_list)
        return final_string

    def SHA256WithRSA(StringToSign, PrivateKey):
        try:
            pem_prefix = '-----BEGIN RSA PRIVATE KEY-----\n'
            pem_suffix = '\n-----END RSA PRIVATE KEY-----'
            PrivateKey = '{}{}{}'.format(pem_prefix, PrivateKey, pem_suffix)

            key = rsa.PrivateKey.load_pkcs1(PrivateKey.encode('utf-8'))
            signature = rsa.sign(StringToSign.encode('utf-8'), key, 'SHA-256')
            result = base64.b64encode(signature).decode('utf-8')
            return (result)
        except (ValueError, pyasn1.error.EndOfStreamError) as e:
            return e

    def LeftAdjust(string, length):
        if len(string) < length:
            return string.ljust(length)
        else:
            return string[:length]

    def RightAdjust(string, length):
        if len(string) < length:
            return string.rjust(length)
        else:
            return string[:length]

    def round_up(number: str) -> int:
        if isinstance(number, str):
            number = float(number)
        return int(math.ceil(number))

    def make_http_request(url, body_request=None, headers=None):
        """
        Membuat HTTP request ke URL yang diberikan.

        Args:
            url (str): URL yang akan diakses.
            body_request (dict/str, optional): Data yang akan dikirim dalam bentuk JSON atau string. Jika None atau string kosong, maka akan menggunakan metode GET.
            headers (dict/str, optional): Header yang akan dikirim dalam request dalam bentuk dictionary atau string.

        Returns:
            list: List yang berisi http_status_code dan response_message tanpa escape karakter.
        """
        if body_request is None or body_request == "":
            method = 'GET'
            body_request = None
        else:
            method = 'POST'

        try:
            # Mengonversi headers ke bentuk dictionary jika diberikan dalam bentuk string
            if isinstance(headers, str):
                try:
                    headers = json.loads(headers)
                except json.JSONDecodeError:
                    headers = ast.literal_eval(headers)
            # Mengonversi body_request ke bentuk dictionary jika diberikan dalam bentuk string dan tidak kosong
            if isinstance(body_request, str) and body_request:
                body_request = json.loads(body_request)
            response = requests.request(method, url, json=body_request, headers=headers)
            response.raise_for_status()
            http_status_code = response.status_code

            # Memeriksa apakah respons berformat JSON
            content_type = response.headers.get('Content-Type', '').lower()
            if 'application/json' in content_type:
                response_data = json.loads(response.text)  # Mengonversi respons menjadi objek Python
                response_message = json.dumps(Modules.fix_escaped_urls(response_data))  # Memperbaiki URL yang di-escape dan mengonversi kembali menjadi string
            else:
                response_message = response.text

            return [http_status_code, response_message]
        except (json.JSONDecodeError, ValueError, requests.exceptions.RequestException) as e:
            try:
                response_data = json.loads(e.response.text)  # Mengonversi respons menjadi objek Python
                response_message = json.dumps(Modules.fix_escaped_urls(response_data))  # Memperbaiki URL yang di-escape dan mengonversi kembali menjadi string
            except (AttributeError, json.JSONDecodeError):
                response_message = str(e)
            return [e, response_message]

    def fix_escaped_urls(data):
            """
            Memperbaiki URL yang di-escape dalam objek Python.

            Args:
                data (dict/list): Objek Python yang mengandung URL yang di-escape.

            Returns:
                dict/list: Objek Python dengan URL yang sudah diperbaiki.
            """
            if isinstance(data, dict):
                new_data = {}
                for key, value in data.items():
                    if key == 'paymentUrl':
                        new_data[key] = value.replace(r'\\/', '/')
                    else:
                        new_data[key] = Modules.fix_escaped_urls(value)
                return new_data
            elif isinstance(data, list):
                return [Modules.fix_escaped_urls(item) for item in data]
            else:
                return data

    def get_value_from_json(json_data, key):
        """
        Mengambil nilai dari parameter tertentu dalam JSON.
        
        Args:
            json_data (str/dict): Data JSON dalam bentuk string (dengan tanda kutip ganda atau tunggal) atau dictionary.
            key (str): Kunci untuk mengakses nilai yang diinginkan, dapat berupa kunci yang di-nest dengan tanda titik (.)
            
        Returns:
            str/dict/list/int/float/bool/None: Nilai yang sesuai dengan kunci yang diberikan, atau None jika kunci tidak ditemukan.
        """
        try:
            # Mengonversi json_data ke bentuk dictionary
            if isinstance(json_data, str):
                if json_data.startswith("'"):
                    json_data = ast.literal_eval(json_data)
                else:
                    json_data = json.loads(json_data)
            
            # Memisahkan kunci yang di-nest
            keys = key.split(".")
            
            # Mengakses nilai secara rekursif menggunakan kunci yang di-nest
            value = json_data
            for k in keys:
                value = value.get(k)
                if value is None:
                    break
            
            return value
        except (json.JSONDecodeError, ValueError, AttributeError) as e:
            print(f"Error: {e}")
            return None

    def run_curl(curl_command):
        try:
            # Parse URL dari perintah cURL
            url_match = re.search(r"'([^']+)'", curl_command)
            url = url_match.group(1) if url_match else None

            # Parse headers dari perintah cURL
            headers = {}
            header_matches = re.findall(r"--header '([^']+)'", curl_command)
            for header in header_matches:
                key, value = header.split(': ', 1)
                headers[key] = re.sub(r'\{\{\$guid\}\}', Modules.generateUUID(), value)

            # Parse data/payload dari perintah cURL
            data_match = re.search(r"--data '(.+)'", curl_command, re.DOTALL)
            data = data_match.group(1) if data_match else None
            if data:
                data = re.sub(r'\{\{\$guid\}\}', Modules.generateUUID(), data)
                data = re.sub(r'\$\{\{guid\}\}', Modules.generateUUID(), data)

            # Parse method dari perintah cURL
            method_match = re.search(r"--request (\w+)", curl_command)
            method = method_match.group(1).upper() if method_match else "POST" if data else "GET"

            # Kirim permintaan HTTP
            if method == "POST":
                response = requests.post(url, headers=headers, data=data)
            else:
                response = requests.get(url, headers=headers)
            
            # Modifikasi respons untuk mengonversi URL
            if response.text:
                try:
                    json_response = response.json()
                    modified_response = Modules.fix_escaped_urls(json_response)
                except json.JSONDecodeError:
                    modified_response = response.text
            else:
                modified_response = "Response is empty"

            return [response.status_code, modified_response]

        except requests.exceptions.RequestException as e:
            return [e.response.status_code if e.response else 0, e.response.text if e.response else str(e)]
        except Exception as e:
            return [0, str(e)]
    
    def convert_date(date_str):
        # Mengubah string tanggal menjadi objek datetime
        date_obj = datetime.strptime(date_str, '%Y%m%d')
        # Mendapatkan tanggal hari ini
        today = datetime.now(timezone.utc).astimezone().date()
        # Membuat list dengan dua elemen
        result = []
        utc_offset = '07:00'
        # Memformat objek datetime ke format yang diinginkan
        formatted_date_start = date_obj.strftime("%Y-%m-%dT%H:%M:%S+") + utc_offset
        result.append(formatted_date_start)
        if date_obj.date() == today:
            # Jika tanggal sama dengan hari ini, gunakan waktu sekarang
            now = datetime.now(timezone.utc).astimezone()
            formatted_date_end = now.strftime("%Y-%m-%dT%H:%M:%S+") + utc_offset
        else:
            # Jika tanggal berbeda dengan hari ini, gunakan waktu 23:59:59
            formatted_date_end = date_obj.replace(hour=23, minute=59, second=59).strftime("%Y-%m-%dT%H:%M:%S+") + utc_offset
        result.append(formatted_date_end)
        return result
    
    def snap_formatted_dates():
        # Mendapatkan tanggal dan waktu saat ini
        now = datetime.now()

        # Mengatur jam, menit, dan detik menjadi 0 untuk waktu tengah malam
        midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)

        # Mendapatkan offset zona waktu saat ini
        offset = midnight.astimezone().utcoffset()
        offset_hours = offset.seconds // 3600
        offset_minutes = (offset.seconds // 60) % 60

        # Membuat string untuk offset zona waktu dengan tanda minus (-) jika offset kurang dari 0
        if offset_hours >= 0:
            utc_offset = "{:02d}:{:02d}".format(offset_hours, offset_minutes)
        else:
            utc_offset = "-{:02d}:{:02d}".format(abs(offset_hours), offset_minutes)

        # Format tanggal dan waktu sesuai dengan kebutuhan
        formatted_midnight = midnight.strftime("%Y-%m-%dT%H:%M:%S+") + utc_offset
        formatted_now = now.strftime("%Y-%m-%dT%H:%M:%S+") + utc_offset
        
        #['2024-05-04T00:00:00-07:00', '2024-05-04T11:38:54-07:00']
        return [formatted_midnight, formatted_now]

    def decode_base64_qr(base64_string):
        # Cek apakah input merupakan string base64 yang valid
        try:
            # Hapus metadata "data:image/png;base64,"
            base64_data = base64_string.split(',')[1]
        except IndexError:
            return "Input bukan merupakan string base64 yang valid"
        # Decode Base64 menjadi bytes
        try:
            img_bytes = base64.b64decode(base64_data)
        except (base64.Error, ValueError):
            return "Input bukan merupakan string base64 yang valid"
        # Membuat gambar NumPy dari bytes
        img_np = numpy.frombuffer(img_bytes, numpy.uint8)
        img = cv2.imdecode(img_np, cv2.IMREAD_UNCHANGED)
        # Mendekode QR Code menggunakan OpenCV
        detector = cv2.QRCodeDetector()
        data, _, _ = detector.detectAndDecode(img)
        if data:
            decoded_text = data
        else:
            decoded_text = "Input bukan merupakan QR Code yang valid"
        return decoded_text
