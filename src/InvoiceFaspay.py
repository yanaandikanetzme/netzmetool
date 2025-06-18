import datetime
from src.modules import Modules
import yaml

class FaspayPay():
        def __init__(self, parent):
                super().__init__(parent)

        def FaspayPayDef(amount, trx_id, bill_no):
                with open("config/config.yaml", "r") as yamlfile:
                        data = yaml.load(yamlfile, Loader=yaml.FullLoader)
                        FaspayUser = data[0]['Details']['Faspay']['FaspayUser']
                        FaspayPass = data[0]['Details']['Faspay']['FaspayPass']
                ctanggal = datetime.datetime.now().strftime('%Y%m%d')
                rawsignature = FaspayUser + FaspayPass + bill_no + "2"
                #bot310001p@ssw0rdfbdebbc477634da48706a4fabd2015b02
                rawsignatureMD5 = Modules.HashMD5(rawsignature)
                rawsignatureSHA1 = Modules.HashSHA1(rawsignatureMD5.lower())
                signatures = rawsignatureSHA1
                bodyreq = {
                'request': 'Payment Notification',
                'trx_id': trx_id,
                'merchant_id': '31835',
                'merchant': 'NETZME',
                'bill_no': bill_no,
                'payment_reff': 'null',
                'payment_date': ctanggal,
                'payment_status_code': '2',
                'payment_status_desc': 'Payment Sukses',
                'bill_total': amount,
                'payment_total': 38833,
                'payment_channel_uid': '702',
                'payment_channel': 'VA BCA',
                'signature': signatures
                }
                #print('rawsignature : ' + rawsignature)
                #print('rawsignatureMD5 : ' + rawsignatureMD5)
                #print('rawsignatureSHA1 : ' + rawsignatureSHA1)
                #print('bodyreq : ' + str(bodyreq))
                return bodyreq 