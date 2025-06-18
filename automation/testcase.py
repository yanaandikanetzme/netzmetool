from automation.invoice import create_invoice
from automation.src.base import validate_expression, create_log_message, repetitive_assertion, validasi_data_list
from automation.payment import payment_invoice_qris, payment_qris_statis
from automation.database import check_events_merchant, checkBalance, checkInvoiceStatus, check_status_qr_merchant_transaction, check_mitra_netzme_transaction_detail, check_events_netzme, check_qris_payment, check_balance_netzme
from src.modules import Modules
from automation.qr_dinamis import create_qr_dinamis

def payment_invoice(merchant_id, payment_method, is_mitra: bool, off_us: bool=True, vendor=None, user_id_netzme=None, logs:bool=False):
    create_log_message(f'----------------- Testcase Invoice {payment_method} -----------------')
    create_log_message(f'##### Check Balance Awal #####')
    cekbalance = checkBalance(merchant_id, showlog=logs)
    amount_lama = cekbalance[3]
    create_log_message(f'##### Create Invoice {payment_method} #####')
    runTest = create_invoice(payment_method, merchant_id=merchant_id)
    invoice_transaction_id = runTest[2]
    nominal = runTest[1]
    create_log_message(f'##### Payment Invoice {payment_method} #####')
    if payment_method == 'BANK_TRANSFER':
        mdr_round = 5550
        nominal_nett = int(nominal) - mdr_round
        create_log_message(f'##### Payment {payment_method} #####')
        
    elif payment_method == 'QRIS':
        mdr_round = Modules.round_up(int(nominal) * 0.007)
        nominal_nett = int(nominal) - mdr_round
        if off_us:
            create_log_message(f'##### Payment {payment_method} Off Us #####')
            rrna = payment_invoice_qris(invoice_transaction_id, vendore=vendor, show_log=logs)
            rrn28digit = rrna[2]
            cekstatus_table_qr_merchant_transaction = check_status_qr_merchant_transaction(nominal,rrna[1], showlog=logs)

            if vendor in ['jalin_domestik', 'jalin_crossborder', 'artajasa']:
                print(vendor)
                create_log_message(f'##### Check Balance Akhir #####')
                cekbalance2 = checkBalance(merchant_id, showlog=logs)
                amount_baru = cekbalance2[3]
                validate_expression(amount_lama, nominal_nett, amount_baru)

                create_log_message(f'##### Check Table qr_merchant_transaction #####')
                validasi_data_list(cekstatus_table_qr_merchant_transaction,"isi", show_logs=logs)
                repetitive_assertion([(nominal, cekstatus_table_qr_merchant_transaction[2]),(cekstatus_table_qr_merchant_transaction[4], mdr_round)], show_logs=logs)
                
                create_log_message(f'##### Check Table events #####')
                type_events = 'pay_invoice'
                status_events = 'paid'
                trace_id = cekstatus_table_qr_merchant_transaction[5]
                all_events = check_events_merchant(trace_id, showlog=logs)
                validasi_data_list(all_events,"isi", show_logs=logs)
                repetitive_assertion([(nominal_nett, all_events[2]),(type_events,all_events[1]),(status_events,all_events[3]),(amount_baru, all_events[4])], show_logs=logs)

                create_log_message(f'##### Check Table merchant_invoice_transaction #####')
                cekstatus_table_invoice = checkInvoiceStatus(invoice_transaction_id, showlog=logs)
                validasi_data_list(cekstatus_table_invoice,"isi", show_logs=logs)
                repetitive_assertion([('paid',cekstatus_table_invoice[1]),(cekstatus_table_invoice[0], nominal)], show_logs=logs)  

                if is_mitra:
                    create_log_message(f'##### Check Table mitra_netzme_transaction_detail #####')
                    table_mitra = check_mitra_netzme_transaction_detail(nominal,rrn28digit, showlog=logs)
                    validasi_data_list(table_mitra,"isi", show_logs=logs)
                    repetitive_assertion([(nominal, table_mitra[2]),(table_mitra[4], mdr_round),(nominal_nett, table_mitra[3])], show_logs=logs)
            else:
                print(vendor)
                create_log_message(f'##### Check Table qr_merchant_transaction #####')
                validasi_data_list(cekstatus_table_qr_merchant_transaction,"tidak isi", show_logs=logs)
                create_log_message(f'##### Check Table events #####')
                validasi_data_list(all_events,"tidak isi", show_logs=logs)
                create_log_message(f'##### Check Table merchant_invoice_transaction #####')
                validasi_data_list(cekstatus_table_invoice,"tidak isi", show_logs=logs)

                create_log_message(f'##### Check Balance Akhir #####')
                nominal_nett = 0
                amount_baru = cekbalance2[3]
                validate_expression(amount_lama, nominal_nett, amount_baru)
                if is_mitra:
                    create_log_message(f'##### Check Table mitra_netzme_transaction_detail #####')
                    table_mitra = check_mitra_netzme_transaction_detail(nominal,rrn28digit, showlog=logs)
                    validasi_data_list(table_mitra,"tidak isi", show_logs=logs)
        else:
            create_log_message(f'##### Check Balance Netzme Awal #####')
            balance_netzme_awal = check_balance_netzme(user_id_netzme,showlog=logs)[0]

            create_log_message(f'##### Payment {payment_method} On Us #####')
            rrna = payment_invoice_qris(invoice_transaction_id, is_off_us=False, user_id_netzme=user_id_netzme, show_log=logs)

            create_log_message(f'##### Check Balance Netzme Akhir #####')
            balance_netzme_akhir = check_balance_netzme(user_id_netzme,showlog=logs)[0]
            validate_expression(balance_netzme_akhir, nominal, balance_netzme_awal)
            
            rrn28digit = rrna[2]
            create_log_message(f'##### Check Table qris_payment #####')
            qr_payment = check_qris_payment(rrn28digit, showlog=logs)
            status = qr_payment[0]
            amount_value = qr_payment[1]
            qr_type = qr_payment[2]
            ref_id = qr_payment[3]
            repetitive_assertion([(nominal, amount_value),('success', status),(qr_type, 'qr_type_qris_dynamic')], show_logs=logs)
            create_log_message(f'##### Check Table events_latest_transaction #####')
            events_latest_transaction = check_events_netzme(ref_id, showlog=logs)
            amount_elt = events_latest_transaction[0]
            type_elt = events_latest_transaction[1]
            status_elt = events_latest_transaction[2]
            repetitive_assertion([(nominal, Modules.round_up(amount_elt)),('success', status_elt),(type_elt, 'qr_invoice')], show_logs=logs)

            cekstatus_table_qr_merchant_transaction = check_status_qr_merchant_transaction(nominal,rrna[1], showlog=logs)
            create_log_message(f'##### Check Balance Akhir #####')
            cekbalance2 = checkBalance(merchant_id, showlog=logs)
            amount_baru = cekbalance2[3]
            validate_expression(amount_lama, nominal_nett, amount_baru)

            create_log_message(f'##### Check Table qr_merchant_transaction #####')
            validasi_data_list(cekstatus_table_qr_merchant_transaction,"isi", show_logs=logs)
            repetitive_assertion([(nominal, cekstatus_table_qr_merchant_transaction[2]),(cekstatus_table_qr_merchant_transaction[4], mdr_round)], show_logs=logs)
            
            create_log_message(f'##### Check Table events #####')
            type_events = 'pay_invoice'
            status_events = 'paid'
            trace_id = cekstatus_table_qr_merchant_transaction[5]
            all_events = check_events_merchant(trace_id, showlog=logs)
            validasi_data_list(all_events,"isi", show_logs=logs)
            repetitive_assertion([(nominal_nett, all_events[2]),(type_events,all_events[1]),(status_events,all_events[3]),(amount_baru, all_events[4])], show_logs=logs)

            create_log_message(f'##### Check Table merchant_invoice_transaction #####')
            cekstatus_table_invoice = checkInvoiceStatus(invoice_transaction_id, showlog=logs)
            validasi_data_list(cekstatus_table_invoice,"isi", show_logs=logs)
            repetitive_assertion([('paid',cekstatus_table_invoice[1]),(cekstatus_table_invoice[0], nominal)], show_logs=logs)  

            if is_mitra:
                create_log_message(f'##### Check Table mitra_netzme_transaction_detail #####')
                table_mitra = check_mitra_netzme_transaction_detail(nominal,rrn28digit, showlog=logs)
                validasi_data_list(table_mitra,"isi", show_logs=logs)
                repetitive_assertion([(nominal, table_mitra[2]),(table_mitra[4], mdr_round),(nominal_nett, table_mitra[3])], show_logs=logs)


def payment_qris_static(merchant_id, is_mitra: bool, off_us:bool = True, vendore=None, user_id_netzme=None, logs:bool=False):
    create_log_message(f'----------------- Testcase Payment QRIS OffUs Static -----------------')
    create_log_message(f'##### Check Balance Awal #####')
    cekbalance = checkBalance(merchant_id, showlog=logs)
    amount_lama = cekbalance[3]
    if off_us:
        create_log_message(f'##### Payment Qris Off Us Static #####')
        run_payment = payment_qris_statis(merchant_id, vendor=vendore, show_log=logs)
        nominal = run_payment[0]
        rrn = run_payment[1]
        rrn28digit = run_payment[2] 
    else:
        create_log_message(f'##### Check Balance Netzme Awal #####')
        balance_netzme_awal = check_balance_netzme(user_id_netzme,showlog=logs)[0]

        create_log_message(f'##### PaymentQris On Us Static #####')
        run_payment = payment_qris_statis(merchant_id,is_off_us=False, user_id_netzme=user_id_netzme, show_log=logs)
        nominal = run_payment[0]
        rrn = run_payment[1]
        rrn28digit = run_payment[2]

        create_log_message(f'##### Check Balance Netzme Akhir #####')
        balance_netzme_akhir = check_balance_netzme(user_id_netzme,showlog=logs)[0]
        validate_expression(balance_netzme_akhir, nominal, balance_netzme_awal)
        create_log_message(f'##### Check Table qris_payment #####')
        qr_payment = check_qris_payment(rrn28digit, showlog=logs)
        status = qr_payment[0]
        amount_value = qr_payment[1]
        qr_type = qr_payment[2]
        ref_id = qr_payment[3]
        repetitive_assertion([(nominal, amount_value),('success', status),(qr_type, 'qr_type_qris_static')], show_logs=logs)
        create_log_message(f'##### Check Table events_latest_transaction #####')
        events_latest_transaction = check_events_netzme(ref_id, showlog=logs)
        amount_elt = events_latest_transaction[0]
        type_elt = events_latest_transaction[1]
        status_elt = events_latest_transaction[2]
        repetitive_assertion([(nominal, Modules.round_up(amount_elt)),('success', status_elt),(type_elt, 'qr_invoice')], show_logs=logs)
    
    mdr_round = Modules.round_up(int(nominal) * 0.007)
    nominal_nett = int(nominal) - mdr_round
    
    create_log_message(f'##### Check Balance Akhir #####')
    cekbalance2 = checkBalance(merchant_id, showlog=logs)
    amount_baru = cekbalance2[3]
    validate_expression(amount_lama, nominal_nett, amount_baru)
    create_log_message(f'##### Check Table qr_merchant_transaction #####')
    cekstatus_table_qr_merchant_transaction = check_status_qr_merchant_transaction(nominal,rrn, showlog=logs)
    trace_id = cekstatus_table_qr_merchant_transaction[5]
    repetitive_assertion([(nominal, cekstatus_table_qr_merchant_transaction[2]),(cekstatus_table_qr_merchant_transaction[4], mdr_round)], show_logs=logs)
    create_log_message(f'##### Check Table events #####')
    all_events = check_events_merchant(trace_id, showlog=logs)
    repetitive_assertion([(nominal_nett, all_events[2]),('pay_qris',all_events[1]),('success',all_events[3]),(amount_baru, all_events[4])], show_logs=logs)
    if is_mitra:
        create_log_message(f'##### Check Table mitra_netzme_transaction_detail #####')
        table_mitra = check_mitra_netzme_transaction_detail(nominal,rrn28digit, showlog=logs)
        repetitive_assertion([(nominal, table_mitra[2]),(table_mitra[4], mdr_round),(nominal_nett, table_mitra[3])], show_logs=logs)
    
def payment_qris_dynamic(merchant_id, is_mitra: bool, off_us:bool = True, vendor=None, user_id_netzme=None, logs:bool=False):
    create_log_message(f'----------------- Testcase Payment QRIS Dinamis -----------------')
    create_log_message(f'##### Check Balance Awal #####')
    cekbalance = checkBalance(merchant_id, showlog=logs)
    amount_lama = cekbalance[3]
    create_log_message(f'##### Create QRIS Dinamis #####')
    runTest = create_qr_dinamis(merchant_id, showlogs=logs)
    invoice_transaction_id = runTest[1]
    nominal = runTest[0]
    mdr_round = Modules.round_up(int(nominal) * 0.007)
    nominal_nett = int(nominal) - mdr_round
    if off_us:
        create_log_message(f'##### Payment QRIS Dinamis Off Us #####')
        rrna = payment_invoice_qris(invoice_transaction_id, vendore=vendor, show_log=logs)
    else:
        create_log_message(f'##### Check Balance Netzme Awal #####')
        balance_netzme_awal = check_balance_netzme(user_id_netzme,showlog=logs)[0]
        
        create_log_message(f'##### Payment QRIS Dinamis On Us #####')
        rrna = payment_invoice_qris(invoice_transaction_id, is_off_us=False, user_id_netzme=user_id_netzme, show_log=logs)

        create_log_message(f'##### Check Balance Netzme Akhir #####')
        balance_netzme_akhir = check_balance_netzme(user_id_netzme,showlog=logs)[0]
        validate_expression(balance_netzme_akhir, nominal, balance_netzme_awal)

        create_log_message(f'##### Check Table qris_payment #####')
        qr_payment = check_qris_payment(rrna[2], showlog=logs)
        status = qr_payment[0]
        amount_value = qr_payment[1]
        qr_type = qr_payment[2]
        ref_id = qr_payment[3]
        repetitive_assertion([(nominal, amount_value),('success', status),(qr_type, 'qr_type_qris_dynamic')], show_logs=logs)
        create_log_message(f'##### Check Table events_latest_transaction #####')
        events_latest_transaction = check_events_netzme(ref_id, showlog=logs)
        amount_elt = events_latest_transaction[0]
        type_elt = events_latest_transaction[1]
        status_elt = events_latest_transaction[2]
        repetitive_assertion([(nominal, Modules.round_up(amount_elt)),('success', status_elt),(type_elt, 'qr_invoice')], show_logs=logs)

    rrn28digit = rrna[2]

    create_log_message(f'##### Check Table qr_merchant_transaction #####')
    cekstatus_table_qr_merchant_transaction = check_status_qr_merchant_transaction(nominal,rrna[1], showlog=logs)
    repetitive_assertion([(nominal, cekstatus_table_qr_merchant_transaction[2]),(cekstatus_table_qr_merchant_transaction[4], mdr_round)], show_logs=logs)
    type_events = 'pay_qris'
    status_events = 'success'
    create_log_message(f'##### Check Balance Akhir #####')
    cekbalance2 = checkBalance(merchant_id, showlog=logs)
    amount_baru = cekbalance2[3]
    validate_expression(amount_lama, nominal_nett, amount_baru)        
    create_log_message(f'##### Check Table events #####')
    trace_id = cekstatus_table_qr_merchant_transaction[5]
    all_events = check_events_merchant(trace_id, showlog=logs)
    repetitive_assertion([(nominal_nett, all_events[2]),(type_events,all_events[1]),(status_events,all_events[3]),(amount_baru, all_events[4])], show_logs=logs)
    if is_mitra:
        create_log_message(f'##### Check Table mitra_netzme_transaction_detail #####')
        table_mitra = check_mitra_netzme_transaction_detail(nominal,rrn28digit, showlog=logs)
        repetitive_assertion([(nominal, table_mitra[2]),(table_mitra[4], mdr_round),(nominal_nett, table_mitra[3])], show_logs=logs)
