import requests
from src.modules import Modules
from src.xmlParser import xmlParser  # Pastikan ini diimpor

class topupNetzme():
    def __init__(self, parent):
        super().__init__(parent)
            
    def topup_netzme(no_va, amount):
        #Topup Netzme
        bank = 'BCA'
        random12 = Modules.RandomDigit(12)
        faspay_user = 'bot31922'
        faspay_pass = 'p@ssw0rd'
        base_url = 'https://paway-stg.netzme.com/fp/payment/notification'
        dates = Modules.get_current_date_topup()
        signature2 = Modules.Get_Signature_Top_Up(faspay_user,faspay_pass,no_va)
        bodyVA = '<faspay><request>Payment Notification</request><trx_id>' + random12 + '</trx_id><merchant_id>'+ bank +'</merchant_id><merchant>'+ bank +'</merchant><bill_no>' + no_va + '</bill_no><payment_reff>null</payment_reff><payment_date>' + dates + '</payment_date><payment_status_code>2</payment_status_code><payment_status_desc>Success</payment_status_desc><amount>' + amount + '</amount><signature>' + signature2 + '</signature><payment_total>' + amount + '</payment_total></faspay>'
        headerreq={'Content-Type':'application/xml'}

        if int(amount) < 50000:
            return 'Amount harus diatas 50rb'
        else:
            r = Modules.POSThttpNotJSONHeaders(base_url, headerreq, bodyVA)
            print ('body request : ' + bodyVA)
            
            # Decode respons bytes menjadi string
            response_content = r.content.decode('utf-8')
            
            # Gunakan xmlParser untuk memformat respons
            formatted_response = xmlParser.xmlParserBeautify(response_content)
            
            print(formatted_response)
            return formatted_response

    #topup_netzme('11382085172343499','100000')