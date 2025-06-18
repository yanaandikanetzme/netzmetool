#lokasi file src/dispute.py
from datetime import datetime

class dispute():
    def __init__(self, parent):
        super().__init__(parent)

    def ArtajasaTemplate(Listdata, totalFightback, totalChargeback):
        try:
            tglReport = str(datetime.now().strftime("%d/%m/%y"))
            jamReport = str(datetime.now().strftime("%H:%M:%S"))
            jumlahData = str(len(Listdata))
            nilai1 = float(str(totalFightback).replace(",", ""))
            nilai2 = float(str(totalChargeback).replace(",", ""))
            totalDispute = str("{:,.2f}".format(nilai1 + nilai2))
            totalChargeback = str("{:,.2f}".format(nilai2))
            totalFightback = str("{:,.2f}".format(nilai1))
            templateHeaderArtajasa = """                                                                                                 	LAPORAN TRANSAKSI HAK DISPUTE QR                                                                                                                            
                                                                                                            PT. ARTAJASA PEMBAYARAN ELEKTRONIS                                                                                                                               """
            
            templateAwalArtajasa = """No Report  : RKNARTA                                                                                                                                                                                           Frekwensi          : HARIAN                      
Layanan    : Interkoneksi QR                                                                                                                                                                                   Tanggal Report     : """ + tglReport + """                    
Nama Bank  : NETZME                                                                                                                                                                                            Tanggal Settlement : """ + tglReport + """                    
Kode       : 00093600814                                                                                                                                                                                       Waktu Report       : """ + jamReport + """                    
Posisi     : HAK                                                                                                                                                                                               Halaman            : 1 dari 1                    
                                                                                                                                                                                                                                                                                            
No.    Trx_Code Tanggal_Trx Jam_Trx  Ref_No       Trace_No Terminal_ID      Merchant_PAN        ACQUIRER    ISSUER      Customer_PAN        Nominal          Merchant_Category Merchant_Criteria Response_Code Merchant_Name_&_Location                 Convenience_Fee Interchange_Fee  Reason_Code   Dispute_Tran_Code  Dispute_Amount  Fee_Return      Dispute_Net_Amount
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
"""

            templateAkhirArtajasa = """----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
END OF PAGES 
TOTAL TRANSAKSI DISPUTE	                                    :                         """+jumlahData+"""                                                                                                                                                                                   
NET HAK DISPUTE        	                                    :                """+str(totalFightback)+"""                                                                                                                                                                                   
NET KEWAJIBAN DISPUTE  	                                    :               """+str(totalChargeback)+"""                                                                                                                                                                                   
TOTAL NET DISPUTE AMOUNT                                    :               """+totalDispute+"""                                                                                                                                                                                   

    """

            output = templateHeaderArtajasa + '\n' + templateAwalArtajasa + '\n'.join(Listdata)+ '\n' + templateAkhirArtajasa
            return (output)
        except IndexError as e:
            print(f"{e}")


    def JalinTemplate(Listdata, totalFightback, totalChargeback):
        try:
            tglReport = str(datetime.now().strftime("%d/%m/%y"))
            jamReport = str(datetime.now().strftime("%H:%M:%S"))
            jumlahData = str(len(Listdata))
            nilai1 = float(str(totalFightback).replace(",", ""))
            nilai2 = float(str(totalChargeback).replace(",", ""))
            totalDispute = str("{:,.2f}".format(nilai1 + nilai2))
            totalChargeback = str("{:,.2f}".format(nilai2))
            totalFightback = str("{:,.2f}".format(nilai1))
            templateHeaderJalin = """                                                                                                  LAPORAN TRANSAKSI DISPUTE                                                                                                                                     
                                                                                                    PT JALIN PEMBAYARAN NUSANTARA"""
            templateAwalJalin = """No Report  : RKNJLIN0814                                                                                                                                                                                       Frekwensi          : HARIAN                      
Layanan    : Interkoneksi QR                                                                                                                                                                                                Tanggal Report     : """+tglReport+"""                    
Prinsipal  : JALIN                                                                                                                                                                                             Tanggal Settlement : """+tglReport+"""                    
Kode       : 360004                                                                                                                                                                                            Waktu Report       : """+jamReport+"""                   
Posisi     : 0814/ACQ                                                                                                                                                                                          Halaman            : 0001 dari 000001                         
                                                                                                                                                                                                                                                                    
No.    Trx_Code Tanggal_Trx Jam_Trx  Ref_No       Trace_No Terminal_ID      Merchant_PAN        Acquirer    Issuer      Customer_PAN        Nominal          Merchant_Category Merchant_Criteria Response_Code Merchant_Name_&_Location                 Convenience_Fee Interchange_Fee Dispute_Tran_Code   Dispute_Amount    Fee_Return        Dispute_Net_Amount  Registration_Number 
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
"""
            templateAkhirJalin = """---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
End of Pages                                                                                                                                                                                                                                                    
TOTAL TRANSAKSI DISPUTE                                          :                         """+jumlahData+"""                                                                                                                                                                            
TOTAL NET DISPUTE AMOUNT (v)                                     :               """+totalDispute+"""
TOTAL PAYMENT CREDIT                                             :                    184039                                                                                                                                                                            
TOTAL AMOUNT PAYMENT CREDIT (w)                                  :         22,606,037,222.00                                                                                                                                                                            
TOTAL INTERCHANGE FEE PAYMENT CREDIT (x)                         :            -86,972,244.31                                                                                                                                                                            
TOTAL REFUND                                                     :                         0                                                                                                                                                                            
TOTAL AMOUNT REFUND (y)                                          :                      0.00                                                                                                                                                                            
TOTAL INTERCHANGE FEE REFUND (z)                                 :                      0.00                                                                                                                                                                            
TOTAL SETTLEMENT AMOUNT (v+w+x+y+z)                              :         22,518,317,207.88                                                                                                                                                                            
    """
            output = templateHeaderJalin + '\n' + templateAwalJalin + '\n'.join(Listdata)+ '\n' + templateAkhirJalin
            return (output)
        except IndexError as e:
            print(f"{e}")