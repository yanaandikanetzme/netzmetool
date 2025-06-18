from src.emv.utils.checksumUtils import checksumUtils
from src.emv.decoder import decode
from src.emv.utils.logger import logger

class emvqr():
    def __init__(self, parent):
        super().__init__(parent)

    enableDebugLog = lambda: globals().update({'logger': print})

    def decode(emvString):
        try:
            return emvqr._decode(emvString, 'data')
        except ValueError as e:
                print(str(e))

    def decodeSubData(emvString):
        return emvqr._decode(emvString, 'subData')

    def decodeAdditionalFields(emvString):
        return emvqr._decode(emvString, 'additionalFields')

    def decodePaymentSpecific(emvString):
        return emvqr._decode(emvString, 'paymentSpecific')

    def _decode(emvString, spec):
        try:
            if not checksumUtils.validateChecksum(emvString):
                a = 'Not Support EMV'
                return (a)#raise Exception('checksum validation failed.')
            emvObject = decode.decode(emvString, spec)
            return emvObject
        except ValueError as e:
            print(str(e))

    __all__ = [
        'decode',
        'decodeSubData',
        'decodeAdditionalFields',
        'decodePaymentSpecific',
        'enableDebugLog',
    ]


