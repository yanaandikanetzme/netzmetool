from src.modules import Modules

encryptionKey = "./n37tMe%^4geNt*"
passwordHashSalt = "v2rU4w7HjC"

noHP = '085600070411'
token = '46d0f1b83ac8244427fcbcf290269350eeeea343e06dd8f7541a97c23d4535d2'
sourceurl = '/api/aggregator/merchant/qr/merchant_detail?phoneNo=' + noHP
clientId = 'loketdotcom'
clearPassword = 'YyF76CN8EXhOZ55P'

class generateSignature():
    def __init__(self, parent):
            super().__init__(parent)

    def genSignaturePOST(source, token, reqtime, clearpassword, bodys):
        method = 'POST'
        plainSignature = 'path=' + source + '&method=' + method + '&token=Bearer ' + token + '&timestamp=' + reqtime + '&body=' + str(bodys)
        key = clearpassword + '-' + reqtime + '-' + 'Bearer ' + token
        hmacSignature = Modules.HashSHA256(plainSignature, key)
        return hmacSignature

    def genSignatureGET(source, token, reqtime, clearpassword):
        method = 'GET'
        body=''
        plainSignature = 'path=' + source + '&method=' + method + '&token=Bearer ' + token + '&timestamp=' + reqtime + '&body=' + str(body)
        key = clearpassword + '-' + reqtime + '-' + 'Bearer ' + token
        hmacSignature = Modules.HashSHA256(plainSignature, key)
        return hmacSignature

    def FunBuildSignMethod(method, source, token, reqtime, clearpassword, *args):
        if method == 'POST':
            plainSignature = 'path=' + source + '&method=' + method + '&token=Bearer ' + token + '&timestamp=' + reqtime + '&body=' + str(args)
            key = clearpassword + '-' + reqtime + '-' + 'Bearer ' + token
            hmacSignature = Modules.HashSHA256(plainSignature, key)
            return hmacSignature
        elif method == 'GET':
            body=''
            plainSignature = 'path=' + source + '&method=' + method + '&token=Bearer ' + token + '&timestamp=' + reqtime + '&body=' + str(body)
            key = clearpassword + '-' + reqtime + '-' + 'Bearer ' + token
            hmacSignature = Modules.HashSHA256(plainSignature, key)
            return hmacSignature

    def genPlainSign(source, token, reqtime, method, body):
        plainSignature = 'path=' + source + '&method=' + method + '&token=Bearer ' + token + '&timestamp=' + reqtime + '&body=' + str(body)
        return plainSignature

    def genKey(clearpassword, reqtime, token):
        key = clearpassword + '-' + reqtime + '-' + 'Bearer ' + token
        return key

    def getautBasic(clientId, clearPassword):
        headerAuth = clientId + ':' + clearPassword
        return (Modules.base64Encode(headerAuth))

    def genPINToko(clearPin, salt, userName):
        keyz = salt + userName
        pinOut = Modules.HashSHA256(clearPin, keyz)
        return pinOut

    def genSignatureAPIGet(source, token, reqtime, method, body, clearPassword):
        listSignature = []
        plains = generateSignature.genPlainSign(source,token,reqtime,method,body)
        signature = generateSignature.genSignatureGET(source, token, reqtime, clearPassword)
        key = generateSignature.genKey(clearPassword,reqtime,token)
        listSignature += [plains]
        listSignature += [key]
        listSignature += [signature]
        return listSignature

    def genSignatureAPIPost(source, token, reqtime, method, body, clearPassword):
        listSignature = []
        tbody = Modules.JsonRemoveWhitespace(body)
        signature = generateSignature.genSignaturePOST(source, token, reqtime, clearPassword, tbody)
        plains = generateSignature.genPlainSign(source,token,reqtime,method,tbody)
        key = generateSignature.genKey(clearPassword,reqtime,token)
        listSignature += [plains]
        listSignature += [key]
        listSignature += [signature]
        return listSignature

    def FunGenerateSignature(method, token, clearPassword, *args):
        reqtime = Modules.current_milli_time()
        if method == 'Merchant Detail':
            PhoneNumber = args[0]
            source = "/api/aggregator/merchant/qr/merchant_detail?phoneNo=" + PhoneNumber
            method = "GET"
            tbody = ''

            listSignature = []
            #tbody = Modules.JsonRemoveWhitespace(body)
            signature = generateSignature.genSignatureGET(source, token, reqtime, clearPassword)
            plains = generateSignature.genPlainSign(source,token,reqtime,method,tbody)
            key = generateSignature.genKey(clearPassword,reqtime,token)
            tokenBearer = "Bearer " + token
            listSignature += [key]
            listSignature += [plains]
            listSignature += [source]
            listSignature += [reqtime]
            listSignature += [tokenBearer]
            listSignature += [signature]
            return listSignature
        if method == 'Inquiry Withdraw':
            source = "/api/aggregator/merchant/qr/withdraw/inquiry"
            method = "POST"
            bod = args[0]
            tbody = Modules.JsonRemoveWhitespace(bod)
            signature = generateSignature.FunBuildSignMethod(method, source, token, reqtime, clearPassword, tbody)
            plains = generateSignature.genPlainSign(source,token,reqtime,method,tbody)
            key = generateSignature.genKey(clearPassword,reqtime,token)
            tokenBearer = "Bearer " + token
            listSignature += [key]
            listSignature += [plains]
            listSignature += [source]
            listSignature += [reqtime]
            listSignature += [tokenBearer]
            listSignature += [signature]
            return listSignature

