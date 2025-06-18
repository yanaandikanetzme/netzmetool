# app/tabs/qr_subtabs/dispute_tab.py
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from src.modules import Modules
from app.custom.custom_text import CustomText
from app.tabs.popup import ResponseOpenAPI
from src.jsonParser import jsonParser
from src.dispute import dispute as disputez
import json
from app.custom.custom_treeview import CustomTreeview
import threading
import re
from datetime import datetime, date, timedelta, timezone

class DisputeTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.dispute_counter = 0
        self.create_frames()
        self.create_treeviews()
        self.create_controls()
        self.create_buttons()
        self.create_text_area()

    def create_frames(self):
        self.frame_top = ttk.Frame(self)
        self.frame_top.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.frame_middle = ttk.Frame(self)
        self.frame_middle.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

        self.frame_bottom = ttk.Frame(self)
        self.frame_bottom.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=5)

    def create_treeviews(self):
        columns_dispute = ('merchant_id', 'ref_id', 'amount_value', 'vendor_name', 'ts', 'count', 'dispute_status', 'latest_dispute_date', 'json_request')
        self.tree_dispute = CustomTreeview(self.frame_top, columns=columns_dispute, show='headings')
        self.tree_dispute.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        for col in columns_dispute:
            self.tree_dispute.heading(col, text=col)
            self.tree_dispute.column(col, width=100, anchor=tk.W)

        self.tree_dispute.column('ref_id', width=200)
        self.tree_dispute.column('ts', width=150)
        self.tree_dispute.column('dispute_status', width=200)
        self.tree_dispute.column('latest_dispute_date', width=150)
        self.tree_dispute.column('json_request', width=200)

        columns_dispute2 = ('counter', 'merchant_id', 'ref_id', 'amount_value', 'vendor_name', 'code', 'ts')
        self.tree_dispute2 = CustomTreeview(self.frame_bottom, columns=columns_dispute2, show='headings')
        self.tree_dispute2.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        for col in columns_dispute2:
            self.tree_dispute2.heading(col, text=col)
            self.tree_dispute2.column(col, width=100, anchor=tk.W)

        self.tree_dispute2.column('counter', width=50)
        self.tree_dispute2.column('ref_id', width=200)
        self.tree_dispute2.column('ts', width=150)

    def create_controls(self):
        controls_frame = ttk.Frame(self.frame_middle)
        controls_frame.pack(fill=tk.X, pady=5)

        tk.Label(controls_frame, text='Dispute Type:').pack(side=tk.LEFT, padx=5)
        self.dispute_type = ttk.Combobox(controls_frame, values=['chargeback', 'fightback', 'second chargeback', 'chargeback reversal', 'fightback reversal', 'goodfaith'], state="readonly", width=20)
        self.dispute_type.pack(side=tk.LEFT, padx=5)

        tk.Label(controls_frame, text='Vendor:').pack(side=tk.LEFT, padx=5)
        self.vendor = ttk.Combobox(controls_frame, values=['jalin', 'artajasa'], state="readonly", width=15)
        self.vendor.pack(side=tk.LEFT, padx=5)
        self.vendor.bind("<<ComboboxSelected>>", self.connectDBDisputeQRIS)

    def create_buttons(self):
        button_frame = ttk.Frame(self.frame_middle)
        button_frame.pack(fill=tk.X, pady=5)

        self.load_button = ttk.Button(button_frame, text="Load Data", command=self.start_thread_connection, width=15)
        self.load_button.pack(side=tk.LEFT, padx=5)

        self.add_data_button = ttk.Button(button_frame, text="Add Data Dispute", command=self.AddDataDisputeQRIS, width=15, state='disabled')
        self.add_data_button.pack(side=tk.LEFT, padx=5)

        self.hit_dispute_button = ttk.Button(button_frame, text="Hit Dispute", command=self.hitDisputeQRIS, width=15, state='disabled')
        self.hit_dispute_button.pack(side=tk.LEFT, padx=5)

        self.save_file_button = ttk.Button(button_frame, text="Save File Dispute", command=self.DisputeFile, width=15, state='disabled')
        self.save_file_button.pack(side=tk.LEFT, padx=5)

    def create_text_area(self):
        self.text_body = CustomText(self.frame_bottom, width=50, height=10)
        self.text_body.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        self.text_body.config(state='disabled')

    # The rest of the methods (start_thread_connection, connectDBDisputeQRIS, AddDataDisputeQRIS, etc.) 
    # remain the same, just update variable names to match the new structure.
    def start_thread_connection(self):
        self.load_button.config(state=tk.DISABLED)
        thread = threading.Thread(target=self.connectDBDisputeQRIS)
        thread.start()
            
    def connectDBDisputeQRIS(self, event=None):
        try:
            #self.LoadInvoiceSettlementManualbutton1.config(state='disabled')
            getSelectedMethod = self.dispute_type.get()
            getSelectedVendor = self.vendor.get()
            querycon = """
            SELECT
                qmt.merchant_id,
                qmt.ref_id,
                COALESCE(NULLIF(qmt.amount_value_round, 0), qmt.amount_value) AS amount_value,
                qmt.vendor_name,
                qmt.ts,
                (SELECT COUNT(1) FROM qris_merchant_dispute WHERE original_rrn = qmt.rrn_origin) AS count,
                (SELECT STRING_AGG("type", ', ' ORDER BY seq ASC) FROM qris_merchant_dispute WHERE original_rrn = qmt.rrn_origin) AS dispute_status,
                subquery.latest_dispute_date,
                qmt.json_request
            FROM
                qr_merchant_transaction qmt
            LEFT JOIN (
                SELECT
                    ref_id,
                    MAX(report_date) AS latest_dispute_date
                FROM
                    qris_merchant_dispute
                GROUP BY
                    ref_id
            ) subquery ON qmt.ref_id = subquery.ref_id
            WHERE
                qmt.vendor_name = '""" + getSelectedVendor + """' order by qmt.seq desc limit 500;
            """
            #('merchant_id', 'ref_id', 'amount_value', 'vendor_name', 'ts', 'dispute_count','dispute_status','json_request')
            ans = Modules.ConnectDBMerchant(querycon)
            for rowz in self.tree_dispute.get_children():
                self.tree_dispute.delete(rowz)
            for rowz in self.tree_dispute2.get_children():
                self.tree_dispute2.delete(rowz)
            
            self.dispute_counter = 0
            self.text_body.config(state='normal')
            self.text_body.delete('1.0', tk.END)
            self.text_body.config(state='disabled')
            for row in ans:
                self.tree_dispute.insert('', tk.END, values=(row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8]))
            self.load_button.config(state=tk.NORMAL)
            self.add_data_button.config(state='normal')
        except ValueError as error:
            ResponseOpenAPI(str(error))
        except IndexError as err:
            ResponseOpenAPI(str(err))
            
    dispute_lists = []

    def AddDataDisputeQRIS(self, event=None):
        try:
            getSelectedMethod = self.dispute_type.get()
            getSelectedVendor = self.vendor.get()

            selectedItem = self.tree_dispute.selection()[0]
            row = self.tree_dispute.item(selectedItem)['values']
            uuid = Modules.generateUUID()

            currentDate = datetime.now().strftime('%Y%m%d')
            vendorName = getSelectedVendor
            trCode = {
                'chargeback': '30',
                'fightback': '40',
                'second chargeback': '50',
                'chargeback reversal': '31',
                'fightback reversal': '41',
                'goodfaith': '81'
            }.get(getSelectedMethod, '')

            self.dispute_counter += 1
            counter_str = f"{self.dispute_counter:03d}"

            self.tree_dispute.delete(selectedItem)
            self.tree_dispute2.insert('', tk.END, values=(counter_str, row[0], row[1], row[2], row[3], trCode, row[4], row[7], row[8]))
            self.add_data_button.config(state='normal')

            group_debit = ['30', '50', '41']
            group_credit = ['40', '31', '81']

            self.qris_disputes = []
            totalAmountChargeback = 0
            totalAmountFightback = 0
            listTrxAddSave = []

            for rowz in self.tree_dispute2.get_children():
                values = self.tree_dispute2.item(rowz)['values']
                merchant_id, QRISrefId, amount, vendorName, transCode, ts = values[1:7]
                qris_json_request = values[8]
                report_date = values[7]

                try:
                    jsonReq = json.loads(qris_json_request.replace("'", '"').replace('\n', '').replace('\r', ''))
                except json.JSONDecodeError:
                    jsonReq = {item.split(":")[0].strip().strip("'"): item.split(":")[1].strip().strip("'") for item in qris_json_request.strip("{}").split(",")}

                rrn = str(jsonReq.get('rrn', ''))
                refId = rrn[:-16] if len(rrn) == 28 else rrn
                
                trxCode = str(jsonReq.get('processingCode', ''))
                captureDate = str(jsonReq.get('captureDate', ''))
                localtransaction = str(jsonReq.get('localTransactionDateTime', ''))
                date_obj = datetime.strptime(str(localtransaction), '%Y%m%d%H%M%S')
                formatted_date = date_obj.strftime('%Y%m%d')

                if report_date == "None":
                    reportDate = (date_obj + timedelta(days=1)).strftime('%Y%m%d')
                else:
                    latest_report_date = report_date
                    reportDate = Modules.generate_date(str(latest_report_date), 1)

                trxDate = Modules.replaceDateToTsDispute(ts)
                traceNo = str(jsonReq.get('systemTraceAuditNumber', ''))
                terminalId = str(jsonReq.get('terminalId', ''))
                merchantPan = str(jsonReq.get('pan', ''))
                acquirer = str(jsonReq.get('acquirerId', ''))
                issuer = str(jsonReq.get('issuerId', ''))
                customerPan = str(jsonReq.get('customerPan', ''))
                merchantCategory = str(jsonReq.get('merchantType', ''))
                merchantCriteria = str(jsonReq.get('merchantCriteria', ''))
                responseCode = "00"
                merchantName = str(jsonReq.get('merchantName', '')).strip("'\"").replace('"', "'")
                merchantLocation = str(jsonReq.get('merchantCity', ''))
                convenienceFee = "0.00"
                
                amount = float(amount)
                fee = (amount * 0.217) / 100
                interchange = (amount * 0.385) / 100

                disputeTranCode = str(transCode)

                if disputeTranCode in group_debit:
                    disputeAmount = -amount
                    disputeNetAmount = -abs(amount - fee)
                    interchangeFee = abs(interchange)
                    feeReturn = abs(fee)
                    update_total = "chargeback"
                    totalAmountChargeback += abs(disputeAmount)
                elif disputeTranCode in group_credit:
                    disputeAmount = amount
                    disputeNetAmount = abs(amount - fee)
                    interchangeFee = -abs(interchange)
                    feeReturn = -abs(fee)
                    update_total = "fightback"
                    totalAmountFightback += abs(disputeAmount)
                else:
                    raise ValueError(f"Unexpected transaction code: {disputeTranCode}")

                prefix = {
                    '30': 'CB', '40': 'FB', '50': '2NDCB',
                    '31': 'CBR', '41': 'FBR', '81': 'GF'
                }.get(disputeTranCode, '')

                registrationNumber = f"{prefix}{currentDate}{Modules.RandomDigit(6)}"

                dispute_data = {
                    "refId": refId,
                    "trxCode": trxCode,
                    "captureDate": formatted_date,
                    "trxDate": trxDate,
                    "traceNo": traceNo,
                    "terminalId": terminalId,
                    "merchantPan": merchantPan,
                    "amount": f"{amount:.2f}",
                    "acquirer": acquirer,
                    "issuer": issuer,
                    "customerPan": customerPan,
                    "merchantCategory": merchantCategory,
                    "merchantCriteria": merchantCriteria,
                    "responseCode": responseCode,
                    "merchantName": merchantName,
                    "merchantLocation": merchantLocation,
                    "convenienceFee": f"{float(convenienceFee):.2f}",
                    "interchangeFee": f"{interchangeFee:.2f}",
                    "disputeTranCode": disputeTranCode,
                    "disputeAmount": f"{disputeAmount:.2f}",
                    "feeReturn": f"{feeReturn:.2f}",
                    "disputeNetAmount": f"{disputeNetAmount:.2f}",
                    "registrationNumber": registrationNumber,
                    "reportDate": reportDate
                }
                self.qris_disputes.append(dispute_data)

                # Prepare data for file saving
                nominalFiles = f"{int(abs(disputeAmount)):,}.00"
                dateSaveFile = Modules.replaceDateToTsDisputeSave(ts)
                counterSaveFile = "{:06d}".format(self.dispute_counter)
                nominalnetFiles = f"{abs(disputeNetAmount):,.2f}"
                nominalinterchangeFeeFiles = f"{abs(interchangeFee):,.2f}"
                reasonCode = "1001"

                # Adjust field widths
                trxCode = Modules.LeftAdjust(trxCode, 9)
                dateSaveFile = Modules.LeftAdjust(dateSaveFile, 21)
                refId = Modules.LeftAdjust(refId, 13)
                traceNo = Modules.LeftAdjust(traceNo, 9)
                terminalId = Modules.LeftAdjust(terminalId, 17)
                merchantPan = Modules.LeftAdjust(merchantPan, 20)
                acquirer = Modules.LeftAdjust(acquirer, 12)
                issuer = Modules.LeftAdjust(issuer, 12)
                customerPan = Modules.LeftAdjust(customerPan, 20)
                nominalFiles = Modules.RightAdjust(nominalFiles, 16)
                merchantCategory = " " + Modules.LeftAdjust(merchantCategory, 18)
                merchantCriteria = Modules.LeftAdjust(merchantCriteria, 18)
                responseCode = Modules.LeftAdjust(responseCode, 14)
                merchantName = Modules.LeftAdjust(merchantName, 25)
                merchantLocation = Modules.LeftAdjust(merchantLocation, 13)
                convenienceFee = Modules.RightAdjust(convenienceFee, 14) + " "
                reasonCode = "  " + Modules.LeftAdjust(reasonCode, 13)

                if getSelectedVendor == "artajasa":
                    counterSaveFile = Modules.LeftAdjust(counterSaveFile, 7)
                    interchangeFee = Modules.RightAdjust(nominalinterchangeFeeFiles, 16)
                    disputeTranCode = Modules.LeftAdjust(disputeTranCode, 2)
                    nominalFiles2 = Modules.RightAdjust(nominalFiles, 32)
                    feeReturn = Modules.RightAdjust(f"{feeReturn:.2f}", 16)
                    nominalnetFiles = Modules.RightAdjust(nominalnetFiles, 16) + " "
                    newVal = f"{counterSaveFile}{trxCode}{dateSaveFile}{refId}{traceNo}{terminalId}{merchantPan}{acquirer}{issuer}{customerPan}{nominalFiles}{merchantCategory}{merchantCriteria}{responseCode}{merchantName}{merchantLocation}ID{convenienceFee}C{interchangeFee}{reasonCode}{disputeTranCode}{nominalFiles2}{feeReturn}{nominalnetFiles}"
                elif getSelectedVendor == "jalin":
                    counterSaveFile = Modules.LeftAdjust(str(self.dispute_counter), 7)
                    interchangeFee = Modules.RightAdjust(f"{interchangeFee:.2f}", 16)
                    disputeTranCode = Modules.RightAdjust(disputeTranCode, 18)
                    nominalFiles2 = Modules.RightAdjust(nominalFiles, 19)
                    feeReturn = Modules.RightAdjust(f"{feeReturn:.2f}", 18)
                    nominalnetFiles = Modules.RightAdjust(nominalnetFiles, 18)
                    registrationNumber = Modules.RightAdjust(registrationNumber, 22) + " "
                    newVal = f"{counterSaveFile}{trxCode}{dateSaveFile}{refId}{traceNo}{terminalId}{merchantPan}{acquirer}{issuer}{customerPan}{nominalFiles}{merchantCategory}{merchantCriteria}{responseCode}{merchantName}{merchantLocation}ID{convenienceFee}C{interchangeFee}{disputeTranCode}{nominalFiles2}{feeReturn}{nominalnetFiles}{registrationNumber}"
                
                listTrxAddSave.append(newVal)

            body_data = {
                "qrisDisputes": self.qris_disputes,
                "vendorName": str(getSelectedVendor),
                "createdBy": f"Tools.Netzme {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            }

            output_json = {
                "requestId": uuid,
                "type": "qris_dispute_submit",
                "body": body_data
            }

            formatted_json = json.dumps(output_json, indent=2)

            self.text_body.config(state='normal')
            self.text_body.delete('1.0', tk.END)
            self.text_body.insert(tk.END, formatted_json)
            self.text_body.config(state='normal')

            self.hit_dispute_button.config(state='normal')
            self.save_file_button.config(state='normal')

            self.dispute_lists = [listTrxAddSave, str(totalAmountChargeback), str(totalAmountFightback)]

        except tk.TclError as error:
            ResponseOpenAPI(str(error))
        except ValueError as error:
            ResponseOpenAPI(str(error))
        except IndexError as err:
            ResponseOpenAPI(str(err))
        except Exception as e:
            ResponseOpenAPI(f"Error in AddDataDisputeQRIS: {str(e)}")
            self.qris_disputes = []  # Reset in case of error

    def DisputeFile(self, event=None):
        try:
            if not hasattr(self, 'qris_disputes') or not self.qris_disputes:
                raise ValueError("No dispute data available. Please add data first.")

            listdataDispute = []
            totalDisputeFightback = 0
            totalDisputeChargeback = 0

            for counter, dispute in enumerate(self.qris_disputes, start=1):
                # Format dispute data sesuai kebutuhan
                formatted_dispute = self.format_dispute_for_template(dispute, counter)
                listdataDispute.append(formatted_dispute)

                # Hitung total
                dispute_amount = float(dispute['disputeAmount'])
                if dispute['disputeTranCode'] in ['30', '50', '41']:
                    totalDisputeChargeback += abs(dispute_amount)
                elif dispute['disputeTranCode'] in ['40', '31', '81']:
                    totalDisputeFightback += abs(dispute_amount)
            vendor = self.vendor.get()
            print(f'listdataDispute sebelum di save : {listdataDispute}')
            if vendor == 'artajasa':
                filename = 'Dispute Artajasa ' + Modules.DateNowSec()
                text2save = str(disputez.ArtajasaTemplate(listdataDispute, totalDisputeFightback, totalDisputeChargeback))
            elif vendor == 'jalin':
                filename = 'Dispute Jalin ' + Modules.DateNowSec()
                text2save = str(disputez.JalinTemplate(listdataDispute, totalDisputeFightback, totalDisputeChargeback))
            else:
                raise ValueError(f"Unsupported vendor: {vendor}")

            file_path = filedialog.asksaveasfile(mode='w', defaultextension=".txt", initialfile=filename)
            if file_path is None:
                return
            file_path.write(text2save)
            messagebox.showinfo("Success", "File dispute berhasil disimpan.")
            file_path.close()

        except Exception as e:
            messagebox.showerror('Error', str(e))
    
    def format_dispute_for_template(self, dispute, counter):
        vendor = self.vendor.get()
        
        # Format date
        trx_date = datetime.strptime(dispute['trxDate'], '%Y-%m-%d %H:%M:%S')
        dateSaveFile = Modules.LeftAdjust(trx_date.strftime('%d/%m/%y    %H:%M:%S'), 21)
        
        # Format amounts with commas and correct signs
        amount = float(dispute['amount'])
        disputeAmount = float(dispute['disputeAmount'])
        feeReturnAmount = float(dispute['feeReturn'])
        netAmount = float(dispute['disputeNetAmount'])
        interchangeFeeAmount = float(dispute['interchangeFee'])
        
        if vendor == 'artajasa':
            if dispute['disputeTranCode'] in ['30', '50', '41']:
                nominalFiles = Modules.RightAdjust(f"{-abs(amount):,.2f}", 16)
                nominalFiles2 = Modules.RightAdjust(f"{-abs(disputeAmount):,.2f}", 32)
                feeReturn = Modules.RightAdjust(f"{abs(feeReturnAmount):,.2f}", 16)
                nominalnetFiles = Modules.RightAdjust(f"{-abs(netAmount):,.2f}", 16)
                interchangeFee = Modules.RightAdjust(f"{abs(interchangeFeeAmount):,.2f}", 16)
            else:
                nominalFiles = Modules.RightAdjust(f"{abs(amount):,.2f}", 16)
                nominalFiles2 = Modules.RightAdjust(f"{abs(disputeAmount):,.2f}", 32)
                feeReturn = Modules.RightAdjust(f"{-abs(feeReturnAmount):,.2f}", 16)
                nominalnetFiles = Modules.RightAdjust(f"{abs(netAmount):,.2f}", 16)
                interchangeFee = Modules.RightAdjust(f"{-abs(interchangeFeeAmount):,.2f}", 16)
        else:  # For Jalin and any other vendors
            if dispute['disputeTranCode'] in ['30', '50', '41']:
                nominalFiles = Modules.RightAdjust(f"{amount:,.2f}", 16)
                nominalFiles2 = Modules.RightAdjust(f"{-abs(disputeAmount):,.2f}", 19)
                feeReturn = Modules.RightAdjust(f"{abs(feeReturnAmount):,.2f}", 18)
                nominalnetFiles = Modules.RightAdjust(f"{-abs(netAmount):,.2f}", 18)
            else:
                nominalFiles = Modules.RightAdjust(f"{amount:,.2f}", 16)
                nominalFiles2 = Modules.RightAdjust(f"{abs(disputeAmount):,.2f}", 19)
                feeReturn = Modules.RightAdjust(f"{-abs(feeReturnAmount):,.2f}", 18)
                nominalnetFiles = Modules.RightAdjust(f"{abs(netAmount):,.2f}", 18)
            interchangeFee = Modules.RightAdjust(f"{-abs(interchangeFeeAmount):,.2f}", 16)

        counterSaveFile = Modules.LeftAdjust(str(counter), 7)
        trxCode = Modules.LeftAdjust(dispute['trxCode'], 9)
        refId = Modules.LeftAdjust(dispute['refId'], 13)
        traceNo = Modules.LeftAdjust(dispute['traceNo'], 9)
        terminalId = Modules.LeftAdjust(dispute['terminalId'], 17)
        merchantPan = Modules.LeftAdjust(dispute['merchantPan'], 20)
        acquirer = Modules.LeftAdjust(dispute['acquirer'], 12)
        issuer = Modules.LeftAdjust(dispute['issuer'], 12)
        customerPan = Modules.LeftAdjust(dispute['customerPan'], 20)
        merchantCategory = " " + Modules.LeftAdjust(dispute['merchantCategory'], 18)
        merchantCriteria = Modules.LeftAdjust(dispute['merchantCriteria'], 18)
        responseCode = Modules.LeftAdjust(dispute['responseCode'], 14)
        merchantName = Modules.LeftAdjust(self.escape_merchant_name(dispute['merchantName'])[:25], 25)
        merchantLocation = Modules.LeftAdjust(dispute['merchantLocation'][:13], 13)
        convenienceFee = Modules.RightAdjust(f"{float(dispute['convenienceFee']):.2f}", 14) + " "
        disputeTranCode = dispute['disputeTranCode']
        
        if vendor == 'artajasa':
            counterSaveFileAJ = "{:06d}".format(int(counter))
            counterSaveFile = Modules.LeftAdjust(counterSaveFileAJ, 7)
            disputeTranCode = Modules.LeftAdjust(str(disputeTranCode), 2)
            nominalnetFiles += " "
            reasonCode = "1001"
            reasonCode = "  " + Modules.LeftAdjust(reasonCode, 13)
            return f"{counterSaveFile}{trxCode}{dateSaveFile}{refId}{traceNo}{terminalId}{merchantPan}{acquirer}{issuer}{customerPan}{nominalFiles}{merchantCategory}{merchantCriteria}{responseCode}{merchantName}{merchantLocation}ID{convenienceFee}C{interchangeFee}{reasonCode}{disputeTranCode}{nominalFiles2}{feeReturn}{nominalnetFiles}"
        elif vendor == 'jalin':
            disputeTranCode = Modules.RightAdjust(str(disputeTranCode), 18)
            registrationNumber = Modules.RightAdjust(dispute.get('registrationNumber', ''), 22) + " "
            return f"{counterSaveFile}{trxCode}{dateSaveFile}{refId}{traceNo}{terminalId}{merchantPan}{acquirer}{issuer}{customerPan}{nominalFiles}{merchantCategory}{merchantCriteria}{responseCode}{merchantName}{merchantLocation}ID{convenienceFee}C{interchangeFee}{disputeTranCode}{nominalFiles2}{feeReturn}{nominalnetFiles}{registrationNumber}"

    def escape_merchant_name(self, name):
        # Replace single quotes with double quotes, then escape double quotes
        return name.replace('"', '\\"')

    def hitDisputeQRIS(self, event=None):
        try:
            url = 'https://tokoapi-stg.netzme.com/api/merchant/qr/qris-dispute'
            headerreq = {"Authorization":'Basic a2FyZTpkZGUyOGM3ZWRiOWQ4MDQ2OTcyYzVjMzI3N2Q5OTlhMg=='}
            bdy = str(self.text_body.get("1.0",'end-1c'))
            json_unescape = bdy.encode().decode('unicode-escape')
            reqbody = json.loads(json_unescape)
            response = Modules.make_http_request(url=url, headers=headerreq, body_request=reqbody)
            if response:
                http_status_code = response[0]
                response_message = response[1]
                response_message = jsonParser.jsonParserBeautify(response_message)
                msgbox = f"HTTP Status Code: {http_status_code}\nResponse Message: {response_message}"
                ResponseOpenAPI(msgbox)
        except ValueError as error:
            ResponseOpenAPI(str(error))
        except IndexError as err:
            ResponseOpenAPI(str(err))