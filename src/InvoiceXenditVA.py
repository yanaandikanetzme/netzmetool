import json
import requests

class InvoiceXenditVA():
    def __init__(self, parent):
        super().__init__(parent)
    
    def generateURLXenditVA(vendor_id, amount):
        try:
            url = 'https://api.xendit.co/v2/payment_methods/' + vendor_id + '/payments/simulate'
            amountInt = int(amount)
            body = {"amount":amountInt}
            header = {"Authorization":"Basic eG5kX2RldmVsb3BtZW50X0VYQ1RPU0RoQjRuelhzWUxOREtkMVNLTzRMcm90R3BPVklTbk9sMjVJVUNJMlVpNkMzbDlVNnlhUEVGbzQyOg=="}
            jsonString = json.dumps(body, indent=4)
            post_response = requests.post(url, json=body, headers=header)
            print(jsonString)
            print(post_response)
            if post_response.status_code == 200:
                aaa = post_response.json()
                return aaa
            else:
                a = str(post_response.status_code) + ' ' + str(post_response.reason)
                return a
        except IndexError as e:
            return(f"{e}")
        except requests.exceptions.HTTPError as error:
            return(f"{error}")
        except requests.exceptions.ConnectionError as b:
            return(f"{b}")
