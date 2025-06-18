import requests
import datetime
from src.modules import Modules

class topupNetzmePOS():
    def __init__(self, parent):
        super().__init__(parent)

    def topupPOS(nomorVA, nominalVa, adminVA):
        url = 'https://paway-stg.netzme.com/pos/va/notif'
        randomUuid = Modules.generateUUID()
        #"yyyy-MM-dd HH:mm:ss"
        ctanggal = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        inputhash = 'nomor_va=' + nomorVA + '&kode_inst=168&channel_id=001&nominal=' + nominalVa + '&admin=' + adminVA + '&refnumber=' + randomUuid + '&waktu_proses=' + ctanggal + '&nopen=5000'
        outputhash = Modules.HashSHA256(inputhash)
        reqBodyPost= {'nomor_va':nomorVA,'kode_inst':'168','channel_id':'001','nominal':nominalVa,'admin':adminVA,'waktu_proses':ctanggal,'refnumber':randomUuid,'nopen':'5000','hashing':outputhash}
        #print(outputhash)
        post_response = Modules.POSThttpHeadersWithoutHeaders(url, reqBodyPost)
        #post_response_json = post_response.json()
        #print(post_response_json)
        return str(post_response)

