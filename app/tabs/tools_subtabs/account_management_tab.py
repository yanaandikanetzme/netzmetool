# app/tabs/tools_subtabs/account_management_tab.py
import tkinter as tk
from tkinter import ttk
from src.modules import Modules
from app.tabs.popup import ResponseOpenAPI
import threading

class AccountManagementTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.account_type = tk.StringVar()
        self.create_widgets()

    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self, padding="20 20 20 20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # Input section
        input_frame = ttk.LabelFrame(main_frame, text="Account Input", padding="10 10 10 10")
        input_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)

        tk.Label(input_frame, text="Account Type:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.type_cb = ttk.Combobox(input_frame, textvariable=self.account_type, width=30, state='readonly')
        self.type_cb['values'] = ['Netzme', 'Toko Netzme']
        self.type_cb.grid(row=0, column=1, padx=5, pady=5)
        self.type_cb.current(0)

        tk.Label(input_frame, text="Phone / User ID:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.input_field = ttk.Entry(input_frame, width=32)
        self.input_field.grid(row=1, column=1, padx=5, pady=5)

        self.check_account_btn = ttk.Button(input_frame, text="Check Account", command=self.start_thread_check_account)
        self.check_account_btn.grid(row=2, column=0, columnspan=2, pady=10)

        # Output section
        output_frame = ttk.LabelFrame(main_frame, text="Account Details", padding="10 10 10 10")
        output_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)

        tk.Label(output_frame, text="User ID:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.output_user_id = ttk.Entry(output_frame, width=32, state='readonly')
        self.output_user_id.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(output_frame, text="Phone No:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.output_phone_no = ttk.Entry(output_frame, width=32, state='readonly')
        self.output_phone_no.grid(row=1, column=1, padx=5, pady=5)

        # Action buttons
        action_frame = ttk.Frame(main_frame)
        action_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)

        self.reset_login_btn = ttk.Button(action_frame, text="Reset Login Request", command=self.start_thread_reset_login_request)
        self.reset_login_btn.grid(row=0, column=0, padx=5, pady=5)

        self.reset_pin_btn = ttk.Button(action_frame, text="Reset PIN Attempts", command=self.start_thread_reset_failed_attempt)
        self.reset_pin_btn.grid(row=0, column=1, padx=5, pady=5)

        self.reset_failed_btn = ttk.Button(action_frame, text="Reset Failed Attempts", command=self.start_thread_reset_attempt_otp)
        self.reset_failed_btn.grid(row=0, column=2, padx=5, pady=5)

    def start_thread_check_account(self):
        self.check_account_btn.config(state=tk.DISABLED)
        threading.Thread(target=self.check_account).start()

    def start_thread_reset_login_request(self):
        self.reset_login_btn.config(state=tk.DISABLED)
        threading.Thread(target=self.reset_login_request, args=(self.reset_login_btn,)).start()

    def start_thread_reset_attempt_otp(self):
        self.reset_pin_btn.config(state=tk.DISABLED)
        threading.Thread(target=self.reset_attempt_otp).start()

    def start_thread_reset_failed_attempt(self):
        self.reset_failed_btn.config(state=tk.DISABLED)
        threading.Thread(target=self.reset_failed_attempt).start()

    def check_account(self):
        try:
            input_value = self.input_field.get()
            validated_input = Modules.checkvalidNumber(input_value)
            account_type = self.account_type.get()

            table = "users" if account_type == 'Netzme' else "merchant_users"
            db_connect = Modules.ConnectDBNetzreg if account_type == 'Netzme' else Modules.ConnectDBMerchant

            SQL = f"SELECT user_name, phone_no FROM {table} WHERE user_name='{validated_input}' OR phone_no='{validated_input}'"
            result = db_connect(SQL)

            if result:
                self.output_user_id.config(state='normal')
                self.output_user_id.delete(0, tk.END)
                self.output_user_id.insert(0, str(result[0][0]))
                self.output_user_id.config(state='readonly')

                self.output_phone_no.config(state='normal')
                self.output_phone_no.delete(0, tk.END)
                self.output_phone_no.insert(0, str(result[0][1]))
                self.output_phone_no.config(state='readonly')
            else:
                ResponseOpenAPI("No account found.")
        except Exception as e:
            ResponseOpenAPI(str(e))
        finally:
            self.check_account_btn.config(state=tk.NORMAL)

    def reset_login_request(self, button):
        try:
            self.perform_reset_action("verification_requests", "merchant_verification_requests", "request_on")
        finally:
            button.config(state=tk.NORMAL)

    def reset_attempt_otp(self):
        self.perform_reset_action("verification_attempts", "merchant_verification_attempts", "verify_on")

    def reset_failed_attempt(self):
        try:
            input_value = self.input_field.get()
            validated_input = Modules.checkvalidNumber(input_value)
            account_type = self.account_type.get()

            if account_type == 'Netzme':
                SQL = f"UPDATE user_pin SET counter_failed = 0, suspend_ts = now() WHERE user_name = (SELECT user_name FROM users u WHERE u.phone_no = '{validated_input}');"
                result = Modules.ConnectDMLNetzreg(SQL)
            else:
                SQL = f"UPDATE merchant_pin SET counter_failed = 0, suspend_ts = now() WHERE user_name = (SELECT user_name FROM merchant_users mu WHERE mu.phone_no ='{validated_input}');"
                result = Modules.ConnectDMLMerchant(SQL)
            print(f'query : {SQL}')
            ResponseOpenAPI(result)
        except Exception as e:
            ResponseOpenAPI(str(e))
        finally:
            self.reset_failed_btn.config(state=tk.NORMAL)

    def perform_reset_action(self, netzme_table, merchant_table, timestamp_column):
        try:
            input_value = self.input_field.get()
            validated_input = Modules.checkvalidNumber(input_value)
            account_type = self.account_type.get()

            table = netzme_table if account_type == 'Netzme' else merchant_table
            db_connect = Modules.ConnectDMLNetzreg if account_type == 'Netzme' else Modules.ConnectDMLMerchant

            SQL = f"DELETE FROM {table} WHERE phone_no = '{validated_input}' AND {timestamp_column} >= (now() - INTERVAL '24 hour');"
            result = db_connect(SQL)

            ResponseOpenAPI(result)
        except Exception as e:
            ResponseOpenAPI(str(e))