from src.emv.utils.logger import logger
from src.jsonParser import jsonParser
from src.emv.specifications.models import models
import json
import os 

class decode():
    def __init__(self, parent):
        super().__init__(parent)

    dir_path = os.path.dirname(os.path.realpath(__file__))

    with open(dir_path + '/' + './specifications/countries.json') as f:
        countries = json.load(f)

    with open(dir_path + '/' + './specifications/currencies.json') as f:
        currencies = json.load(f)

    with open(dir_path + '/' + './specifications/mcc_codes.json') as f:
        mcc_codes = json.load(f)

    def decode(emvString, spec='data'):
        emvObject = {}
        inputText = emvString
        while len(inputText) > 0:
            logger.debug('inputText', inputText)
            emvItem, remainingText = decode._readNext(inputText, spec)
            if spec == 'data':
                print(emvItem)
                emvItem = decode._addMetaData(emvItem)
            elif spec == 'additionalFields':
                print(emvItem)
                emvItem = decode._addMetaDataForAdditionalFields(emvItem)
            emvObject[emvItem['tag']] = emvItem
            inputText = remainingText
        return emvObject

    def _readNext(inputText, spec):
        id = inputText[:2]
        strLen = inputText[2:4]
        len = int(strLen)
        if not len:
            raise ValueError(f"Length definition expect a number. Incorrect length definition for value: {inputText}.")
        data2 = inputText[:len + 4]
        data = inputText[4:len + 4]
        emvItem = {
            'tag': id,
            'length': len,
            'name': decode._getName(spec, id),
            'data': data,
            #'rawData': data2,
        }
        remainingText = inputText[len + 4:]
        return emvItem, remainingText

    fnGetName = {
        'data': models.getName,
        'subData': models.getNameSubData,
        'additionalFields': models.getNameAdditionalFields,
    }

    def _getName(spec, id):
        return decode.fnGetName[spec](id)

    def _addMetaData(emvItem):
        if emvItem['name'] == 'Merchant Account Information':
            #emvItem['data'] = decode(emvItem['data'], 'subData')
            emvItem['data'] = jsonParser.jsonParserBeautify(json.dumps(decode.decode(emvItem['data'], 'subData')))
        if emvItem['tag'] == '52':
            mcc_code = next((item for item in decode.mcc_codes if item['mcc'] == emvItem['data']), None)
            if mcc_code:
                emvItem['data'] = f"{emvItem['data']} ({mcc_code['usda_description']})"
        if emvItem['tag'] == '53':
            currency = next((item for item in decode.currencies if item['code'] == emvItem['data']), None)
            if currency:
                emvItem['data'] = f"{emvItem['data']} ({currency['number']})"
        if emvItem['tag'] == '58':
            country = next((item for item in decode.countries if item['Code'] == emvItem['data']), None)
            if country:
                emvItem['data'] = f"{emvItem['data']} ({country['Name']})"
        return emvItem

    def _addMetaDataForAdditionalFields(emvItem):
        if emvItem['tag'] == '60':
            emvItem['data'] = decode.decode(emvItem['data'], 'paymentSpecific')
        return emvItem

    def decode(emvString, spec='data'):
        emvObject = {}
        inputText = emvString
        while len(inputText) > 0:
            #loggers.debug('inputText', inputText)
            emvItem, remainingText = decode._readNext(inputText, spec)
            if spec == 'data':
                emvItem = decode._addMetaData(emvItem)
            elif spec == 'additionalFields':
                emvItem = decode._addMetaDataForAdditionalFields(emvItem)
            emvObject[emvItem['tag']] = emvItem
            inputText = remainingText
        return emvObject

    decode

