# app/tabs/open_api_subtabs/netzme_open_api_subtabs/netzme_non_snap_tab.py
from tkinter import *
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from src.modules import Modules
from app.tabs.popup import ResponseOpenAPI
import json
import os
#from config.configs import Configs
from app.custom.custom_text import CustomText
from src.generateSignature import generateSignature
from src.jsonParser import jsonParser
from app.custom.custom_treeview import CustomTreeview

class NetzmeNonSnapTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        # Add your elements here

        self.y20 = tk.StringVar()
        variables = [self.y20]
        functions = [self.on_field_NOAcb2change]
        for variable, function in zip(variables, functions):
            variable.trace_add('write', lambda *args, func=function: func())

        self.NOAlbl1 = tk.Label(self,text="AggregatorId")
        self.NOAcb1 = ttk.Combobox(self, width=55)
        self.NOAcb1['values'] = Modules.getAllAggregatorNetzme()
        self.NOAcb1.config(state='readonly')
        #self.NOAcb1.current(currentclientnetzme)
        self.NOAcb1.bind("<<ComboboxSelected>>", self.getClearPasswordNetzme)
    
        self.NOAlbl2 = tk.Label(self,text="ClearPassword")
        self.NOAEn1 = tk.Entry(self)

        self.NOAlbl3 = tk.Label(self,text="Auth Token")
        self.NOAEn2 = tk.Entry(self, width=55)
        self.NOAEn2.config(state='normal')
        #self.NOAEn2.delete(0, END)
        #self.NOAEn2.insert(tk.END, str(tokenmerch))

        self.NOAlbluserId = tk.Label(self,text="User ID")
        #print(userIdnetzme)
        self.NOAEnuserId = tk.Entry(self)
        self.NOAEnuserId.bind('<KeyRelease>', self.NetzmeOpenAPIBody)
        #self.NOAEnuserId.delete(0, END)
        #self.NOAEnuserId.insert(tk.END, str(userIdnetzme))

        self.NOAlbl5 = tk.Label(self,text="Endpoint")
        self.NOAcb2 = ttk.Combobox(self, textvariable=self.y20, width=55)
        self.NOAcb2['values'] = ['Authorization','Get Account Status','Get Balance',
                                 'Get History','Get Fixed Topup VA','QRIS Get Detail','Get Detail Transaction']
        self.NOAcb2.config(state='readonly')

        self.NOABtn1 = ttk.Button(self, text="Add", command=self.newpopup)
        self.NOABtn2 = ttk.Button(self, text="Send", command=self.start_thread_connection)
        self.NOABtn3 = ttk.Button(self, text="Check", command=self.CheckTokenNetzme)
        self.NOABtn4 = ttk.Button(self, text="Test", command=self.NetzmeOpenAPISign)
        self.NOABtn5 = ttk.Button(self, text="Create Curl", command=self.NetzmeOpenAPICreateCurl)

        self.NOAlbl6 = tk.Label(self,text="Output")
        self.NOAlbl7 = tk.Label(self,text="Raw Key")
        self.NOAEn4 = tk.Entry(self, width=55)
        self.NOAEn4.config(state='normal')

        self.NOAlbl8 = tk.Label(self,text="Raw Signature")
        self.NOAEn5 = tk.Entry(self, width=55)
        self.NOAEn5.config(state='normal')

        self.NOAlbl9 = tk.Label(self,text="Source")
        self.NOAEn6 = tk.Entry(self, width=55)
        self.NOAEn6.config(state='normal')
        
        self.NOAlbl10 = tk.Label(self,text="Signature")
        self.NOAEn7 = tk.Entry(self, width=55)
        self.NOAEn7.config(state='normal')

        self.NOAlbl11 = tk.Label(self,text="Request Time")
        self.NOAEn8 = tk.Entry(self, width=55)
        self.NOAEn8.config(state='normal')

        self.NOAlbl12 = tk.Label(self,text="Authorization")
        self.NOAEn9 = tk.Entry(self, width=55)
        self.NOAEn9.config(state='normal')

        self.NOAlbl13 = tk.Label(self,text="Body")
        self.NOABody = CustomText(self, width=100, height=16)
        #self.NOABody.bind("<<TextModified>>", self.NetzmeOpenAPISign)
        
        self.NOAlbl14 = tk.Label(self,text="QR Content")
        self.NOAlbl15 = tk.Label(self,text="Ref Id")

        self.NOAQR = tk.Entry(self)
        self.NOAQR.config(state='normal')
        self.NOAQR.bind('<KeyRelease>', self.NetzmeOpenAPIBody)
        #self.NOAQR.delete(0, END)
        #self.NOAQR.insert(tk.END, str(netzmeqr))

        self.NOARefId = tk.Entry(self)
        self.NOARefId.config(state='normal')
        self.NOARefId.bind('<KeyRelease>', self.NetzmeOpenAPIBody)
        #self.NOARefId.delete(0, END)
        #self.NOARefId.insert(tk.END, str(norefid))
        self.NOAcb2.bind("<<ComboboxSelected>>", self.NetzmeOpenAPIBody)
        self.loadAwal()

    def loadAwal(self):
        self.NetzmeOpenAPIBody()
        self.getClearPasswordNetzme()

    def on_field_NOAcb2change(self):
        self.NetzmeOpenAPIBody()

    def getClearPasswordNetzme(self, *args):
        aggId = self.NOAcb1.get()
        #print(aggId)
        if not self.NOAcb1.get() == "":
            self.NOAEn1.config(state='normal')
            getstr = Modules.searchclearPassByaggregatorNetzme(aggId)[0]
            self.NOAEn1.delete(0, END)
            self.NOAEn1.insert(tk.END, str(getstr))

    def NetzmeOpenAPIBody(self, *args):
        #print('NetzmeOpenAPIBody')
        self.showhideNetzmeOpenAPIElement()
        #['Authorization','Get Account Status','Get Balance','Get History','Get Fixed Topup VA','QRIS Get Detail','Get Detail Transaction']
        currentselected = self.NOAcb2.get()
        userId = self.NOAEnuserId.get()
        guid = Modules.generateUUID()
        qrcontent = self.NOAQR.get()
        refIdx = self.NOARefId.get()
        if currentselected == 'Authorization':
            #Auth token
            source = '/oauth/merchant/accesstoken'
            method = "POST"
            body = {"grant_type":"client_credentials"}
            json_formatted_str = json.dumps(body, indent=4)
            self.NOABody.delete('1.0', tk.END)
            self.NOABody.insert(tk.END, str(json_formatted_str))
        elif currentselected == 'Get Account Status':
            body = ""
            self.NOABody.delete('1.0', tk.END)
            self.NOABody.insert(tk.END, str(body))
        elif currentselected == 'Get Balance':
            body = ""
            self.NOABody.delete('1.0', tk.END)
            self.NOABody.insert(tk.END, str(body))
        elif currentselected == 'Get History':
            body = {"requestId":guid,"type":"aggregator_transaction_history","body":{"userId":str(userId),"limit":20,"seqId":0}}
            json_formatted_str = json.dumps(body, indent=4)
            self.NOABody.delete('1.0', tk.END)
            self.NOABody.insert(tk.END, str(json_formatted_str))
        elif currentselected == 'Get Fixed Topup VA':
            body = ""
            self.NOABody.delete('1.0', tk.END)
            self.NOABody.insert(tk.END, str(body))
        elif currentselected == 'QRIS Get Detail':
            body = {"requestId":guid,"type":"aggregator_scan_qr","body":{"userId":str(userId),"qrContent":qrcontent}}
            json_formatted_str = json.dumps(body, indent=4)
            self.NOABody.delete('1.0', tk.END)
            self.NOABody.insert(tk.END, str(json_formatted_str))
        elif currentselected == 'Get Detail Transaction':
            body = {"requestId":guid,"type":"aggregator_transaction","body":{"userId":str(userId),"refId":refIdx}}
            json_formatted_str = json.dumps(body, indent=4)
            self.NOABody.delete('1.0', tk.END)
            self.NOABody.insert(tk.END, str(json_formatted_str))
        self.NetzmeOpenAPISign()

    def NetzmeOpenAPISign(self,*args):
        userId = self.NOAEnuserId.get()
        currentselected = self.NOAcb2.get()
        clientId = self.NOAcb1.get()
        clearPassword = self.NOAEn1.get()
        token = self.NOAEn2.get()
        tokenBearer = "Bearer " + token
        reqtime = Modules.current_milli_time()
        bod = str(self.NOABody.get("1.0",'end-1c'))
        if currentselected == 'Get Account Status':
            source = "/aggregator/cdd/status?userid=" + userId
            method = "GET"
            body = ''
            self.NOABody.delete('1.0', tk.END)
            self.NOABody.insert(tk.END, str(body))
            plains = generateSignature.genPlainSign(source,token,reqtime,method,body)
            signature = generateSignature.genSignatureGET(source, token, reqtime, clearPassword)
            key = generateSignature.genKey(clearPassword,reqtime,token)
            self.changeOpenAPInetzmeEntry(key, plains, source, signature, reqtime, tokenBearer)
        elif currentselected == 'Get Balance':
            source = "/payment/aggregator/balance?userId=" + userId
            method = "GET"
            body = ''
            self.NOABody.delete('1.0', tk.END)
            self.NOABody.insert(tk.END, str(body))
            plains = generateSignature.genPlainSign(source,token,reqtime,method,body)
            signature = generateSignature.genSignatureGET(source, token, reqtime, clearPassword)
            key = generateSignature.genKey(clearPassword,reqtime,token)
            self.changeOpenAPInetzmeEntry(key, plains, source, signature, reqtime, tokenBearer)
        elif currentselected == 'Get History':
            source = "/payment/aggregator/history"
            method = "POST"
            tbody = Modules.JsonRemoveWhitespace(bod)
            signature = generateSignature.genSignaturePOST(source, token, reqtime, clearPassword, tbody)
            plains = generateSignature.genPlainSign(source,token,reqtime,method,tbody)
            key = generateSignature.genKey(clearPassword,reqtime,token)
            self.changeOpenAPInetzmeEntry(key, plains, source, signature, reqtime, tokenBearer)
        elif currentselected == 'Get Fixed Topup VA':
            source = "/payment/aggregator/fixed_va?userId=" + userId
            method = "GET"
            body = ''
            self.NOABody.delete('1.0', tk.END)
            self.NOABody.insert(tk.END, str(body))
            plains = generateSignature.genPlainSign(source,token,reqtime,method,body)
            signature = generateSignature.genSignatureGET(source, token, reqtime, clearPassword)
            key = generateSignature.genKey(clearPassword,reqtime,token)
            self.changeOpenAPInetzmeEntry(key, plains, source, signature, reqtime, tokenBearer)
        elif currentselected == 'QRIS Get Detail':
            source = "/payment/aggregator/qr/scan"
            method = "POST"
            tbody = Modules.JsonRemoveWhitespace(bod)
            signature = generateSignature.genSignaturePOST(source, token, reqtime, clearPassword, tbody)
            plains = generateSignature.genPlainSign(source,token,reqtime,method,tbody)
            key = generateSignature.genKey(clearPassword,reqtime,token)
            self.changeOpenAPInetzmeEntry(key, plains, source, signature, reqtime, tokenBearer)
        elif currentselected == 'Get Detail Transaction':
            source ="/payment/aggregator/transaction"
            method = "POST"
            tbody = Modules.JsonRemoveWhitespace(bod)
            signature = generateSignature.genSignaturePOST(source, token, reqtime, clearPassword, tbody)
            plains = generateSignature.genPlainSign(source,token,reqtime,method,tbody)
            key = generateSignature.genKey(clearPassword,reqtime,token)
            self.changeOpenAPInetzmeEntry(key, plains, source, signature, reqtime, tokenBearer)


    def NetzmeOpenAPIHit(self,*args):
        currentselected = self.NOAcb2.get()
        baseurl = 'https://api-stg.netzme.com'
        clientId = self.NOAcb1.get()
        clearPassword = self.NOAEn1.get()
        token = self.NOAEn2.get()
        tokenBearer = "Bearer " + token
        signature = str(self.NOAEn7.get())
        reqtime = str(self.NOAEn8.get())
        userId = self.NOAEnuserId.get()
        bod = jsonParser.jsonParserMinify(self.NOABody.get("1.0",'end-1c'))

        if currentselected == 'Authorization':
            source = '/oauth/token/accesstoken'
            authtoken = 'Basic ' + generateSignature.getautBasic(clientId,clearPassword)
            headerreq = {"Content-Type": "application/json","Authorization":authtoken}
        else:
            headerreq = {"Content-Type": "application/json","Signature":signature,"Request-Time":reqtime,"Authorization":tokenBearer,"Client-Id":clientId}
            if currentselected == 'Get Account Status':
                source = "/aggregator/cdd/status?userid=" + userId
            elif currentselected == 'Get Balance':
                source = "/payment/aggregator/balance?userId=" + userId
            elif currentselected == 'Get History':
                source = "/payment/aggregator/history"
            elif currentselected == 'Get Fixed Topup VA':
                source = "/payment/aggregator/fixed_va?userId=" + userId
            elif currentselected == 'QRIS Get Detail':
                source = "/payment/aggregator/qr/scan"
            elif currentselected == 'Get Detail Transaction':
                source ="/payment/aggregator/transaction"

        response = Modules.make_http_request(url=baseurl+source, headers=headerreq, body_request=bod)
        self.NOABtn2.config(state=tk.NORMAL)
        if response:
            http_status_code = response[0]
            response_message = response[1]
            response_message = jsonParser.jsonParserBeautify(response_message)
            msgbox = f"HTTP Status Code: {http_status_code}\nResponse Message: {response_message}"
            ResponseOpenAPI(msgbox)
            if currentselected == "Authorization":
                strings = Modules.get_value_from_json(response_message, 'access_token')
                if strings:
                    self.NOAEn2.config(state='normal')
                    self.NOAEn2.delete(0, tk.END)
                    self.NOAEn2.insert(0, strings)


    def NetzmeOpenAPICreateCurl(self,*args):
        currentselected = self.NOAcb2.get()
        baseurl = 'https://api-stg.netzme.com'
        clientId = self.NOAcb1.get()
        clearPassword = self.NOAEn1.get()
        token = self.NOAEn2.get()
        tokenBearer = "Bearer " + token
        signature = str(self.NOAEn7.get())
        reqtime = str(self.NOAEn8.get())
        userId = self.NOAEnuserId.get()
        RequestBody = jsonParser.jsonParserMinify(self.NOABody.get("1.0",'end-1c'))

        if currentselected == 'Authorization':
            source = '/oauth/token/accesstoken'
            authtoken = 'Basic ' + generateSignature.getautBasic(clientId,clearPassword)
            headerreq = {"Content-Type": "application/json","Authorization":authtoken}
        else:
            headerreq = {"Content-Type": "application/json","Signature":signature,"Request-Time":reqtime,"Authorization":tokenBearer,"Client-Id":clientId}
            if currentselected == 'Get Account Status':
                source = "/aggregator/cdd/status?userid=" + userId
            elif currentselected == 'Get Balance':
                source = "/payment/aggregator/balance?userId=" + userId
            elif currentselected == 'Get History':
                source = "/payment/aggregator/history"
            elif currentselected == 'Get Fixed Topup VA':
                source = "/payment/aggregator/fixed_va?userId=" + userId
            elif currentselected == 'QRIS Get Detail':
                source = "/payment/aggregator/qr/scan"
            elif currentselected == 'Get Detail Transaction':
                source ="/payment/aggregator/transaction"
        output = Modules.generate_curl_command(url=baseurl+source, headers = headerreq, payload=RequestBody)
        ResponseOpenAPI(output)

    def changeOpenAPInetzmeEntry(self, key, plains, source, signature, reqtime, tokenBearer):
        self.NOAEn4.config(state='normal')
        self.NOAEn4.delete(0, END)
        self.NOAEn4.insert(tk.END, str(key))
        self.NOAEn5.config(state='normal')
        self.NOAEn5.delete(0, END)
        self.NOAEn5.insert(tk.END, str(plains))
        self.NOAEn6.config(state='normal')
        self.NOAEn6.delete(0, END)
        self.NOAEn6.insert(tk.END, str(source))
        self.NOAEn7.config(state='normal')
        self.NOAEn7.delete(0, END)
        self.NOAEn7.insert(tk.END, str(signature))
        self.NOAEn8.config(state='normal')
        self.NOAEn8.delete(0, END)
        self.NOAEn8.insert(tk.END, str(reqtime))
        self.NOAEn9.config(state='normal')
        self.NOAEn9.delete(0, END)
        self.NOAEn9.insert(tk.END, str(tokenBearer))

    def showhideNetzmeOpenAPIElement(self, *args):
        widgets = [self.NOAlbl1, self.NOAcb1, self.NOABtn5, self.NOABtn2, self.NOAlbl2, self.NOAEn1,
                self.NOAlbl3, self.NOAEn2, self.NOAlbluserId, self.NOAEnuserId, self.NOAlbl5, self.NOAcb2,
                self.NOAlbl6, self.NOAlbl7, self.NOAEn4, self.NOAlbl8, self.NOAEn5, self.NOAlbl9, self.NOAEn6,
                self.NOAlbl10, self.NOAEn7, self.NOAlbl11, self.NOAEn8, self.NOAlbl12, self.NOAEn9, self.NOAlbl13,
                self.NOABody, self.NOAlbl14, self.NOAQR, self.NOAlbl15, self.NOARefId]

        for widget in widgets:
            widget.place(x=17500, y=3)

        currentselected = self.NOAcb2.get()
        self.NOABtn5.place(x=650, y=3)

        if currentselected == 'Authorization':
            self.NOAlbl1.place(x=3, y=3)
            self.NOAcb1.place(x=110, y=3)
            self.NOABtn2.place(x=850, y=3)
            self.NOAlbl2.place(x=3, y=33)
            self.NOAEn1.place(x=110, y=33)
            self.NOAEn1.config(state='normal')
            self.NOAlbl3.place(x=3, y=63)
            self.NOAEn2.place(x=110, y=63)
            self.NOAEn2.config(state='normal')
            self.NOABtn3.place(x=650, y=63)
            self.NOAlbl5.place(x=3, y=93)
            self.NOAcb2.place(x=110, y=93)
            self.NOAlbl13.place(x=3, y=343)
            self.NOABody.place(x=110, y=343)

        else:
            self.NOAlbl1.place(x=3, y=3)
            self.NOAcb1.place(x=110, y=3)
            self.NOABtn2.place(x=850, y=3)
            self.NOAlbl2.place(x=3, y=33)
            self.NOAEn1.place(x=110, y=33)
            self.NOAEn1.config(state='normal')
            self.NOAlbl3.place(x=3, y=63)
            self.NOAEn2.place(x=110, y=63)
            self.NOAEn2.config(state='normal')
            self.NOABtn3.place(x=650, y=63)
            self.NOAlbl5.place(x=3, y=93)
            self.NOAcb2.place(x=110, y=93)
            self.NOAlbl6.place(x=3, y=123)
            self.NOAlbl7.place(x=3, y=153)
            self.NOAEn4.place(x=110, y=153)
            self.NOAEn4.config(state='normal')
            self.NOAlbl8.place(x=3, y=183)
            self.NOAEn5.place(x=110, y=183)
            self.NOAEn5.config(state='normal')
            self.NOAlbl9.place(x=3, y=213)
            self.NOAEn6.place(x=110, y=213)
            self.NOAEn6.config(state='normal')
            self.NOAlbl10.place(x=3, y=243)
            self.NOAEn7.place(x=110, y=243)
            self.NOAEn7.config(state='normal')
            self.NOAlbl11.place(x=3, y=283)
            self.NOAEn8.place(x=110, y=283)
            self.NOAEn8.config(state='normal')
            self.NOAlbl12.place(x=3, y=313)
            self.NOAEn9.place(x=110, y=313)
            self.NOAEn9.config(state='normal')
            self.NOAlbl13.place(x=3, y=343)
            self.NOABody.place(x=110, y=343)
            self.NOAlbluserId.place(x=750, y=63)
            self.NOAEnuserId.place(x=840, y=63)
            self.NOAEnuserId.config(state='normal')

            if currentselected == 'QRIS Get Detail':
                self.NOAlbl14.place(x=750, y=93)
                self.NOAQR.place(x=840, y=93)
            elif currentselected == 'Get Detail Transaction':
                self.NOAlbl15.place(x=750, y=93)
                self.NOARefId.place(x=840, y=93)

    def CheckTokenNetzme(self):
        try:
            aggregatorId = self.NOAcb1.get()
            SQL = "select*from user_token_auth where user_name = '" + aggregatorId + "'"
            exeQuery = Modules.ConnectDBNetzreg(SQL)
            for row in exeQuery:
                self.NOAEn2.config(state='normal')
                self.NOAEn2.delete(0, tk.END)
                self.NOAEn2.insert(tk.END, str(row[4]))
                #self.updateFileConfig()
                #[['M_9RyYNaUH', '+6281329288484']]
        except ValueError as e:
            ResponseOpenAPI(str(e))

    def onDeleteChild(self, w):
        w.destroy()
    
    def start_thread_connection(self):
        self.NOABtn2.config(state=tk.DISABLED)
        # Memulai thread baru untuk koneksi database
        thread = threading.Thread(target=self.NetzmeOpenAPIHit)
        thread.start()

    def newpopup(self):
        dialog = Toplevel(self)
        dialog.wm_title("Manage Aggregator")
        dialog.geometry('500x500')
        dialog.wm_transient(self)
        dialog.wm_protocol("WM_DELETE_WINDOW", lambda: self.onDeleteChild(dialog))
        columnsAggre = ('aggregatorId', 'clearPassword')
        self.treeAggregator = CustomTreeview(dialog, columns=columnsAggre, show='headings')
        self.treeAggregator.place(relx=0.01, rely=0.1, width=400, height=400)
        self.treeAggregator.grid(row=0, column=0, sticky=tk.NSEW)
        self.treeAggregator.heading('aggregatorId', text='aggregatorId')
        self.treeAggregator.heading('clearPassword', text='clearPassword')
        self.treeAggregator.column('aggregatorId', anchor=tk.W, stretch='NO', width=100, minwidth=100)
        self.treeAggregator.column('clearPassword', anchor=tk.W, stretch='NO', width=100, minwidth=100)

        addButton = Button(dialog, text="Add", command=lambda: self.onDeleteChild(dialog))
        addButton.grid(row=0,column=1)

        editButton = Button(dialog, text="Edit", command=lambda: self.onDeleteChild(dialog))
        editButton.grid(row=1,column=1)

        saveButton = Button(dialog, text="Save", command=lambda: self.onDeleteChild(dialog))
        saveButton.grid(row=2,column=1)

        cancelButton = Button(dialog, text="Cancel", command=lambda: self.onDeleteChild(dialog))
        cancelButton.grid(row=3,column=1)