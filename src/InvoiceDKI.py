import json
from tkinter import *
from src.modules import Modules
from src.jsonParser import jsonParser
from datetime import datetime
import yaml

baseurl='https://tokoapi-stg.netzme.com'
urlGetToken = "/oauth/merchant/dki/accesstoken"
urlInquiry = "/dki/merchant/inquiry/notif"
urlPayment = "/dki/merchant/payment/notif"
urlRefund = "/dki/merchant/reversal/notif"
xclientkey = 'dki'

with open("config/config.yaml", "r") as yamlfile:
    data = yaml.load(yamlfile, Loader=yaml.FullLoader)
    apiKey = data[0]['Details']['DKI']['apiKey']
    api_secret = data[0]['Details']['DKI']['api_secret']

cred = xclientkey + ":" + apiKey
auth = 'Basic ' + Modules.base64Encode(cred)


class InvoiceDKI():
    def __init__(self, parent):
            super().__init__(parent)

    def getRequestTokenDKI():
        try:
            url = baseurl + urlGetToken
            bd = {"grant_type":"client_credentials"}
            xtimestamp = datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]+'+07:00'
            getTokenSignature = xclientkey + '|' + xtimestamp
            xsignature = Modules.HashSHA256(getTokenSignature, api_secret)
            hd = {"Content-Type":"application/json", "X-CLIENT-KEY":xclientkey, "X-TIMESTAMP":xtimestamp, "X-SIGNATURE":xsignature}
            output = Modules.POSThttpHeaders(url, hd, bd)
            print(output)
            json_str1 = json.dumps(output)
            respa = json.loads(json_str1)['access_token']
            return str(respa)
        except (ValueError, KeyError) as error:
            return (str(error))

    def generateTokenCurl():
        try:
            method = 'POST'
            url = baseurl + urlGetToken
            bd = {"grant_type":"client_credentials"}
            xtimestamp = datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]+'+07:00'
            getTokenSignature = xclientkey + '|' + xtimestamp
            xsignature = Modules.HashSHA256(getTokenSignature, api_secret)
            hd = {"Content-Type":"application/json", "X-CLIENT-KEY":xclientkey, "X-TIMESTAMP":xtimestamp, "X-SIGNATURE":xsignature}
            curl = Modules.generate_curl_command(url,hd,bd)
            return curl
        except (ValueError, KeyError) as error:
            return (str(error))

    def generateInqCurl(VA, Amountz, token):
        try:
            method = 'POST'
            url = baseurl + urlInquiry
            xtimestamp = datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]+'+07:00'
            Amounts = f"{int(Amountz) :012d}"
            bodyreq='{"Amount":"' + Amounts + '","Transmission_Datetime":"1004094200","Stan":"123456","Settlement_Date":"1005","channel_ID":"6017","Retrieval_Reference_Number":"171234564200","cA_Terminal_ID":"TESTNETZ","cA_ID":"085782492004","Location_Name":"TESTNETZ","Private_data":"' + VA + '","Transmission_Year":"2022"}'
            minifybd = jsonParser.jsonParserMinify(bodyreq)
            BodySHA256 = Modules.HashSHA256(minifybd)
            plainSignature = 'POST:' + urlInquiry + ':' + token + ':' + BodySHA256 + ':' + xtimestamp
            signature = Modules.HashSHA256(plainSignature, api_secret)
            hd = {"Content-Type":"application/json", "X-CLIENT-KEY":xclientkey, "X-TIMESTAMP":xtimestamp, "X-SIGNATURE":signature, "Authorization":auth}
            bd=json.loads(bodyreq)
            curl = Modules.generate_curl_command(url,hd,bd)
            return curl
        except (ValueError, KeyError) as error:
            return (str(error))

    def generatePayCurl(VA, Amountz, token):
        try:
            method = 'POST'
            url = baseurl + urlPayment
            xtimestamp = datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]+'+07:00'
            Amounts = f"{int(Amountz) :012d}"
            bodyreq = '{"Amount":"' + Amounts + '","Transmission_Datetime":"1004094200","Stan":"123456","Settlement_Date":"1005","Channel_ID":"6017","Retrieval_Reference_Number":"171234564200","CA_Terminal_ID":"TESTNETZ","CA_ID":"085782492004","Location_Name":"TESTNETZ","Private_data":"' + VA + '","Transmission_Year":"2022","Src_Account":"085782492004"}'
            bd = json.loads(bodyreq)
            minifybd = jsonParser.jsonParserMinify(bodyreq)
            BodySHA256 = Modules.HashSHA256(minifybd)
            plainSignature = 'POST:' + urlPayment + ':' + token + ':' + BodySHA256 + ':' + xtimestamp
            signature = Modules.HashSHA256(plainSignature, api_secret)
            hd = {"Content-Type":"application/json", "X-CLIENT-KEY":xclientkey, "X-TIMESTAMP":xtimestamp, "X-SIGNATURE":signature, "Authorization":auth}
            curl = Modules.generate_curl_command(url,hd,bd)
            #print(curl)
            return curl
        except (ValueError, KeyError) as error:
            return (str(error))

    def inquiryInvoiceDKI(VA, Amountz, token):
        try:
            url = baseurl + urlInquiry
            xtimestamp = datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]+'+07:00'
            Amounts = f"{int(Amountz) :012d}"
            bodyreq='{"Amount":"' + Amounts + '","Transmission_Datetime":"1004094200","Stan":"123456","Settlement_Date":"1005","channel_ID":"6017","Retrieval_Reference_Number":"171234564200","cA_Terminal_ID":"TESTNETZ","cA_ID":"085782492004","Location_Name":"TESTNETZ","Private_data":"' + VA + '","Transmission_Year":"2022"}'
            minifybd = jsonParser.jsonParserMinify(bodyreq)
            BodySHA256 = Modules.HashSHA256(minifybd)
            print(token)
            print(url)
            print('Inquiry bodyreq : ' + str(bodyreq))
            print("BodySHA256 : " + BodySHA256)
            print(xtimestamp)
            plainSignature = 'POST:' + urlInquiry + ':' + token + ':' + BodySHA256 + ':' + xtimestamp
            signature = Modules.HashSHA256(plainSignature, api_secret)
            hd = {"Content-Type":"application/json", "X-CLIENT-KEY":xclientkey, "X-TIMESTAMP":xtimestamp, "X-SIGNATURE":signature, "Authorization":auth}
            print('plainSignature: ' + plainSignature)
            print('signature: ' + signature)
            bd=json.loads(bodyreq)
            resp = Modules.POSThttpHeaders(url, hd, bd)
            print(resp)
            return resp
        except (ValueError, KeyError) as error:
            return (str(error))

    def paymentInvoiceDKI(VA, Amountz, token):
        try:
            url = baseurl + urlPayment
            xtimestamp = datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]+'+07:00'
            Amounts = f"{int(Amountz) :012d}"
            bodyreq = '{"Amount":"' + Amounts + '","Transmission_Datetime":"1004094200","Stan":"123456","Settlement_Date":"1005","Channel_ID":"6017","Retrieval_Reference_Number":"171234564200","CA_Terminal_ID":"TESTNETZ","CA_ID":"085782492004","Location_Name":"TESTNETZ","Private_data":"' + VA + '","Transmission_Year":"2022","Src_Account":"085782492004"}'
            bd = json.loads(bodyreq)
            minifybd = jsonParser.jsonParserMinify(bodyreq)
            BodySHA256 = Modules.HashSHA256(minifybd)
            plainSignature = 'POST:' + urlPayment + ':' + token + ':' + BodySHA256 + ':' + xtimestamp
            signature = Modules.HashSHA256(plainSignature, api_secret)
            hd = {"Content-Type":"application/json", "X-CLIENT-KEY":xclientkey, "X-TIMESTAMP":xtimestamp, "X-SIGNATURE":signature, "Authorization":auth}
            resp = Modules.POSThttpHeaders(url, hd, bd)
            print(resp)
            return resp
        except (ValueError, KeyError) as error:
            return (str(error))
