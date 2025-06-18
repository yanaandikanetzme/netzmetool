from src.modules import Modules
import random
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import random, string
import string
from src.modules import Modules
from app.tabs.popup import ResponseOpenAPI
from src.jsonParser import jsonParser


def testHitFDS():
    for x in range(100):
        jm = str('%0.2d' % random.randint(0, 6))
        mnt = str('%0.2d' % random.randint(0, 59))
        dtk = str('%0.2d' % random.randint(0, 59))

        randomrrn = Modules.RandomDigit(12)
        date = Modules.DateNowSec()
        datenow = '2023-12-13 '+jm+':'+mnt+':'+dtk+'.799+00'
        issuerId = '93600911'
        acquirerId = '93600814'
        uuid = Modules.generateUUID()
        mpan = acquirerId + str(random.randint(10000000, 99999999))
        cpan = issuerId + str(random.randint(10000000, 99999999))

        refId = randomrrn + date + issuerId
        numberNominal = str(random.randint(100, 20000)) + '00'

        url = 'https://u_netzme:b89b9754592765cE8d4C95f501DdDA2D6E36d8CE5305B95b5fF064e71BbE3525@fds-api-stg.netzme.id/predict/model'
        requestBody = {"request_id":uuid,"transaction_time":datenow,"ref_id":refId,"trx_code":"260000","trace_no":"123456","terminal_id":"A01","merchant_pan":mpan,"acquirer":acquirerId,"issuer":issuerId,"customer_pan":cpan,"nominal": numberNominal+'.0',"merchant_category":"5399","merchant_criteria":"UMI","response_code":"0","merchant_id":"ID2021000001712","merchant_city":"SIMEULUE","merchant_country":"62","convenience_fee":0.0,"interchange_fee":0.0}
        print('------------------------------------------------------------------------------------')
        print(Modules.POSThttp(url,requestBody))
        print('Hit ke : ' + str(x+1))


#testHitFDS()

url = 'https://api-stg.netzme.com/payment/balance'
headers = {'content-type': 'application/json', 'Authorization': 'Basic bnRyQ0FvVmk6RGF1ZG16dGY4Rw==', 'Accept': 'application/json'}
method = 'GET'
body = {"type":"topup_va_list"}

response = Modules.make_http_request(url=url, headers=headers)

if response:
    http_status_code = response[0]
    response_message = response[1]
    print(response_message)
    response_message = jsonParser.jsonParserBeautify(response_message)
    msgbox = f"\nHTTP Status Code: {http_status_code}\nResponse Message: {response_message}"
    print(msgbox)
    