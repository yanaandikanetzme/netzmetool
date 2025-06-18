from automation.src.base import create_log_message, send_http_request, connect_to_postgres
from src.modules import Modules

url = 'https://pay-stg.netzme.com/api/v1/invoice/createTransaction'
header = {'Authorization': 'custom P4IOiP4LOeBb7tN8X50iFFXB+fbEVUXXpIsx5iYWpDs=','Content-Type': 'application/json'}

credentials_prod = {
    "client_id": "merchantqasnap",
    "client_secret": "5e19734c851240e2b37f23a32715dc68",
    "private_key": "MIIBOwIBAAJBAKfdxaK7SdvlHeW2KSl6KXW/Q4+uIXUGTSqoEAkqzQzUHRrXhfFYe8sc9mxXRXR8xF2MAhgqydbrVOLyj3U/N9sCAwEAAQJADcCMZWWEioA9r8j5nE1Gwj+2EDpKwWSPw9Pa5HVeMRO5dtpjyIOar1xPsZD8znWQiDJsD0kV2wByvgLsYFBBQQIhAN4KB6pYMb0jWWDaR0wvBtDvdcFqvi2yI1e7sCSp3H4hAiEAwYqYtURnS6Zt2dsT0W+wQ+1ZnSUlCKlqZyydnNku3nsCIQCqlRAQiZMk2Lx40RlHaTWWXPGdt9EFsD7Azzvi3vC7oQIgWbMIj4qCbVdXNk8I4lpnUTQiAmkCvv7155eP/O/Tfx0CIQClHn77Z8Gx/ZDmL1h1+FnTVVhgjz5dzCM8gjw33WVwFQ==",
    "x-callback-token": "2jULkeQLPYanBrhc3WZffekjl9T5s2bJqJwyxKbjREY="
}

credentials_stg = {
                    "client_id": "banksumpah",
                    "client_secret": "e4a63488152d4150935c88d1e0412925",
                    "private_key": "MIIBOwIBAAJBAJ3lNsAfsufNWrZvJGg7Bov7tj5SzHr1J8YlrqD9isioFs8M/DY/u4KNvTEScg7QIL5jLFfSR2OTI36ltmutlCMCAwEAAQJARtHve778DLJz9I3nQ4TuC81r0Yprwt7A50Qxjm4KWLMvpOxNYS7jgWthIqY4ZjjdCAFpuvABPd1JfvhIvUlqSQIhAMjqCr1ZFKZDBx+AwBXhpXk0kwZB5HTa3zR+GbcNoibFAiEAyS+5M2qHpQNW1XF7wxYe01HGlrCD8iqE/3N9XDwavccCICqBYT5H31eBbLtceMboUyK+XbCANj4GpBwt5XDVwI1lAiEAobYwgTmRynuCopJTTp5LLMTAgYNkq5Stzr8/9pGBVSUCIQCb45S9PildaIDrnvphw6G6tNvJaI4tuGEHVPrwEMYCHA==",
                    "x-callback-token": "P4IOiP4LOeBb7tN8X50iFFXB+fbEVUXXpIsx5iYWpDs="
                    }
enve = 'stg'

def create_invoice_snap(payment_method, merchant_id):
    amount = '1' + Modules.RandomDigit(5)
    feetype = 'on_seller'
    clientId = 'merchantqasnap'
    random12num = clientId + "-" + Modules.RandomDigit(12)
    bodyreq = {"custIdMerchant":merchant_id,"partnerReferenceNo":random12num,"amount":{"value":amount,"currency":"IDR"},"amountDetail":{"basicAmount":{"value":amount,"currency":"IDR"},"shippingAmount":{"value":"0","currency":"IDR"}},"PayMethod":payment_method,"commissionPercentage":"0","expireInSecond":"3600","feeType":feetype,"additionalInfo":{"email":"purba.jati@netzme.id","notes":"desc","description":"description","phoneNumber":"+6285172343499","imageUrl":"a","fullname":"qanetzme"}}

def create_invoice(payment_method, merchant_id):
    feetype = 'on_seller'
    MerchantId = merchant_id
    amount = '1' + Modules.RandomDigit(5)
    clientId = 'banksumpah'
    random12num = Modules.RandomDigit(12)
    bodyreq = {"request":{"merchant":MerchantId,"amount":amount,"email":"purbaperdanajati@gmail.com",
                                "notes":"desc","description":"description","phone_number":"+62817345545",
                                "image_url":"","fullname":"Percoba QA",
                                "amount_detail":{"basicAmount":amount,"shippingAmount":0},
                                "payment_method":payment_method,"commission_percentage":0,
                                "expire_in_second":3600,"fee_type":feetype,
                                "partner_transaction_id":clientId + "-" + random12num}}
    
    #create_log_message(f'Create Invoice {payment_method}')
    resp = send_http_request('POST', url=url, body_request=bodyreq, headers=header, response_params='result.trxId')
    if resp == None:
        return ValueError
    output = []
    output.append(str(payment_method))
    output.append(str(amount))
    output.append(str(resp))
    return (output)
