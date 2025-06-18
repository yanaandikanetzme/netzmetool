from src.modules import Modules
import yaml
import psycopg2
import json

class InvoiceQROffUs():
    def __init__(self, parent):
        super().__init__(parent)

    def buildBodyQRIS(mpan, amount, nmid, mtype, mcity, mposcode, mnamelong, mcriteria, mId, terminals):
        rrn = Modules.RandomDigit(14)
        customerdata = ''
        body = '{"pan": "' + mpan + '","processingCode": "260000","transactionAmount": "' + amount + '","transmissionDateTime": "20212008160000","systemTraceAuditNumber": "123456","localTransactionDateTime": "20212008160000","settlementDate": "20212008","captureDate": "20212008","merchantType": "' + mtype + '","posEntryMode": "011","feeType": "C","feeAmount": 0,"acquirerId": "93600814","issuerId": "93600911","forwardingId": "008","rrn": "' + rrn + '","approvalCode": "121212","terminalId": "' + terminals + '","merchantId": "' + mId + '","merchantName": "' + mnamelong + '","merchantCity": "' + mcity + '","merchantCountry": "62","productIndicator": "Q001","customerData": "' + customerdata + '","merchantCriteria": "' + mcriteria + '","currencyCode": "360","postalCode": "' + mposcode + '","additionalField": "","customerPan": "9360091187569790"}'

    def buildBodyQRISAJ(mpan, amount, nmid, mtype, mcity, mposcode, mnamelong, mcriteria, mId, terminals):
        rrn = Modules.RandomDigit(14)
        customerdata = ''
        body = '{"pan": "' + mpan + '","processingCode": "260000","transactionAmount": "' + amount + '","transmissionDateTime": "20212008160000","systemTraceAuditNumber": "123456","localTransactionDateTime": "20212008160000","settlementDate": "20212008","captureDate": "20212008","merchantType": "' + mtype + '","posEntryMode": "011","feeType": "C","feeAmount": 0,"acquirerId": "93600814","issuerId": "93600911","forwardingId": "008","rrn": "' + rrn + '","approvalCode": "121212","terminalId": "' + terminals + '","merchantId": "' + mId + '","merchantName": "' + mnamelong + '","merchantCity": "' + mcity + '","merchantCountry": "62","productIndicator": "Q001","customerData": "' + customerdata + '","merchantCriteria": "' + mcriteria + '","currencyCode": "360","postalCode": "' + mposcode + '","additionalField": "","customerPan": "9360091187569790"}'


    def getQRdetailOffUs(invoice_transaction_id):
        with open('config/cred_database.json', 'r') as f:
            credentials = json.load(f)

        # Ambil informasi koneksi berdasarkan connection_key
        connection_info = credentials['Merchant'][0]

        # Konfigurasi koneksi ke PostgreSQL
        conn = psycopg2.connect(
            host=connection_info['host'],
            database=connection_info['database'],
            user=connection_info['user'],
            password=connection_info['password']
        )

        cur = conn.cursor()
        cur.execute("SELECT qm.merchant_pan,mit.total_amount,qm.merchant_type,qc.terminal_id,qm.ms_user_id,qm.merchant_name_long,qm.merchant_city,qm.merchant_criteria,qm.postal_code FROM merchant_invoice_transaction mit INNER JOIN qris_merchant qm ON qm.merchant_id=mit.merchant_id INNER JOIN qris_content qc ON mit.invoice_transaction_id=qc.qris_content_id WHERE mit.payment_method='QRIS' AND mit.status='waiting' AND mit.expired_ts> now() and mit.invoice_transaction_id='" + invoice_transaction_id + "' ORDER BY mit.created_ts DESC;")
        rows = cur.fetchall()
        outputdict = []
        for row in rows:
            print('')
        conn.close()