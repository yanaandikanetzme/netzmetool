import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.modules import Modules
from src.jsonParser import jsonParser
import hashlib
import hmac
import codecs


client_id='xplorinsnap'
CLIENT_SECRET = 'b856837012d643c2906e94164927f787'
private_key= "MIIBOgIBAAJBAMtxa/5kMlkxO/06NxcHvHvOhNHoocsomMdDXBHuM9FaBD5w44KSgbrl31AYInZreEv5OvkNhnpcrnOMhflLV+kCAwEAAQJAEXoW6u20nZDrNF/R57qUaJZfNqEjdQ5xwXx55lhuPyezMZvWZULBXGMpEA5i8VDIvp9lvFtAnH1psXnzwLiqWQIhANRPvLN7uiAo4kVz5rRVZi6reAfhoAqeNMs/YimCjhs3AiEA9U6CWf3hcm76WZmmJ0yYEHOqBBYExCuL6ipzbBM69d8CIEWeR/BK2AOHpHrFwJbNkg4np9pdv877hbBH/nZCGzsNAiA42GemmQmsbgE/0DZLtxkp/tOwPLYAC6NRsWKr8czg+wIhANQbBsy6C+z9lZGRcJ4VrVgZTLMAIgaRF4zxEuVrxIR3",
xcallbacktoken = "AA7aj/Ih2O/PQX2/SXPDAtYkyNabEqCKV21dXRq/7Fc="

HTTPMethod = 'POST'
EndpointUrl = '/api/v1.0/payment/balance-inquiry'
AccessToken ='eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE2OTg2ODk2ODEsImlhdCI6MTY5ODYzNTY4MSwiaXNzIjoieHBsb3JpbnNuYXAifQ.QT-C6gLdNJki7wCEj2w6QdTh10OzUITmGwzaCoClQSfkZDvXRfiLVpJTtwMZZXpbxCrIU5OLtAciRYw16a5UGQ'
XTIMESTAMP ='2022-11-10T00:00:00+07:00'
ReqBody = '{"partnerReferenceNo": "xplorinsnap92112645","AccountNo": "M_TB1NMLig"}'

minifyreqBody = jsonParser.jsonParserMinify(ReqBody)

shaReqbody = Modules.HashSHA256(minifyreqBody).lower()
print(shaReqbody)
stringToSign = HTTPMethod + ":" + EndpointUrl + ":" + AccessToken + ":" + shaReqbody + ":" + XTIMESTAMP
print(stringToSign)
aa = Modules.HashSHA512(stringToSign, CLIENT_SECRET)
print(aa)

print('--------------------------------------------------------------------------------------------------')


#--------------------
#ad73dcbcd0ed54d2055777fca93190c41926301438a75ca3dc60ad1303a80a8c
token = '8edcbea1a8af0c8a7dec118ccff5700fb342d3602ab0806739b576fb1340157c'
timestamp = '1698733922807'
rawKey = 'AMyrseIfnwhTwYG2-'+ timestamp + '-Bearer ' + token
rawSignature = 'path=/api/aggregator/merchant/qr/balance/detail?userId=M_TB1NMLig&method=GET&token=Bearer ' + token + '&timestamp='+ timestamp + '&body='

rawKey2 = 'AMyrseIfnwhTwYG2-1698721204352-Bearer 4166450ccbf446d4b94fd573df4f82e0ac8c296ef9d94ad4ff0c39e536220c1b'
rawSignature2 = 'path=/api/aggregator/merchant/invoice/transaction/6b5f2c37683a4598a2fedf1be4f494c1&method=GET&token=Bearer 4166450ccbf446d4b94fd573df4f82e0ac8c296ef9d94ad4ff0c39e536220c1b&timestamp=1698721204352&body='

ab = Modules.HashSHA256(rawSignature,rawKey)
bc = Modules.HashSHA256(rawSignature2,rawKey2)

#url=https://tokoapi.netzme.com/api/aggregator/merchant/qr/balance
#/detail?userId=M_C4px4Xee, params=null, headers={"Authorization":"Bearer 61a0de564780c687fcecd582011af423bd52aa418bcbdc903b91ad9003343738","Request-Time":"1698631205453","Signature":"335a570d888733ca5917c1b00de8832134a33d9b90041f1617835da857a578b3","Client-Id":"nutech",
#"Content-Type":"application/json"}
print('get balance')
print('rawKey = ' + rawKey)
print('rawSignature = ' + rawSignature)
print('signature = ' + ab)
print(' ')
print('get invoice transaction')
print('rawKey = ' + rawKey2)
print('rawSignature = ' + rawSignature2)
print('signature = ' + bc)