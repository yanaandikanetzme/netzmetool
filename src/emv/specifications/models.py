import json
import os

class models():
    def __init__(self, parent):
        super().__init__(parent)

    dir_path = os.path.dirname(os.path.realpath(__file__))

    with open(dir_path + '/' + '_schema.json') as f:
        dataObjectsSchema = json.load(f)

    with open(dir_path + '/' + '_schemaSubData.json') as f:
        subDataObjectsSchema = json.load(f)

    with open(dir_path + '/' + '_schemaAdditionalFields.json') as f:
        additionalFieldsObjectsSchema = json.load(f)

    with open(dir_path + '/' + '_schemaPaymentSpecific.json') as f:
        paymentSpecificObjectsSchema = json.load(f)

    def getName(stringId):
        dataObject = models.dataObjectsSchema.get(stringId)
        if not dataObject:
            id = int(stringId)
            if 2 <= id <= 51:
                dataObject = models.dataObjectsSchema['02-51']
            elif 65 <= id <= 79:
                dataObject = models.dataObjectsSchema['65-79']
            elif 80 <= id <= 99:
                dataObject = models.dataObjectsSchema['80-99']
        return models._getName(dataObject)

    def getNameSubData(stringId):
        dataObject = models.subDataObjectsSchema.get(stringId)
        return models._getName(dataObject)

    def getNameAdditionalFields(stringId):
        dataObject = models.additionalFieldsObjectsSchema.get(stringId)
        if not dataObject:
            id = int(stringId)
            if 10 <= id <= 49:
                dataObject = models.additionalFieldsObjectsSchema['10-49']
            elif 50 <= id <= 99:
                dataObject = models.additionalFieldsObjectsSchema['50-99']
        return models._getName(dataObject)

    def getNamePaymentSpecific(stringId):
        dataObject = models.paymentSpecificObjectsSchema.get(stringId)
        if not dataObject:
            id = int(stringId)
            if 1 <= id <= 99:
                dataObject = models.paymentSpecificObjectsSchema['01-99']
        return models._getName(dataObject)

    def _getName(dataObject):
        return dataObject['name'] if dataObject else None


