import src.emv.emvqr as emvqr
import src.emv.utils.logger as logger

class supp():
    def __init__(self, parent):
        super().__init__(parent)

    enableDebugLog = lambda: globals().update({'logger': print})

    def getAll(emvString):
        try:
            result = emvqr.decode.decode(emvString)
            dicta = {}
            ress = ''
            #print('-------------------------------------------------------------------')
            if "00" in result:
                ress += "\n" + str(result['00'])
            if "01" in result:
                ress += "\n" + str(result['01'])
            if "02" in result:
                ress += "\n" + str(result['02'])
            if "03" in result:
                ress += "\n" + str(result['03'])
            if "04" in result:
                ress += "\n" + str(result['04'])
            if "05" in result:
                ress += "\n" + str(result['05'])
            if "06" in result:
                ress += "\n" + str(result['06'])
            if "07" in result:
                ress += "\n" + str(result['07'])
            if "08" in result:
                ress += "\n" + str(result['08'])
            if "09" in result:
                ress += "\n" + str(result['09'])
            if "10" in result:
                ress += "\n" + str(result['10'])
            if "11" in result:
                ress += "\n" + str(result['11'])
            if "12" in result:
                ress += "\n" + str(result['12'])
            if "13" in result:
                ress += "\n" + str(result['13'])
            if "14" in result:
                ress += "\n" + str(result['14'])
            if "15" in result:
                ress += "\n" + str(result['15'])
            if "16" in result:
                ress += "\n" + str(result['16'])
            if "17" in result:
                ress += "\n" + str(result['17'])
            if "18" in result:
                ress += "\n" + str(result['18'])
            if "19" in result:
                ress += "\n" + str(result['19'])
            if "20" in result:
                ress += "\n" + str(result['20'])
            if "21" in result:
                ress += "\n" + str(result['21'])
            if "22" in result:
                ress += "\n" + str(result['22'])
            if "23" in result:
                ress += "\n" + str(result['23'])
            if "24" in result:
                ress += "\n" + str(result['24'])
            if "25" in result:
                ress += "\n" + str(result['25'])
            if "26" in result:
                ress += "\n" + str(result['26'])

            if "27" in result:
                ress += "\n" + str(result['27'])
            if "28" in result:
                ress += "\n" + str(result['28'])
            if "29" in result:
                ress += "\n" + str(result['29'])
            if "30" in result:
                ress += "\n" + str(result['30'])
            if "31" in result:
                ress += "\n" + str(result['31'])
            if "32" in result:
                ress += "\n" + str(result['32'])
            if "33" in result:
                ress += "\n" + str(result['33'])
            if "34" in result:
                ress += "\n" + str(result['34'])
            if "35" in result:
                ress += "\n" + str(result['35'])
            if "36" in result:
                ress += "\n" + str(result['36'])
            if "37" in result:
                ress += "\n" + str(result['37'])
            if "38" in result:
                ress += "\n" + str(result['38'])
            if "39" in result:
                ress += "\n" + str(result['39'])
            if "40" in result:
                ress += "\n" + str(result['40'])
            if "41" in result:
                ress += "\n" + str(result['41'])
            if "42" in result:
                ress += "\n" + str(result['42'])
            if "43" in result:
                ress += "\n" + str(result['43'])
            if "44" in result:
                ress += "\n" + str(result['44'])
            if "45" in result:
                ress += "\n" + str(result['45'])
            if "46" in result:
                ress += "\n" + str(result['46'])
            if "47" in result:
                ress += "\n" + str(result['47'])
            if "48" in result:
                ress += "\n" + str(result['48'])
            if "49" in result:
                ress += "\n" + str(result['49'])
            if "50" in result:
                ress += "\n" + str(result['50'])
            if "51" in result:
                ress += "\n" + str(result['51'])
            if "52" in result:
                ress += "\n" + str(result['52'])
            if "53" in result:
                ress += "\n" + str(result['53'])
            if "54" in result:
                ress += "\n" + str(result['54'])
            if "55" in result:
                ress += "\n" + str(result['55'])
            if "56" in result:
                ress += "\n" + str(result['56'])
            if "57" in result:
                ress += "\n" + str(result['57'])
            if "58" in result:
                ress += "\n" + str(result['58'])
            if "59" in result:
                ress += "\n" + str(result['59'])
            if "60" in result:
                ress += "\n" + str(result['60'])
            if "61" in result:
                ress += "\n" + str(result['61'])
            if "62" in result:
                ress += "\n" + str(result['62'])
            if "63" in result:
                ress += "\n" + str(result['63'])
            if "64" in result:
                ress += "\n" + str(result['64'])
            if "65" in result:
                ress += "\n" + str(result['65'])
            if "66" in result:
                ress += "\n" + str(result['66'])
            if "67" in result:
                ress += "\n" + str(result['67'])
            if "68" in result:
                ress += "\n" + str(result['68'])
            if "69" in result:
                ress += "\n" + str(result['69'])
            if "70" in result:
                ress += "\n" + str(result['70'])
            if "71" in result:
                ress += "\n" + str(result['71'])
            if "72" in result:
                ress += "\n" + str(result['72'])
            if "73" in result:
                ress += "\n" + str(result['73'])
            if "74" in result:
                ress += "\n" + str(result['74'])
            if "75" in result:
                ress += "\n" + str(result['75'])
            if "76" in result:
                ress += "\n" + str(result['76'])
            if "77" in result:
                ress += "\n" + str(result['77'])
            if "78" in result:
                ress += "\n" + str(result['78'])
            if "79" in result:
                ress += "\n" + str(result['79'])
            if "80" in result:
                ress += "\n" + str(result['80'])
            if "81" in result:
                ress += "\n" + str(result['81'])
            if "82" in result:
                ress += "\n" + str(result['82'])
            if "83" in result:
                ress += "\n" + str(result['83'])
            if "84" in result:
                ress += "\n" + str(result['84'])
            if "85" in result:
                ress += "\n" + str(result['85'])
            if "86" in result:
                ress += "\n" + str(result['86'])
            if "87" in result:
                ress += "\n" + str(result['87'])
            if "88" in result:
                ress += "\n" + str(result['88'])
            if "89" in result:
                ress += "\n" + str(result['89'])
            if "90" in result:
                ress += "\n" + str(result['90'])
            if "91" in result:
                ress += "\n" + str(result['91'])
            if "92" in result:
                ress += "\n" + str(result['92'])
            if "93" in result:
                ress += "\n" + str(result['93'])
            if "94" in result:
                ress += "\n" + str(result['94'])
            if "95" in result:
                ress += "\n" + str(result['95'])
            if "96" in result:
                ress += "\n" + str(result['96'])
            if "97" in result:
                ress += "\n" + str(result['97'])
            if "98" in result:
                ress += "\n" + str(result['98'])
            if "99" in result:
                ress += "\n" + str(result['99'])
            beauti=ress
            return(beauti)
        except ValueError as e:
            return(str(e))

    def main():
        pass

    if __name__ == "__main__":
        main()


