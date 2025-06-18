#lokasi test.py
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from automation.testcase import payment_invoice, payment_qris_dynamic, payment_qris_static


merchant_id = 'M_yyd5IuJz'
vendor_payment_off_us_acquirer = 'jalin_crossborder' #vendor untuk payment qris merchant
user_netzme = '8PxJMz3o'
logs = True

#vendor : jalin_domestik, jalin_crossborder, artajasa, check_status_jalin_domestik, check_status_cross_border, check_status_artajasa

payment_invoice(merchant_id, 'QRIS', is_mitra=True, off_us=False, user_id_netzme=user_netzme, logs=logs)
payment_invoice(merchant_id, 'QRIS', is_mitra=True, off_us=True, vendor=vendor_payment_off_us_acquirer, logs=logs)
payment_qris_static(merchant_id, is_mitra=True, vendore=vendor_payment_off_us_acquirer, logs=logs)
payment_qris_static(merchant_id, is_mitra=True, off_us=False, user_id_netzme=user_netzme, logs=logs)
payment_qris_dynamic(merchant_id, is_mitra=True, vendor=vendor_payment_off_us_acquirer, logs=logs)
payment_qris_dynamic(merchant_id, is_mitra=True, off_us=False, user_id_netzme=user_netzme, logs=logs)
