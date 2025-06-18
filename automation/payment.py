from automation.src.base import click_element_repeatedly, wait_for_element, open_url, get_element_value_repeatedly, connect_to_postgres, send_http_request, send_http_request_mac, validate_expression, get_nested_value, get_dinamis_trx_id
from automation.database import checkAggregatorNetzme, checkHaspin, getRRNbyEventsNetzme
from automation.qr_dinamis import create_qr_dinamis
from src.modules import Modules
import yaml
import re
from src.jsonParser import jsonParser

def get_qris_secret(vendor):
    with open("config/config.yaml", "r") as yamlfile:
        data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        selection = vendor
        if selection == 'jalin_domestik':
            NetzmeKey = data[0]['Details']['QRIS']['KeyDomestik']
            urllinkQRInv = 'https://tokoapi-stg.netzme.com/qr/payment'
        elif selection == 'jalin_crossborder':
            NetzmeKey = data[0]['Details']['QRIS']['KeyCrossBorder']
            urllinkQRInv = 'https://tokoapi-stg.netzme.com/qr/cb/payment'
        elif selection == 'check_status_jalin_domestik':
            NetzmeKey = data[0]['Details']['QRIS']['KeyDomestik']
            urllinkQRInv = 'https://tokoapi-stg.netzme.com/qr/check'
        elif selection == 'check_status_cross_border':
            NetzmeKey = data[0]['Details']['QRIS']['KeyCrossBorder']
            urllinkQRInv = 'https://tokoapi-stg.netzme.com/qr/cb/check'
        elif selection == 'artajasa':
            NetzmeKey = data[0]['Details']['QRIS']['KeyCrossBorder']
            urllinkQRInv = 'https://tokoapi-stg.netzme.com/api/kare-aj/qr/payment/generic'
        elif selection == 'check_status_artajasa':
            NetzmeKey = data[0]['Details']['QRIS']['KeyCrossBorder']
            urllinkQRInv = 'https://tokoapi-stg.netzme.com/api/kare-aj/qr/check/generic'
        output = [urllinkQRInv, NetzmeKey]
        return output

def payment_invoice_qris(invoice_transaction_id, is_off_us: bool = True, show_log:bool = False, vendore=None, user_id_netzme=None):
    query2 = ("SELECT mit.invoice_id, qc.qris_content_id as invoice_transaction_id,qm.merchant_name, qc.amount_value as total_amount,qc.qr_content,qm.merchant_pan,qm.merchant_type,qm.nmid,qm.merchant_city,qm.postal_code,qm.merchant_criteria,qm.ms_user_id,qc.terminal_id,qc.qr_content FROM qris_content qc full outer join merchant_invoice_transaction mit on qc.qris_content_id = mit.invoice_transaction_id inner JOIN qris_merchant qm ON qm.merchant_id=qc.merchant_id where qc.status='open' and qc.qris_content_id = '" + invoice_transaction_id + "' ORDER BY qc.seq DESC")
    output = connect_to_postgres(query2, connection_key='Merchant', show_logs=show_log)
    selected_item_values = output
    invoice_id = selected_item_values[0]
    invoice_transaction_id = selected_item_values[1]
    merchant_name = selected_item_values[2]
    invoiceAmount = str(selected_item_values[3])
    qrcodes = selected_item_values[4]
    mpan = str(selected_item_values[5])
    mtype = selected_item_values[6]
    mId = selected_item_values[7]
    mcity = selected_item_values[8]
    mposcode = selected_item_values[9]
    mnamelong = selected_item_values[11]
    mcriteria = selected_item_values[10]
    terminals = selected_item_values[12]
    uuid = Modules.generateUUID()
    rrn = Modules.random_string(12).upper()
    costumerdata = str(invoice_id)
    datesec = Modules.DateNowSec()
    datenowtgl = Modules.generate_date()
    customerPan = '93600911' + Modules.RandomDigit(11)
    resultss = re.search('0703A0108(.*)99420002000132', qrcodes).group(1)
    invoicetrx = '0703A0108' + str(resultss) + '99420002000132' + str(invoice_transaction_id)
    qr_content = selected_item_values[13]

    if is_off_us:
        get_config = get_qris_secret(vendore)
        urllinkQRInv = get_config[0]
        NetzmeKey = get_config[1]
        selection = vendore
        issuerId = "93600911"
        if selection == 'jalin_domestik':
            bodyreq = {"pan": str(mpan), "processingCode":"260000", "transactionAmount": str(invoiceAmount), "transmissionDateTime": datesec, "systemTraceAuditNumber": "123456","localTransactionDateTime": datesec,"settlementDate": datenowtgl,"captureDate": datenowtgl,"merchantType": str(mtype),"posEntryMode": "011","feeType": "C","feeAmount": 0,"acquirerId": "93600814","issuerId": str(issuerId),"forwardingId": "008","rrn":str(rrn),"approvalCode": "121212","terminalId": str(terminals),"merchantId": str(mId),"merchantName": str(merchant_name),"merchantCity": str(mcity),"merchantCountry": "62","productIndicator": "Q001","customerData": str(costumerdata),"merchantCriteria": str(mcriteria),"currencyCode": "360","postalCode": str(mposcode),"additionalField": str(invoicetrx),"customerPan": str(customerPan)}
            headerreq = {"Content-Type": "application/json"}
        elif selection == 'jalin_crossborder':
            bodyreq = {"msgId": datesec + "123456360004123456233459","pan": str(mpan),"processingCode": "260000","transactionAmount": str(invoiceAmount),"settlementAmount": str(invoiceAmount),"cardholderAmount":"50000","transmissionDateTime": datesec,"settlementRate": "1","cardholderRate": "500","systemTraceAuditNumber": "123456","localTransactionDateTime": datesec,"settlementDate": datenowtgl,"captureDate": datenowtgl,"merchantType": str(mtype),"posEntryMode": "011","feeType": "C","feeAmount": 0,"acquirerId": "93600814","issuerId": str(issuerId),"forwardingId": "008","rrn": str(rrn),"approvalCode": "121212","terminalId": str(terminals),"merchantId": str(mId),"merchantName": str(merchant_name),"merchantCity": str(mcity),"merchantCountry": "62","productIndicator": "Q001","customerData": str(costumerdata),"merchantCriteria": str(mcriteria),"currencyCode": "764","settlementCurrCode": "764","cardholderCurrCode": "360","postalCode": str(mposcode),"additionalField": str(invoicetrx),"customerPan": "9764092212345678901","additionalData": "0002010102122654000200011893600153019"}
            headerreq = {"Content-Type": "application/json"}
        elif selection == 'check_status_jalin_domestik':
            bodyreq = {"pan": str(mpan), "processingCode":"360000", "transactionAmount": str(invoiceAmount), "transmissionDateTime": datesec, "systemTraceAuditNumber": "123456","localTransactionDateTime": datesec,"settlementDate": datenowtgl,"captureDate": datenowtgl,"merchantType": str(mtype),"posEntryMode": "011","feeType": "C","feeAmount": 0,"acquirerId": "93600814","issuerId": str(issuerId),"forwardingId": "008","rrn":str(rrn),"approvalCode": "121212","terminalId": str(terminals),"merchantId": str(mId),"merchantName": str(merchant_name),"merchantCity": str(mcity),"merchantCountry": "62","productIndicator": "Q001","customerData": str(costumerdata),"merchantCriteria": str(mcriteria),"currencyCode": "360","postalCode": str(mposcode),"additionalField": str(invoicetrx),"customerPan": str(customerPan)}
            headerreq = {"Content-Type": "application/json"}
        elif selection == 'check_status_cross_border':
            bodyreq = {"msgId": datesec + "123456360004123456233459","pan": str(mpan),"processingCode": "360000","transactionAmount": str(invoiceAmount),"settlementAmount": str(invoiceAmount),"cardholderAmount":"50000","transmissionDateTime": datesec,"settlementRate": "1","cardholderRate": "500","systemTraceAuditNumber": "123456","localTransactionDateTime": datesec,"settlementDate": datenowtgl,"captureDate": datenowtgl,"merchantType": str(mtype),"posEntryMode": "011","feeType": "C","feeAmount": 0,"acquirerId": "93600814","issuerId": str(issuerId),"forwardingId": "008","rrn": str(rrn),"approvalCode": "121212","terminalId": str(terminals),"merchantId": str(mId),"merchantName": str(merchant_name),"merchantCity": str(mcity),"merchantCountry": "62","productIndicator": "Q001","customerData": str(costumerdata),"merchantCriteria": str(mcriteria),"currencyCode": "764","settlementCurrCode": "764","cardholderCurrCode": "360","postalCode": str(mposcode),"additionalField": str(invoicetrx),"customerPan": "9764092212345678901","additionalData": "0002010102122654000200011893600153019"}
            headerreq = {"Content-Type": "application/json"}
        elif selection == 'artajasa':
            headerreq = {"Authorization":"Basic a2FyZTpkZGUyOGM3ZWRiOWQ4MDQ2OTcyYzVjMzI3N2Q5OTlhMg==", "Content-Type": "application/json"}
            bodyreq = {"acquirerId":"93600814","additionalField":str(invoicetrx),"approvalCode":"069547","captureDate":str(datenowtgl),"currencyCode":"360","customerData":str(costumerdata),"customerPan":str(customerPan),"feeAmount":0,"feeType":"C","forwardingId":"360001","issuerId":str(issuerId),"localTransactionDateTime":str(datesec),"merchantCity":str(mcity),"merchantCountry":"ID","merchantCriteria":str(mcriteria),"merchantId":str(mId),"merchantName":str(merchant_name),"merchantType":str(mtype),"msgId":str(uuid),"paidAmount":str(invoiceAmount),"pan":str(mpan),"posEntryMode":"011","postalCode":str(mposcode),"processingCode":"262000","productIndicator":"Q001","rrn":str(rrn),"rrnOrigin":str(rrn),"settlementDate":str(datenowtgl),"systemTraceAuditNumber":"033462","terminalId":str(terminals),"transactionAmount":str(invoiceAmount),"transmissionDateTime":str(datesec)}
        elif selection == 'check_status_artajasa':
            headerreq = {"Authorization":"Basic a2FyZTpkZGUyOGM3ZWRiOWQ4MDQ2OTcyYzVjMzI3N2Q5OTlhMg==", "Content-Type": "application/json"}
            bodyreq = {"acquirerId":"93600814","additionalField":str(invoicetrx),"approvalCode":"069547","captureDate":str(datenowtgl),"currencyCode":"360","customerData":str(costumerdata),"customerPan":str(customerPan),"feeAmount":0,"feeType":"C","forwardingId":"360001","issuerId":str(issuerId),"localTransactionDateTime":str(datesec),"merchantCity":str(mcity),"merchantCountry":"ID","merchantCriteria":str(mcriteria),"merchantId":str(mId),"merchantName":str(merchant_name),"merchantType":str(mtype),"msgId":str(uuid),"pan":str(mpan),"posEntryMode":"011","postalCode":str(mposcode),"processingCode":"362000","productIndicator":"Q001","rrn":str(rrn),"settlementDate":str(datenowtgl),"systemTraceAuditNumber":"033462","terminalId":str(terminals),"transactionAmount":str(invoiceAmount),"transmissionDateTime":str(datesec)}
        jsonminify = jsonParser.jsonParserMinify(bodyreq)

        rrn28digit = rrn + datenowtgl + issuerId
        send_http_request_mac('POST',url=urllinkQRInv, body_request=jsonminify, headers=headerreq, mac='sha256', key=NetzmeKey, show_logs=show_log)
        return([invoiceAmount, rrn, rrn28digit, qr_content])
    else:
        if user_id_netzme != None:
            issuerId = "93600814"
            ref_id = payment_qris_on_us(user_id_netzme, qr_content, invoiceAmount)
            rrn = getRRNbyEventsNetzme(user_id_netzme, ref_id)
            rrn28digit = rrn + datenowtgl + issuerId
            return([invoiceAmount, rrn, rrn28digit, qr_content])
        else:
            raise ValueError("Argumen user_id_netzme harus diisi")    

def payment_qris_statis(merchant_id, is_off_us:bool = True, show_log:bool = False , vendor=None, user_id_netzme=None):
    query = "SELECT * FROM qris_merchant where merchant_id = '" + merchant_id + "'"

    output = connect_to_postgres(query, connection_key='Merchant', show_logs=show_log)
    selectedItem = output
    mpan = str(selectedItem[0]) #merchant_pan
    mId = selectedItem[1] #nmid
    mercId = selectedItem[2] #merchant_id
    qr_content = selectedItem[3] #qr_content_static
    mtype = selectedItem[4] #merchant_type
    mcity = selectedItem[5] #merchant_city
    mposcode = selectedItem[6] #postal_code
    mnamelong = selectedItem[7] #merchant_name_long
    mname = selectedItem[8] #merchant_name
    mcrits = selectedItem[9] #merchant_criteria
    countrycode = selectedItem[10] #country_code
    revdom = selectedItem[11] #rev_domain
    creatby = selectedItem[12] #created_by
    createdate = selectedItem[13] #created_date
    updateby = selectedItem[14] #updated_by
    updatedat = selectedItem[15] #updated_date
    act = selectedItem[16] #active
    qrsp = selectedItem[17] #qr_static_path
    globun = selectedItem[18] #global_unique
    stats = selectedItem[19] #status
    muserid = selectedItem[20] #ms_user_id
    museridlt = selectedItem[21] #ms_user_id_lt
    nmidlt = selectedItem[22] #nmid_lt
    mnamelt = selectedItem[23] #merchant_name_lt
    mcriteria = str(mcrits)
    invoiceAmount = str('1' + Modules.RandomDigit(5))
    terminals = str('A01')
    uuid = Modules.generateUUID()
    rrn = Modules.random_string(12).upper()
    costumerdata = str('Payment QRIS statis '+ mercId + ' using Automation Off Us')
    costumerdataCS = str('CheckStatus QRIS statis '+ mercId + ' using Automation Off Us')
    datesec = Modules.DateNowSec()
    datenowtgl = Modules.generate_date()

    if is_off_us:
        get_config = get_qris_secret(vendor)
        urllinkQRInv = get_config[0]
        NetzmeKey = get_config[1]
        issuerId = '93600911'
        customerPan = '93600911' + Modules.RandomDigit(11)
        selection = vendor
        if selection == 'jalin_domestik':
            bodyreq = {"pan": str(mpan),"processingCode": "260000","transactionAmount": str(invoiceAmount),"transmissionDateTime": str(datesec),"systemTraceAuditNumber": "123456","localTransactionDateTime": str(datesec),"settlementDate": str(datenowtgl),"captureDate": str(datenowtgl),"merchantType": str(mtype),"posEntryMode": "011","feeType": "C","feeAmount": 0,"acquirerId": "93600814","issuerId": str(issuerId),"forwardingId": "008","rrn": str(rrn),"approvalCode": "121212","terminalId": str(terminals),"merchantId": str(mId),"merchantName": str(mname),"merchantCity": str(mcity),"merchantCountry": "62","productIndicator": "Q001","customerData": str(costumerdata),"merchantCriteria": str(mcriteria),"currencyCode": "360","postalCode": str(mposcode),"additionalField": "","customerPan": str(customerPan)}
        elif selection == 'jalin_crossborder':
            bodyreq = {"msgId": datesec + "123456360004123456233459","pan": str(mpan),"processingCode": "260000","transactionAmount": str(invoiceAmount),"settlementAmount": str(invoiceAmount),"cardholderAmount": "50000","transmissionDateTime": str(datesec),"settlementRate": "1","cardholderRate": "500","systemTraceAuditNumber": "123456","localTransactionDateTime": str(datesec),"settlementDate": str(datenowtgl),"captureDate": str(datenowtgl),"merchantType": str(mtype),"posEntryMode": "011","feeType": "C","feeAmount": 0,"acquirerId": "93600814","issuerId": str(issuerId),"forwardingId": "008","rrn": str(rrn),"approvalCode": "121212","terminalId": str(terminals),"merchantId": str(mId),"merchantName":str(mname),"merchantCity": str(mcity),"merchantCountry": "62","productIndicator": "Q001","customerData": str(costumerdataCS),"merchantCriteria": str(mcriteria),"currencyCode": "764","settlementCurrCode": "764","cardholderCurrCode": "360","postalCode": str(mposcode),"additionalField": "","customerPan": "9764092212345678901","additionalData": "0002010102122654000200011893600153019"}
        elif selection == 'check_status_jalin_domestik':
            bodyreq = {"pan": str(mpan), "processingCode":"360000", "transactionAmount": str(invoiceAmount),"transmissionDateTime": str(datesec),"systemTraceAuditNumber": "123456","localTransactionDateTime": str(datesec),"settlementDate": str(datenowtgl),"captureDate": str(datenowtgl),"merchantType": str(mtype),"posEntryMode": "011","feeType": "C","feeAmount": 0,"acquirerId": "93600814","issuerId": str(issuerId),"forwardingId": "008","rrn":str(rrn),"approvalCode": "121212","terminalId": str(terminals),"merchantId": str(mId),"merchantName": str(mname),"merchantCity": str(mcity),"merchantCountry": "62","productIndicator": "Q001","customerData": str(costumerdata),"merchantCriteria": str(mcriteria),"currencyCode": "360","postalCode": str(mposcode),"additionalField": "","customerPan": str(customerPan)}
        elif selection == 'check_status_cross_border':
            bodyreq = {"msgId": datesec + "123456360004123456233459","pan": str(mpan),"processingCode": "360000","transactionAmount": str(invoiceAmount),"settlementAmount": str(invoiceAmount),"cardholderAmount": "50000","transmissionDateTime": str(datesec),"settlementRate": "1","cardholderRate": "500","systemTraceAuditNumber": "123456","localTransactionDateTime": str(datesec),"settlementDate": str(datenowtgl),"captureDate": str(datenowtgl),"merchantType": str(mtype),"posEntryMode": "011","feeType": "C","feeAmount": 0,"acquirerId": "93600814","issuerId": str(issuerId),"forwardingId": "008","rrn": str(rrn),"approvalCode": "121212","terminalId": str(terminals),"merchantId": str(mId),"merchantName": str(mname),"merchantCity": str(mcity),"merchantCountry": "62","productIndicator": "Q001","customerData": str(costumerdataCS),"merchantCriteria": str(mcriteria),"currencyCode": "764","settlementCurrCode": "764","cardholderCurrCode": "360","postalCode": str(mposcode),"additionalField": "","customerPan": "9764092212345678901","additionalData": "0002010102122654000200011893600153019"}
        elif selection == 'artajasa':
            bodyreq = {"acquirerId":"93600814","additionalField":"0703A01","approvalCode":"069547","captureDate":str(datenowtgl),"currencyCode":"360","customerData":str(costumerdata),"customerPan":str(customerPan),"feeAmount":0,"feeType":"C","forwardingId":"360001","issuerId":str(issuerId),"localTransactionDateTime":str(datesec),"merchantCity":str(mcity),"merchantCountry":"ID","merchantCriteria":str(mcriteria),"merchantId":str(mId),"merchantName":str(mname),"merchantType":str(mtype),"msgId":str(uuid),"paidAmount":str(invoiceAmount),"pan":str(mpan),"posEntryMode":"011","postalCode":str(mposcode),"processingCode":"262000","productIndicator":"Q001","rrn":str(rrn),"rrnOrigin":str(rrn),"settlementDate":str(datenowtgl),"systemTraceAuditNumber":"033462","terminalId":str(terminals),"transactionAmount":str(invoiceAmount),"transmissionDateTime":str(datesec)}
        elif selection == 'check_status_artajasa':
            bodyreq = {"acquirerId":"93600814","additionalField":"0703A01","approvalCode":"069547","captureDate":str(datenowtgl),"currencyCode":"360","customerData":str(costumerdataCS),"customerPan":str(customerPan),"feeAmount":0,"feeType":"C","forwardingId":"360001","issuerId":str(issuerId),"localTransactionDateTime":str(datesec),"merchantCity":str(mcity),"merchantCountry":"ID","merchantCriteria":str(mcriteria),"merchantId":str(mId),"merchantName":str(mname),"merchantType":str(mtype),"msgId":str(uuid),"pan":str(mpan),"posEntryMode":"011","postalCode":str(mposcode),"processingCode":"362000","productIndicator":"Q001","rrn":str(rrn),"settlementDate":str(datenowtgl),"systemTraceAuditNumber":"033462","terminalId":str(terminals),"transactionAmount":str(invoiceAmount),"transmissionDateTime":str(datesec)}
        jsonminify = jsonParser.jsonParserMinify(bodyreq)
        if vendor in ['artajasa', 'check_status_artajasa']:
            headerreq = {"Authorization":"Basic a2FyZTpkZGUyOGM3ZWRiOWQ4MDQ2OTcyYzVjMzI3N2Q5OTlhMg==", "Content-Type": "application/json"}
        else:
            headerreq = {"Content-Type": "application/json"}
        rrn28digit = rrn + datenowtgl + issuerId
        send_http_request_mac('POST',url=urllinkQRInv, body_request=jsonminify, headers=headerreq, mac='sha256', key=NetzmeKey, show_logs=show_log)
        return([invoiceAmount, rrn, rrn28digit, qr_content])
    else:
        if user_id_netzme != None:
            issuerId = "93600814"
            ref_id = payment_qris_on_us(user_id_netzme, qr_content, invoiceAmount)
            rrn = getRRNbyEventsNetzme(user_id_netzme, ref_id, showlog=show_log)
            rrn28digit = rrn + datenowtgl + issuerId
            return([invoiceAmount, rrn, rrn28digit, qr_content])
        else:
            raise ValueError("Argumen user_id_netzme harus diisi")  

def payment_qris_on_us(user_id_netzme, qris_content, nominal, show_log:bool = False):
    uuid = Modules.generateUUID()
    hashpin = checkHaspin(user_id_netzme, showlog=show_log)[0]
    aggregator = checkAggregatorNetzme(user_id_netzme, showlog=show_log)[0]
    url = 'https://api-stg.netzme.com/internal/payment/aggregator/qr/pay'
    header = {"Authorization":"Basic c2t5ZmVlZDpza3lmZWVkKio=","Content-Type":"application/json"}
    bodyreq = {"requestId":uuid,"type":"aggregator_pay_qr","body":{"userId":user_id_netzme,"qrContent":qris_content,"amount":nominal,"aggregatorId":aggregator,"hashPin":hashpin}}
    response = send_http_request('POST',url=url, body_request=bodyreq, headers=header, show_logs=show_log)
    ref_id = str(get_nested_value(response, 'body.refId', show_logs=show_log))
    return ref_id

def payment_invoice_bank_transfer(invoice_transaction_id, show_log):
    query2 = f"select payment_url from merchant_invoice_transaction mit where mit.invoice_transaction_id = '{invoice_transaction_id}'"
    output = connect_to_postgres(query2, connection_key='Merchant', show_logs=show_log)
    url = output[0]
    bank_transfer_button = ("/html/body/div/main/div/div/div[2]/div[1]/section[2]/div/div/div/h3/button/span[2]/span")
    mandiri_element = ("/html/body/div/main/div/div/div[2]/div[1]/section[2]/div/div/div/div/div/ul/li[1]/button/div")
    nominal_element = ("/html/body/div/main/div/div/div[2]/div[1]/section[1]/div/div/p")
    simulate_element = ("/html/body/div/div/div/button")
    success_payment_invoice = ("/html/body/div/div[1]/div[1]/div")

    driver = open_url(url)
    click_element_repeatedly(driver, "xpath", bank_transfer_button)
    get_element_value_repeatedly(driver, "xpath", nominal_element)
    click_element_repeatedly(driver, "xpath", mandiri_element)
    click_element_repeatedly(driver, "xpath", simulate_element)
    wait_for_element(driver, "xpath", success_payment_invoice)
    driver.quit()
