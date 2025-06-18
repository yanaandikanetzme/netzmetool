#lokasi file automation/src/base.py
import requests
import psycopg2
import logging
import os
import json
import subprocess
import decimal
import hashlib
import hmac
from src.jsonParser import jsonParser
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException

# Dapatkan path absolut untuk file log
log_file_path = os.path.join(os.getcwd(), 'automation/app.log')

# Konfigurasi logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s]: %(message)s',
    handlers=[
        logging.FileHandler(log_file_path),
        logging.StreamHandler()
    ]
)

def create_log_message(string):
    logging.info(f'{string}')

def validasi_data_list(lst, expected, show_logs=True):
    print(expected)
    if expected == "isi":
        if len(lst) != 0:
            if show_logs:
                logging.info(f"Passed, Ada data transaksi")
            return True
        else:
            logging.error(f"Failed, Data transaksi tidak di temukan !")
            raise ValueError('Failed, Data transaksi tidak di temukan !')
    else:
        if len(lst) == 0:
            if show_logs:
                logging.info(f"Passed, Tidak ada data transaksi")
            return True
        else:
            logging.error(f"Failed, Ditemukan data transaksi !")
            raise ValueError('Failed, Ditemukan data transaksi !')

def send_http_request(method, url, headers=None, response_params=None, body_request=None, show_logs=False):
    """
    Fungsi untuk mengirim permintaan HTTP dan mengambil nilai dari parameter tertentu pada respons.

    Args:
        method (str): Metode HTTP (POST atau GET)
        url (str): URL tujuan (termasuk parameter jika ada)
        headers (dict or str, optional): Header permintaan HTTP
        response_params (str or list, optional): Parameter yang ingin diambil nilainya dari respons
        body_request (dict or str, optional): Data yang akan dikirim dalam body request (untuk metode POST dengan JSON data)
        show_logs (bool, optional): Jika True, maka log akan ditampilkan. Jika False, maka log tidak akan ditampilkan (default adalah False)

    Returns:
        dict or list or str: Respons lengkap dari permintaan HTTP atau nilai dari parameter yang diminta
    """
    method = method.upper()

    # Handle headers
    if isinstance(headers, str):
        try:
            headers = json.loads(headers.replace("'", '"'))
        except json.JSONDecodeError:
            if show_logs:
                logging.error(f"Header tidak valid: {headers}")
            headers = {}
    elif headers is None:
        headers = {}

    # Log headers yang digunakan
    if headers and show_logs:
        logging.info(f"Headers yang digunakan: {headers}")

    # Hapus header 'Content-Type' jika ada
    headers.pop('Content-Type', None)

    # Handle body_request
    if isinstance(body_request, str):
        try:
            body_request = json.loads(body_request.replace("'", '"'))
        except json.JSONDecodeError:
            if show_logs:
                logging.error(f"Body request tidak valid: {body_request}")
            body_request = {}
    elif body_request is None:
        body_request = {}

    if method == 'POST':
        if show_logs:
            logging.info(f'Mengirim permintaan POST ke {url}')
        if headers:
            if body_request:
                if show_logs:
                    logging.info(f'Body Request: {body_request}')
                response = requests.post(url, json=body_request, headers=headers)
            else:
                response = requests.post(url, headers=headers)
        else:
            if body_request:
                if show_logs:
                    logging.info(f'Body Request: {body_request}')
                response = requests.post(url, json=body_request)
            else:
                response = requests.post(url)
    elif method == 'GET':
        if show_logs:
            logging.info(f'Mengirim permintaan GET ke {url}')
        if headers:
            response = requests.get(url, headers=headers)
        else:
            response = requests.get(url)
    else:
        raise ValueError('Metode HTTP tidak valid. Harus POST atau GET.')

    if show_logs:
        logging.info(f'Respons diterima: Status Code {response.status_code}')

    if response.headers.get('Content-Type', '').startswith('application/json'):
        response_data = response.json()
        if show_logs:
            logging.info(f'Respons JSON: {response_data}')

        if response_params:
            values = _extract_values_from_response(response_data, response_params)
            return values
        else:
            return response_data
    else:
        response_text = response.text
        if show_logs:
            logging.info(f'Respons Text: {response_text}')
        return response_text

def _extract_values_from_response(data, params, show_logs=False):
    """
    Helper function to extract values from a nested JSON response based on the provided parameters.

    Args:
        data (dict): The JSON response data.
        params (str or list): The parameter(s) to extract from the response.
        show_logs (bool, optional): Jika True, maka log akan ditampilkan. Jika False, maka log tidak akan ditampilkan (default adalah False)

    Returns:
        dict or list or str: The extracted value(s).
    """
    if isinstance(params, str):
        # Handle a single string parameter
        parts = params.split('.')
        current_data = data
        for part in parts:
            if current_data is None:
                if show_logs:
                    logging.error(f'Kunci parameter "{params}" tidak ditemukan dalam respons.')
                return None
            elif part in current_data:
                current_data = current_data[part]
            else:
                if show_logs:
                    logging.error(f'Kunci parameter "{params}" tidak ditemukan dalam respons.')
                return None
        if show_logs:
            logging.info(f'Nilai dari parameter "{params}": {current_data}')
        return current_data
    else:
        # Handle a list of parameters
        values = {}
        for param in params:
            parts = param.split('.')
            current_data = data
            for part in parts:
                if current_data is None:
                    if show_logs:
                        logging.error(f'Kunci parameter "{param}" tidak ditemukan dalam respons.')
                    break
                elif part in current_data:
                    current_data = current_data[part]
                else:
                    if show_logs:
                        logging.error(f'Kunci parameter "{param}" tidak ditemukan dalam respons.')
                    break
            if current_data is not None:
                values[param] = current_data
                if show_logs:
                    logging.info(f'Nilai dari parameter "{param}": {current_data}')
        return values

def connect_to_postgres(query, columns=None, connection_key='Merchant', show_logs=False):
    """
    Fungsi untuk melakukan koneksi ke database PostgreSQL dan menjalankan query SELECT.

    Args:
        query (str): Query SELECT yang akan dijalankan
        columns (list, optional): Daftar kolom yang ingin diambil nilainya
        connection_key (str, optional): Kunci untuk mengambil informasi koneksi dari file cred_database.json (default adalah 'Merchant')
        show_logs (bool, optional): Jika True, maka log akan ditampilkan. Jika False, maka log tidak akan ditampilkan (default adalah False)

    Returns:
        list: Daftar hasil query yang berisi nilai dari kolom yang diminta
    """
    conn = None  # Deklarasikan variabel conn di luar blok try

    try:
        # Baca informasi koneksi dari file cred_database.json
        with open('config/cred_database.json', 'r') as f:
            credentials = json.load(f)

        # Ambil informasi koneksi berdasarkan connection_key
        connection_info = credentials[connection_key][0]

        # Konfigurasi koneksi ke PostgreSQL
        conn = psycopg2.connect(
            host=connection_info['host'],
            database=connection_info['database'],
            user=connection_info['user'],
            password=connection_info['password']
        )
        cur = conn.cursor()

        if show_logs:
            logging.info(f"Menjalankan query: {query}")

        cur.execute(query)
        rows = cur.fetchall()

        if not rows:
            if show_logs:
                logging.info("Hasil query kosong")
            return []

        # Get the column names returned by the query
        column_names = [desc[0] for desc in cur.description]

        # If the columns argument is provided, extract the specified columns from the rows
        if columns:
            results = [dict(zip(column_names, row)) for row in rows]
            results = [row[col] for row in results for col in columns]
        else:
            # If the columns argument is not provided, return the rows as a list of values
            results = [value for row in rows for value in row]

        if show_logs:
            logging.info(f"Hasil query: {results}")
        return results

    except (Exception, psycopg2.Error) as error:
        if show_logs:
            logging.error(f"Terjadi error: {error}")
        return []

    finally:
        if conn:  # Periksa apakah conn tidak None
            cur.close()
            conn.close()
            if show_logs:
                logging.info("Koneksi PostgreSQL ditutup")
#lokasi file automation/src/base.py

def connect_to_postgres2(query, columns=None, connection_key='Merchant', show_logs=False):
    """
    Fungsi untuk melakukan koneksi ke database PostgreSQL dan menjalankan query SELECT.

    Args:
        query (str): Query SELECT yang akan dijalankan
        columns (list, optional): Daftar kolom yang ingin diambil nilainya
        connection_key (str, optional): Kunci untuk mengambil informasi koneksi dari file cred_database.json (default adalah 'Merchant')
        show_logs (bool, optional): Jika True, maka log akan ditampilkan. Jika False, maka log tidak akan ditampilkan (default adalah False)

    Returns:
        list: Daftar baris hasil query yang berisi nilai dari kolom yang diminta
    """
    conn = None

    try:
        with open('config/cred_database.json', 'r') as f:
            credentials = json.load(f)

        # Ambil informasi koneksi berdasarkan connection_key
        connection_info = credentials[connection_key][0]

        # Konfigurasi koneksi ke PostgreSQL
        conn = psycopg2.connect(
            host=connection_info['host'],
            database=connection_info['database'],
            user=connection_info['user'],
            password=connection_info['password']
        )
        cur = conn.cursor()

        if show_logs:
            logging.info(f"Menjalankan query: {query}")

        cur.execute(query)
        rows = cur.fetchall()

        if not rows:
            if show_logs:
                logging.info("Hasil query kosong")
            return []

        # Get the column names returned by the query
        column_names = [desc[0] for desc in cur.description]

        # If the columns argument is provided, extract the specified columns from the rows
        if columns:
            results = [dict(zip(column_names, row)) for row in rows]
            results = [[row[col] for col in columns] for row in results]
        else:
            # If the columns argument is not provided, return the rows as a list of lists
            results = rows

        if show_logs:
            logging.info(f"Hasil query: {results}")
        return results

    except (Exception, psycopg2.Error) as error:
        if show_logs:
            logging.error(f"Terjadi error: {error}")
        return []

    finally:
        if conn:
            cur.close()
            conn.close()
            if show_logs:
                logging.info("Koneksi PostgreSQL ditutup")

def query_and_get_rows(query, columns=None, connection_key='Merchant', show_logs=False):
    """
    Fungsi untuk menjalankan query dan memastikan hasil query dikembalikan dalam bentuk daftar baris.

    Args:
        query (str): Query SELECT yang akan dijalankan
        columns (list, optional): Daftar kolom yang ingin diambil nilainya
        connection_key (str, optional): Kunci untuk mengambil informasi koneksi dari file cred_database.json (default adalah 'Merchant')
        show_logs (bool, optional): Jika True, maka log akan ditampilkan. Jika False, maka log tidak akan ditampilkan (default adalah False)

    Returns:
        tuple: Tuple yang berisi daftar baris hasil query dan daftar nama kolom
    """
    result_data = connect_to_postgres2(query, columns, connection_key, show_logs)

    # Memastikan hasil query dalam bentuk daftar baris
    if isinstance(result_data, list):
        rows = result_data
    else:
        # Jika result_data bukan list, coba konversi menjadi list dengan satu elemen
        try:
            rows = [list(result_data)]
        except (TypeError, ValueError):
            # Jika data tidak dapat dikonversi menjadi list, kembalikan daftar kosong
            rows = []

    # Dapatkan nama kolom dari deskripsi kolom cursor
    conn = None
    try:
        # Baca informasi koneksi dari file cred_database.json
        with open('config/cred_database.json', 'r') as f:
            credentials = json.load(f)

        # Ambil informasi koneksi berdasarkan connection_key
        connection_info = credentials[connection_key][0]

        # Konfigurasi koneksi ke PostgreSQL
        conn = psycopg2.connect(
            host=connection_info['host'],
            database=connection_info['database'],
            user=connection_info['user'],
            password=connection_info['password']
        )
        cur = conn.cursor()
        cur.execute(query)
        column_names = [desc[0] for desc in cur.description]

        return rows, column_names

    except (Exception, psycopg2.Error) as error:
        if show_logs:
            logging.error(f"Terjadi error: {error}")
        return rows, []

    finally:
        if conn:
            cur.close()
            conn.close()
            if show_logs:
                logging.info("Koneksi PostgreSQL ditutup")


def wrap_single_int(data):
    """
    Fungsi untuk membungkus sebuah nilai integer dalam daftar.

    Args:
        data (any): Data yang akan diproses

    Returns:
        list: Daftar yang berisi data
    """
    if isinstance(data, int):
        return [data]
    else:
        return data
  
def ensure_list_of_rows(data):
    """
    Fungsi untuk memastikan data berupa daftar baris (list of rows).

    Args:
        data (any): Data yang akan diproses

    Returns:
        list: Daftar baris yang berisi data
    """
    if isinstance(data, int):
        # Jika data adalah integer, buat daftar dengan satu baris yang berisi nilai integer tersebut
        return [(str(data),)]
    elif isinstance(data, (list, tuple)):
        # Jika data iterable, konversi setiap elemen menjadi tuple
        return [tuple(str(value) for value in row) for row in data]
    else:
        # Jika data bukan integer atau iterable, coba konversi menjadi string
        try:
            data_str = str(data)
        except ValueError:
            # Jika data tidak dapat dikonversi menjadi string, kembalikan daftar kosong
            return []
        else:
            # Jika konversi berhasil, buat daftar dengan satu baris yang berisi data tersebut
            return [(data_str,)]
        
def get_nested_value(data, keys, default=None, show_logs=False):
    """
    Mengambil nilai dari kunci yang tertanam dalam objek atau daftar.

    Args:
        data (dict/list/str): Objek, daftar, atau string JSON yang akan diakses.
        keys (str): Kunci atau path kunci yang dipisahkan dengan titik untuk mengakses nilai.
        default (Any, optional): Nilai default yang akan dikembalikan jika kunci tidak ditemukan.
        show_logs (bool, optional): Jika True, maka log akan ditampilkan. Jika False, maka log tidak akan ditampilkan (default adalah False)

    Returns:
        Any: Nilai yang ditemukan atau default jika tidak ditemukan.
    """
    try:
        # Jika data adalah string, parse ke JSON terlebih dahulu
        if isinstance(data, str):
            data = json.loads(data.replace("'", '"'))

        # Pecah keys menjadi list
        key_parts = keys.split('.')

        # Iterasi melalui setiap key dan akses nilai
        current_value = data
        for key in key_parts:
            if isinstance(current_value, dict):
                current_value = current_value.get(key, default)
            elif isinstance(current_value, list):
                try:
                    index = int(key)
                    current_value = current_value[index]
                except (ValueError, IndexError):
                    if show_logs:
                        print(f"Error: Key '{key}' not found in data: {data}")
                    return default
            else:
                if show_logs:
                    print(f"Error: Unexpected data type for key '{key}': {type(current_value)}")
                return default

        return current_value
    except (KeyError, IndexError, TypeError, json.JSONDecodeError) as e:
        if show_logs:
            print(f"Error in get_nested_value: {e}")
        return default

def run_curl_command(curl_command, param_response=None):
    try:
        logging.info(f"Menjalankan perintah cURL: {curl_command}")
        result = subprocess.run(curl_command, shell=True, check=True, capture_output=True, text=True)
        logging.info(f"Keluaran standar:\n{result.stdout}")

        if result.stdout.startswith('{'):  # Cek apakah respons adalah JSON
            response_data = json.loads(result.stdout)
            http_status_code = response_data.get('code', None)
            logging.info(f"Status Code HTTP: {http_status_code}")

            if param_response:
                value = get_nested_value(response_data, param_response)
                logging.info(f"Nilai dari parameter '{param_response}': {value}")
                return value
            else:
                return response_data
        else:
            logging.info(f"Respons bukan dalam format JSON, tidak dapat mengekstrak status kode HTTP.")
            if param_response:
                logging.error("Parameter respons tidak dapat diekstrak dari respons non-JSON.")
                return None
            else:
                return result.stdout

    except subprocess.CalledProcessError as e:
        logging.error(f"Terjadi kesalahan saat menjalankan perintah cURL: {e.stderr}")
        return None
    
def validate_expression(a, b, expected_result):
    """
    Fungsi untuk memvalidasi hasil operasi aritmatika dengan nilai yang diharapkan.

    Args:
        a (int, float, decimal.Decimal, or str): Nilai pertama dalam operasi.
        b (int, float, decimal.Decimal, or str): Nilai kedua dalam operasi.
        expected_result (int, float, decimal.Decimal, or str): Nilai hasil yang diharapkan.
        show_logs (bool, optional): Jika True, maka log akan ditampilkan. Jika False, maka log tidak akan ditampilkan (default adalah False)

    Returns:
        bool: True jika hasil operasi sama dengan nilai yang diharapkan, False jika tidak.

    Raises:
        TypeError: Jika tipe data a, b, atau expected_result tidak valid.
    """
    try:
        # Konversi a, b, dan expected_result ke decimal.Decimal
        a = decimal.Decimal(str(a))
        b = decimal.Decimal(str(b))
        expected_result = decimal.Decimal(str(expected_result))
    except (ValueError, decimal.InvalidOperation):
        raise TypeError("Tipe data a, b, atau expected_result tidak valid.")
    
    result = a + b
    
    try:
        assert result == expected_result, f"Hasil operasi {a} + {b} tidak sesuai dengan nilai database ({expected_result}). Nilai dari hasil perhitungan: {result}"
    except AssertionError as e:
        error_message = str(e)
        logging.error(error_message)  # Selalu tampilkan logging.error
        return False
    else:
        success_message = f"Validasi berhasil untuk amount {a} + {b} = {expected_result}"
        logging.info(success_message)  # Log success message
        return True

def repetitive_assertion(pairs, show_logs=False):
    """
    Melakukan perulangan untuk memeriksa kesamaan setiap pasangan dalam daftar pairs.
    Jika semua pasangan sesuai, hanya akan menampilkan log 'Passed'.
    Jika ada pasangan yang tidak sesuai, akan menampilkan log untuk pasangan tersebut.

    Args:
        pairs (list): Daftar pasangan yang akan diperiksa.
        show_logs (bool, optional): Jika True, maka log akan ditampilkan. Jika False, maka log tidak akan ditampilkan (default adalah False)
    """
    failed_pairs = []  # Daftar pasangan yang tidak sesuai

    for i, pair in enumerate(pairs, 1):
        try:
            pair = tuple(str(item) for item in pair)
            assert pair[0] == pair[1], f"Test {i} failed: {pair[0]} != {pair[1]}"
            if show_logs:
                logging.info(f"Test {i} passed: {pair[0]} == {pair[1]}")
        except AssertionError as e:
            failed_pairs.append(pair)
            if show_logs:
                logging.error(str(e))

    if failed_pairs:
        logging.info(f"Terdapat {len(failed_pairs)} pasangan yang tidak sesuai:")
        for i, pair in enumerate(failed_pairs, 1):
            logging.info(f"Test {i} failed: {pair[0]} != {pair[1]}")
    else:
        logging.info("Validasi sesuai")
            
def get_dinamis_trx_id(data):
    if data is None:
        return None
    keys = 'body.linkUrlQr'
    data_minify = jsonParser.jsonParserMinify(data)
    output = get_nested_value(data_minify, keys)
    substring = output.split('/')[-1]  # extract substring after last '/'
    return(substring)  # prints '7fad6563a1e6490f83500c1c9bd87eda'

def get_parameter_value(data, parameter):
    """
    Fungsi untuk mendapatkan nilai dari parameter tertentu dalam sebuah data JSON.

    Args:
        data (str): Data JSON dalam format string.
        parameter (str): Nama parameter yang ingin diambil nilainya.

    Returns:
        value: Nilai dari parameter yang diberikan, atau None jika parameter tidak ditemukan.
    """
    # Parse the string into a dictionary
    data_dict = json.loads(data)
    # Access the value of the parameter key
    value = data_dict.get(parameter)
    return value

def open_url(url):
    """
    Fungsi untuk membuka URL menggunakan Selenium.
    Args:
        url (str): URL yang ingin dibuka.
    Returns:
        driver (WebDriver): Instance WebDriver yang telah membuka URL.
    """
    driver = webdriver.Chrome()
    driver.get(url)
    return driver

def close_browser(driver):
    """
    Fungsi untuk menutup browser yang dikendalikan oleh instance WebDriver.
    Args:
        driver (WebDriver): Instance WebDriver yang mengendalikan browser.
    Returns:
        None
    """
    driver.quit()

def click_element_repeatedly(driver, strategy, locator, num_clicks=1, delay=0):
    """
    Fungsi untuk melakukan klik pada elemen tertentu secara repetitif.

    Args:
        driver (WebDriver): Instance WebDriver yang telah membuka URL.
        strategy (str): Strategi pencarian elemen (xpath, id, class_name, tag_name, name, link_text, partial_link_text).
        locator (str): Nilai pencarian elemen.
        num_clicks (int): Jumlah kali klik pada elemen. Nilai default adalah 1.
        delay (int): Jeda waktu dalam detik antara setiap klik. Nilai default adalah 0.

    Returns:
        str: Teks dari elemen yang diklik setelah klik terakhir, atau nilai locator jika elemen tidak memiliki teks.
    """
    wait = WebDriverWait(driver, 10)
    strategy_map = {
        "xpath": By.XPATH,
        "id": By.ID,
        "class_name": By.CLASS_NAME,
        "tag_name": By.TAG_NAME,
        "name": By.NAME,
        "link_text": By.LINK_TEXT,
        "partial_link_text": By.PARTIAL_LINK_TEXT
    }
    by_strategy = strategy_map.get(strategy.lower())
    if by_strategy is None:
        raise ValueError(f"Strategi pencarian '{strategy}' tidak valid.")

    element_locator = (by_strategy, locator)
    element = wait.until(EC.presence_of_element_located(element_locator))

    for i in range(num_clicks):
        try:
            element = wait.until(EC.presence_of_element_located(element_locator))
            element.click()
            print(f"Klik pada elemen ({i + 1}/{num_clicks})")
        except (StaleElementReferenceException, NoSuchElementException):
            # Jika terjadi StaleElementReferenceException atau NoSuchElementException, cari elemen kembali
            try:
                element = wait.until(EC.presence_of_element_located(element_locator))
                element.click()
                print(f"Klik pada elemen (retry {i + 1}/{num_clicks})")
            except NoSuchElementException:
                raise NoSuchElementException(f"Elemen dengan locator '{locator}' tidak ditemukan.")
        time.sleep(delay)

def get_element_value_repeatedly(driver, strategy, locator, num_times=1, delay=0):
    """
    Fungsi untuk mendapatkan nilai dari elemen secara repetitif.
    Args:
        driver (WebDriver): Instance WebDriver yang telah membuka URL.
        strategy (str): Strategi pencarian elemen (xpath, id, class_name, tag_name, name, link_text, partial_link_text).
        locator (str): Nilai pencarian elemen.
        num_times (int): Jumlah kali mendapatkan nilai elemen. Nilai default adalah 1.
        delay (int): Jeda waktu dalam detik antara setiap pengambilan nilai. Nilai default adalah 0.
    Returns:
        None
    """
    wait = WebDriverWait(driver, 10)
    strategy_map = {
        "xpath": By.XPATH,
        "id": By.ID,
        "class_name": By.CLASS_NAME,
        "tag_name": By.TAG_NAME,
        "name": By.NAME,
        "link_text": By.LINK_TEXT,
        "partial_link_text": By.PARTIAL_LINK_TEXT
    }
    by_strategy = strategy_map.get(strategy.lower())
    if by_strategy is None:
        raise ValueError(f"Strategi pencarian '{strategy}' tidak valid.")

    element_locator = (by_strategy, locator)

    for i in range(num_times):
        element = wait.until(EC.presence_of_element_located(element_locator))
        element_value = element.text
        print(f"Nilai elemen ({i + 1}/{num_times}): {element_value}")
        time.sleep(delay)

def input_text_repeatedly(driver, strategy, locator, text, num_times=1, delay=0):
    """
    Fungsi untuk melakukan input teks secara repetitif pada suatu elemen.
    Args:
        driver (WebDriver): Instance WebDriver yang telah membuka URL.
        strategy (str): Strategi pencarian elemen (xpath, id, class_name, tag_name, name, link_text, partial_link_text).
        locator (str): Nilai pencarian elemen.
        text (str): Teks yang akan diinput.
        num_times (int): Jumlah kali input teks. Nilai default adalah 1.
        delay (int): Jeda waktu dalam detik antara setiap input teks. Nilai default adalah 0.
    Returns:
        None
    """
    wait = WebDriverWait(driver, 10)
    strategy_map = {
        "xpath": By.XPATH,
        "id": By.ID,
        "class_name": By.CLASS_NAME,
        "tag_name": By.TAG_NAME,
        "name": By.NAME,
        "link_text": By.LINK_TEXT,
        "partial_link_text": By.PARTIAL_LINK_TEXT
    }
    by_strategy = strategy_map.get(strategy.lower())
    if by_strategy is None:
        raise ValueError(f"Strategi pencarian '{strategy}' tidak valid.")

    element_locator = (by_strategy, locator)

    for i in range(num_times):
        element = wait.until(EC.presence_of_element_located(element_locator))
        element.clear()
        element.send_keys(text)
        print(f"Input teks ({i + 1}/{num_times}): {text}")
        time.sleep(delay)

def wait_for_element(driver, strategy, locator, timeout=20):
    """
    Fungsi untuk menunggu sebuah elemen muncul di halaman hingga waktu tertentu.
    Args:
        driver (WebDriver): Instance WebDriver yang mengendalikan browser.
        strategy (str): Strategi pencarian elemen (xpath, id, class_name, tag_name, name, link_text, partial_link_text).
        locator (str): Nilai pencarian elemen.
        timeout (int): Waktu maksimum dalam detik untuk menunggu elemen muncul. Nilai default adalah 20 detik.
    Returns:
        WebElement: Elemen yang ditemukan, atau None jika elemen tidak ditemukan dalam waktu yang ditentukan.
    """
    try:
        strategy_map = {
            "xpath": By.XPATH,
            "id": By.ID,
            "class_name": By.CLASS_NAME,
            "tag_name": By.TAG_NAME,
            "name": By.NAME,
            "link_text": By.LINK_TEXT,
            "partial_link_text": By.PARTIAL_LINK_TEXT
        }
        by_strategy = strategy_map.get(strategy.lower())
        if by_strategy is None:
            raise ValueError(f"Strategi pencarian '{strategy}' tidak valid.")

        element_locator = (by_strategy, locator)
        wait = WebDriverWait(driver, timeout)
        element = wait.until(EC.presence_of_element_located(element_locator))
        return element
    except TimeoutException:
        print(f"Elemen dengan lokator {element_locator} tidak ditemukan dalam {timeout} detik.")
        return None

def calculate_difference_with_userids(data1, data2):
    """
    Menghitung pengurangan antara data2 dan data1.
    Data dengan nilai 'userid' akan tetap ditampilkan.

    Args:
        data1 (list): List pertama.
        data2 (list): List kedua.

    Returns:
        list: Hasil pengurangan antara data2 dan data1.
    """
    result = []

    for i in range(len(data1)):
        # Jika elemen adalah 'userid', tambahkan langsung ke hasil
        if isinstance(data1[i], str) and data1[i] == data2[i]:
            result.append(data1[i])
        # Jika elemen adalah Decimal, lakukan pengurangan Decimal
        elif isinstance(data1[i], decimal) and isinstance(data2[i], decimal):
            diff = data2[i] - data1[i]
            result.append(diff)
        else:
            result.append(data2[i])  # Tambahkan langsung jika bukan 'userid'

    return result

### --------------------------- Validasi Perhitungan ---------------------------

"""
# Contoh penggunaan
a = 1
b = 2
expected_result = 3

if validate_expression(a, b, expected_result):
    print("Validasi berhasil!")
else:
    print("Validasi gagal.")

# Contoh lain dengan hasil yang tidak sesuai
a = 5
b = 3
expected_result = 10

if validate_expression(a, b, expected_result):
    print("Validasi berhasil!")
else:
    print("Validasi gagal.")
"""

### --------------------------- Query ---------------------------

# Contoh penggunaan
query = "SELECT * FROM tabel_hewan"

# Menampilkan semua kolom
#hasil_semua_kolom = connect_to_postgres(query, connection_key='A')

# Menampilkan kolom tertentu
columns = ["Nama", "id"]
#hasil_kolom_tertentu = connect_to_postgres(query, columns, connection_key='B')

### --------------------------- HTTP ---------------------------
#url = 'https://api.example.com/data'
#headers = {'Content-Type': 'application/json'}
#data = {'name': 'John Doe', 'age': 30}

# Mengirim permintaan POST dan mendapatkan seluruh respons
#response = send_http_request('POST', url, data=data, headers=headers)
#print(response)

# Mengirim permintaan GET dan mendapatkan nilai dari parameter tertentu
#url = 'https://api.example.com/users?age=>25&city=New+York'
#headers = {'Authorization': 'Bearer token123'}
#response = send_http_request('GET', url, headers=headers)

#create_log_message('testcase 1')
#url = 'https://httpbin.org/get'
#response = send_http_request('GET', 'https://httpbin.org/get', response_params='headers.Accept-Encoding')

url = 'https://pay-stg.netzme.com/api/v1/invoice/createTransaction'
header = {'Authorization': 'custom P4IOiP4LOeBb7tN8X50iFFXB+fbEVUXXpIsx5iYWpDs=','Content-Type': 'application/json'}
data = '{"request":{"merchant":"M_TB1NMLig","amount":10001,"email":"Netzmea1831141@gmail.com","notes":"desc","description":"pembelian-Feeney","phone_number":"+62817345544","image_url":"","fullname":"pecobaan qa 1","amount_detail":{"basicAmount":10001,"shippingAmount":0},"payment_method":"VA_BNI","commission_percentage":0,"expire_in_second":960000,"fee_type":"on_seller","partner_transaction_id":"PartnerBankS-32739139","trxSource":"banksumpah"}}'
#response = send_http_request('POST', url=url, data=data, headers=header)

cuurl = """curl -X POST 'https://pay-stg.netzme.com/api/v1/invoice/createTransaction' -H 'Authorization: custom P4IOiP4LOeBb7tN8X50iFFXB+fbEVUXXpIsx5iYWpDs=' -H 'Content-Type: application/json' -d '{"request": {"merchant": "M_TB1NMLig", "amount": 10001, "email": "Netzmea1831141@gmail.com", "notes": "desc", "description": "pembelian-Feeney", "phone_number": "+62817345544", "image_url": "", "fullname": "pecobaan qa 1", "amount_detail": {"basicAmount": 10001, "shippingAmount": 0}, "payment_method": "VA_BNI", "commission_percentage": 0, "expire_in_second": 960000, "fee_type": "on_seller", "partner_transaction_id": "PartnerBankS-32739139", "trxSource": "banksumpah"}}'"""

#va_number = run_curl_command(cuurl, 'result.virtualAccountData.0.virtualAccountNo')
#print (va_number)

def send_http_request_mac(method, url, headers=None, response_params=None, body_request=None, mac=None, key=None, show_logs=False):
    """
    Fungsi untuk mengirim permintaan HTTP dan mengambil nilai dari parameter tertentu pada respons.
    Fungsi ini juga dapat menambahkan header 'mac' dengan nilai yang dihitung menggunakan HMAC-SHA-256 atau HMAC-SHA-512 dari body_request.

    Args:
        method (str): Metode HTTP (POST atau GET)
        url (str): URL tujuan (termasuk parameter jika ada)
        headers (dict or str, optional): Header permintaan HTTP
        response_params (str or list, optional): Parameter yang ingin diambil nilainya dari respons
        body_request (dict or str, optional): Data yang akan dikirim dalam body request (untuk metode POST dengan JSON data)
        mac (str, optional): Metode hash yang akan digunakan untuk menghitung nilai 'mac' (default=None, opsi: 'sha256', 'sha512')
        key (str, optional): Kunci rahasia yang akan digunakan sebagai keybit dalam penghitungan HMAC (default=None)
        show_logs (bool, optional): Jika True, maka log akan ditampilkan. Jika False, maka log tidak akan ditampilkan (default adalah False)

    Returns:
        dict or list or str: Respons lengkap dari permintaan HTTP atau nilai dari parameter yang diminta
    """
    method = method.upper()

    # Handle headers
    if isinstance(headers, str):
        try:
            headers = json.loads(headers.replace("'", '"'))
        except json.JSONDecodeError:
            if show_logs:
                logging.error(f"Header tidak valid: {headers}")
            headers = {}
    elif headers is None:
        headers = {}

    # Log headers yang digunakan
    if headers and show_logs:
        logging.info(f"Headers yang digunakan: {headers}")

    # Handle body_request
    body_str = None
    if isinstance(body_request, dict):
        body_str = json.dumps(body_request, sort_keys=True)
    elif isinstance(body_request, str):
        try:
            body_dict = json.loads(body_request.replace("'", '"'))
            body_str = json.dumps(body_dict, sort_keys=True)
        except json.JSONDecodeError:
            if show_logs:
                logging.error(f"Body request tidak valid: {body_request}")
            body_str = None
    elif body_request is None:
        body_str = ''

    # Menghitung nilai 'mac' jika diperlukan
    if mac is not None:
        mac = mac.lower()
        if body_str is not None:
            if mac == 'sha256':
                if key:
                    hash_obj = hmac.new(key.encode(), body_str.encode(), hashlib.sha256)
                else:
                    hash_obj = hashlib.sha256(body_str.encode())
            elif mac == 'sha512':
                if key:
                    hash_obj = hmac.new(key.encode(), body_str.encode(), hashlib.sha512)
                else:
                    hash_obj = hashlib.sha512(body_str.encode())
            else:
                if show_logs:
                    logging.error(f"Metode hash '{mac}' tidak didukung. Pilihan yang valid: 'sha256', 'sha512'")
                hash_obj = None

            if hash_obj:
                mac_value = hash_obj.hexdigest().upper()
                headers['mac'] = mac_value
                if show_logs:
                    logging.info(f"Header 'mac' ditambahkan dengan nilai: {mac_value}")
        else:
            if show_logs:
                logging.error("Body request tidak valid atau kosong, tidak dapat menghitung nilai 'mac'")

    if method == 'POST':
        if show_logs:
            logging.info(f'Mengirim permintaan POST ke {url}')
        if headers:
            if body_str:
                if show_logs:
                    logging.info(f'Body Request: {body_str}')
                response = requests.post(url, data=body_str, headers=headers)
            else:
                response = requests.post(url, headers=headers)
        else:
            if body_str:
                if show_logs:
                    logging.info(f'Body Request: {body_str}')
                response = requests.post(url, data=body_str)
            else:
                response = requests.post(url)
    elif method == 'GET':
        if show_logs:
            logging.info(f'Mengirim permintaan GET ke {url}')
        if headers:
            response = requests.get(url, headers=headers)
        else:
            response = requests.get(url)
    else:
        raise ValueError('Metode HTTP tidak valid. Harus POST atau GET.')

    if show_logs:
        logging.info(f'Respons diterima: Status Code {response.status_code}')

    if response.headers.get('Content-Type', '').startswith('application/json'):
        response_data = response.json()
        if show_logs:
            logging.info(f'Respons JSON: {response_data}')

        if response_params:
            values = _extract_values_from_response(response_data, response_params)
            return values
        else:
            return response_data
    else:
        response_text = response.text
        if show_logs:
            logging.info(f'Respons Text: {response_text}')
        return response_text
