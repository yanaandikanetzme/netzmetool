from automation.src.base import connect_to_postgres, send_http_request, send_http_request_mac, validate_expression, get_nested_value, get_parameter_value
from src.modules import Modules
import yaml
import re
from src.jsonParser import jsonParser

def check_events_merchant(traceId, showlog:bool = False):
    query = "select user_id, type, amount_value, status_message, balance_value, * from events where trace_id ='" + traceId + "'"
    output = connect_to_postgres(query, show_logs=showlog, connection_key='Merchant')
    return output

def check_mitra_netzme_transaction_detail(nominal, transactionId, showlog:bool = False):
    query = "select merchant_id, trx_ref_id, trx_amount, trx_net_amount, mdr_amount, * from mitra_netzme_transaction_detail mntd where mntd.trx_amount = '" + nominal + "' and mntd.trx_ref_id ='" + transactionId + "'"
    output = connect_to_postgres(query, show_logs=showlog, connection_key='Merchant')
    return output

def check_status_qr_merchant_transaction(nominal, rrn, showlog:bool = False):
    query = "select merchant_id,rrn_origin,amount_value,mdr_pctg,mdr_amount_roundup, trx_id, * from qr_merchant_transaction qmt where qmt.rrn_origin = '" + rrn + "' and qmt.amount_value = '" + nominal + "'"
    output = connect_to_postgres(query, show_logs=showlog, connection_key='Merchant')
    return output

def checkBalance(merchantId, showlog:bool = False):
    query = "SELECT merchant_balance_unsettle.user_id, SUM (merchant_balance_unsettle.balance) AS balance_unsettles, merchant_balance.balance as balance_settle, SUM(merchant_balance_unsettle.balance) + merchant_balance.balance as total_balance FROM merchant_balance_unsettle INNER JOIN merchant_balance ON merchant_balance.user_id = merchant_balance_unsettle.user_id where merchant_balance_unsettle.user_id in ('" + merchantId + "')  GROUP BY merchant_balance_unsettle.user_id,merchant_balance.balance order by merchant_balance_unsettle.user_id;"
    output = connect_to_postgres(query, show_logs=showlog, connection_key='Merchant')
    return output

def checkInvoiceStatus(invoiceTrxId, showlog:bool = False):
    query = "select mit.total_amount, mit.status from merchant_invoice_transaction mit where mit.invoice_transaction_id = '" + invoiceTrxId + "' order by paid_ts desc;"
    output = connect_to_postgres(query, show_logs=showlog, connection_key='Merchant')
    return output

def checkAggregatorNetzme(user_id_netzme, showlog:bool = False):
    query = "select aggregator_id from aggregator_users au where au.active_flag = true and au.user_id = '" + user_id_netzme + "' order by aggregator_id desc limit 1"
    output = connect_to_postgres(query, show_logs=showlog, connection_key='NetzmeNetzreg')
    return output

def checkHaspin(user_id_netzme, showlog:bool = False):
    query = "select hash_pin from user_pin up where up.user_name = '" + user_id_netzme + "'"
    output = connect_to_postgres(query, show_logs=showlog, connection_key='NetzmeNetzreg')
    return output

def getRRNbyEventsNetzme(user_id_netzme, ref_id, showlog:bool = False):
    query = "select details from events_latest_transaction elt where elt.user_id = '" + user_id_netzme + "' and ref_id = '" + ref_id + "' order by elt.ts desc limit 1"
    sas = connect_to_postgres(query, show_logs=showlog, connection_key='NetzmeLenjer')
    output = str(sas[0])
    data1 = jsonParser.jsonParserMinify(output)
    parameter = 'refId'
    ref_id = get_parameter_value(data1,parameter)
    return ref_id

def check_events_netzme(ref_id, showlog:bool = False):
    query = "select elt.amount_value, elt.type, details->>'status' as value from events_latest_transaction elt where ref_id = '" + ref_id + "' order by elt.ts desc limit 1;"
    output = connect_to_postgres(query, show_logs=showlog, connection_key='NetzmeLenjer')
    return output

def check_qris_payment(rrn28digit, showlog:bool = False):
    query = "select status, amount_value, qr_type, ref_id from qris_payment qp where rrn_payment ='" + rrn28digit + "' order by ts desc limit 1;"
    output = connect_to_postgres(query, show_logs=showlog, connection_key='Merchant')
    return output

def get_password_merchant(merchantId, showlog:bool = False):
    query = "select password_hash from merchant_users mu where mu.user_name = '" + merchantId + "' ;"
    output = connect_to_postgres(query, show_logs=showlog, connection_key='Merchant')
    return output

def check_balance_netzme(userId, showlog:bool = False):
    query = "select b.amount_value - SUM (pt.amount_value) AS total from balance b LEFT JOIN pending_transaction pt ON pt.user_id = b.user_id where b.user_id ='" + userId + "' group by b.user_id ;"
    output = connect_to_postgres(query, show_logs=showlog, connection_key='NetzmeLenjer')
    return output
