import json
from src.modules import Modules

reff_id = str(Modules.generate_date() + Modules.RandomDigit(4))
trx_date = str(Modules.current_milli_time())

class InvoiceIndomaret():
    def __init__(self, parent):
        super().__init__(parent)

    def inquiryIndomaret(va, merchId):
        url = 'https://mcapi-stg.netzme.com/otc/generate/payment/inquiry'
        raw = (va + reff_id + trx_date + merchId + 'TmV0em1lTXN0')
        print(raw)
        sha = Modules.HashSHA256(str(raw))
        dictionary = {'payment_code':va,'reff_id':int(reff_id),'trx_date':int(trx_date),'merchant_code':merchId,'token':sha}
        jsonString = json.dumps(dictionary, indent=4)
        print('url inquiry : ' + url)
        print('body inquiry : ' + str(dictionary))
        #print ('json request : ' + jsonString)
        #requests.post(url, data={key: value}, json={key: value}, args)
        post_response = Modules.POSThttpHeadersWithoutHeaders(url, dictionary)
        #post_response_json = post_response.json()
        print('inquiry payment : ' + str(post_response))
        return str(post_response)

    def paymentIndomaret(va, amt, merchId):
        url = 'https://mcapi-stg.netzme.com/otc/generate/payment/confirmation'
        raw = (str(va) + str(amt) + reff_id + trx_date + merchId + 'TmV0em1lTXN0')
        print(raw)
        sha = Modules.HashSHA256(str(raw))
        dictionary = {'payment_code':va,'total_amount':int(amt),'reff_id':int(reff_id),'trx_date':int(trx_date),'merchant_code':merchId,'token':sha}
        jsonString = json.dumps(dictionary, indent=4)
        #print ('json request : ' + jsonString)
        print('url payment : ' + url)
        print('body payment : ' + str(dictionary))
        post_response = Modules.POSThttpHeadersWithoutHeaders(url, dictionary)
        #post_response_json = post_response.json()
        print('response payment : ' + str(post_response))
        return str(post_response)
