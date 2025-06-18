from src.modules import Modules
from automation.database import get_password_merchant
from automation.src.base import send_http_request, get_dinamis_trx_id

def create_qr_dinamis(merchant_id, showlogs:bool = False):
    nominal = str('1' + Modules.RandomDigit(5))
    guid = Modules.generateUUID()
    url = 'https://tokoapi-stg.netzme.com/api/merchant/qr/dynamic'
    bodyreq = '{"requestId":"' + guid + '","type":"get_qr_dynamic","requestTime":0,"body":{"amount":"IDR ' + str(nominal) + '.0","feeAmount":"IDR 0.00","trxSource":"banksumpah","userId":"' + merchant_id + '"}}'
    raw_pass = merchant_id + ":" + get_password_merchant(merchant_id, showlog=showlogs)[0]
    hashed = Modules.base64Encode(raw_pass)
    header = {"Authorization": "Basic " + hashed}
    response = send_http_request("POST", url=url, headers=header, body_request=bodyreq, show_logs=showlogs)
    trx_id = get_dinamis_trx_id(response)
    return [str(nominal), str(trx_id)]
