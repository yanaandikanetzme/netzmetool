import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import uuid
import requests
import json
from src.modules import Modules
from app.tabs.popup import ResponseOpenAPI
import threading

class DisbursementAPIApp(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        self.user_entries = []

        self.create_widgets()
        self.on_request_type_change()

    def create_widgets(self):
        # Left frame for inputs
        self.left_frame = ttk.Frame(self.main_frame)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Right frame for request body
        self.right_frame = ttk.Frame(self.main_frame)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(0, 0))

        # Request Type
        ttk.Label(self.left_frame, text="Request Type:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.request_type_var = tk.StringVar(value="review")
        self.request_type_combo = ttk.Combobox(self.left_frame, textvariable=self.request_type_var, values=["review", "process"], state="readonly", width=30)
        self.request_type_combo.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        self.request_type_var.trace_add("write", self.on_request_type_change)

        # Institution ID
        ttk.Label(self.left_frame, text="Institution ID:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.institution_id_entry = ttk.Entry(self.left_frame, width=30)
        self.institution_id_entry.grid(row=1, column=1, sticky="w", padx=5, pady=5)
        self.institution_id_entry.insert(0, "institutiontest1")
        self.institution_id_entry.bind('<KeyRelease>', self.update_request_body)

        # Review Request ID
        self.review_request_id = tk.StringVar()
        self.review_request_id_label = ttk.Label(self.left_frame, text="Review Request ID:")
        self.review_request_id_label.grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.review_request_id_entry = ttk.Entry(self.left_frame, textvariable=self.review_request_id, width=30)
        self.review_request_id_entry.grid(row=2, column=1, sticky="w", padx=5, pady=5)

        # User Maker
        self.user_maker_label = ttk.Label(self.left_frame, text="User Maker:")
        self.user_maker_label.grid(row=3, column=0, sticky="e", padx=5, pady=5)
        self.user_maker_entry = ttk.Entry(self.left_frame, width=30)
        self.user_maker_entry.grid(row=3, column=1, sticky="w", padx=5, pady=5)
        self.user_maker_entry.insert(0, "Makernya")
        self.user_maker_entry.bind('<KeyRelease>', self.update_request_body)

        # User Approval
        self.user_approval_label = ttk.Label(self.left_frame, text="User Approval:")
        self.user_approval_label.grid(row=4, column=0, sticky="e", padx=5, pady=5)
        self.user_approval_entry = ttk.Entry(self.left_frame, width=30)
        self.user_approval_entry.grid(row=4, column=1, sticky="w", padx=5, pady=5)
        self.user_approval_entry.insert(0, "Approvalnya")
        self.user_approval_entry.bind('<KeyRelease>', self.update_request_body)

        # Users Frame with Scrollbar
        self.users_outer_frame = ttk.LabelFrame(self.left_frame, text="Users")
        self.users_outer_frame.grid(row=5, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
        self.left_frame.rowconfigure(5, weight=1)
        self.left_frame.columnconfigure(1, weight=1)

        self.users_canvas = tk.Canvas(self.users_outer_frame)
        self.users_scrollbar = ttk.Scrollbar(self.users_outer_frame, orient="vertical", command=self.users_canvas.yview)
        self.users_frame = ttk.Frame(self.users_canvas)

        self.users_canvas.configure(yscrollcommand=self.users_scrollbar.set)

        self.users_scrollbar.pack(side="right", fill="y")
        self.users_canvas.pack(side="left", fill="both", expand=True)
        self.users_canvas.create_window((0, 0), window=self.users_frame, anchor="nw")

        self.users_frame.bind("<Configure>", lambda e: self.users_canvas.configure(scrollregion=self.users_canvas.bbox("all")))

        # Configure columns
        self.users_frame.columnconfigure(1, weight=3)  # Phone Number
        self.users_frame.columnconfigure(2, weight=2)  # Amount
        self.users_frame.columnconfigure(3, weight=4)  # Message

        # Add labels for Phone Number, Amount, and Message
        ttk.Label(self.users_frame, text="Phone Number").grid(row=0, column=1, padx=5, pady=2, sticky="w")
        ttk.Label(self.users_frame, text="Amount").grid(row=0, column=2, padx=5, pady=2, sticky="w")
        ttk.Label(self.users_frame, text="Message").grid(row=0, column=3, padx=5, pady=2, sticky="w")

        # Buttons
        self.button_frame = ttk.Frame(self.left_frame)
        self.button_frame.grid(row=6, column=0, columnspan=2, pady=10)

        self.add_user_button = ttk.Button(self.button_frame, text="Add User", command=self.add_user)
        self.add_user_button.pack(side=tk.LEFT, padx=5)

        self.remove_user_button = ttk.Button(self.button_frame, text="Remove User", command=self.remove_user)
        self.remove_user_button.pack(side=tk.LEFT, padx=5)

        self.send_button = ttk.Button(self.button_frame, text="Send Request", command=self.start_thread_connection)
        self.send_button.pack(side=tk.LEFT, padx=5)

        # Request Body (in right frame)
        ttk.Label(self.right_frame, text="Request Body:").pack(anchor="w", padx=5, pady=5)
        self.request_body_text = scrolledtext.ScrolledText(self.right_frame, width=50, height=30)
        self.request_body_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Add initial user
        self.add_user()

    def add_user(self):
        new_row = len(self.user_entries) + 1
        user_entry = UserEntry(self.users_frame, new_row, self.update_request_body)
        self.user_entries.append(user_entry)
        self.update_request_body()

    def remove_user(self):
        if self.user_entries:
            user_entry = self.user_entries.pop()
            user_entry.destroy()
            self.update_request_body()
    
    def start_thread_connection(self):
        self.send_button.config(state=tk.DISABLED)
        # Memulai thread baru untuk koneksi database
        thread = threading.Thread(target=self.send_request)
        thread.start()
    
    def send_request(self):
        request_type = self.request_type_var.get()
        url = f"https://api-stg.netzme.com/disburs/netzme/{request_type}"
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Basic c2t5ZmVlZDpza3lmZWVkKio="
        }

        request_id = self.review_request_id.get() if request_type == "process" else str(uuid.uuid4())
        data = self.get_request_data(request_id, f"disburs_{request_type}")

        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            response_data = response.json()
            if request_type == "review":
                self.review_request_id.set(response_data.get("requestId", ""))
            ResponseOpenAPI(f"{request_type.capitalize()} API Response\nStatus Code: {response.status_code}\n\nResponse Message: {json.dumps(response_data, indent=2)}", self)
            self.send_button.config(state=tk.NORMAL)
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            self.send_button.config(state=tk.NORMAL)

    def get_request_data(self, request_id, request_type):
        data = {
            "requestId": request_id,
            "type": request_type,
            "body": {
                "institutionId": self.institution_id_entry.get(),
                "method": "phoneNo",
                "disbursementUsers": [user.get_data() for user in self.user_entries]
            }
        }
        if request_type == "disburs_process":
            data["body"]["userMaker"] = self.user_maker_entry.get()
            data["body"]["userApproval"] = self.user_approval_entry.get()
        return data

    def update_request_body(self, *args):
        request_type = self.request_type_var.get()
        request_id = self.review_request_id.get() if request_type == "process" else str(uuid.uuid4())
        request_data = self.get_request_data(request_id, f"disburs_{request_type}")
        self.request_body_text.delete(1.0, tk.END)
        self.request_body_text.insert(tk.END, json.dumps(request_data, indent=2))

    def on_request_type_change(self, *args):
        request_type = self.request_type_var.get()
        if request_type == "review":
            self.review_request_id_label.grid_remove()
            self.review_request_id_entry.grid_remove()
            self.user_maker_label.grid_remove()
            self.user_maker_entry.grid_remove()
            self.user_approval_label.grid_remove()
            self.user_approval_entry.grid_remove()
        else:
            self.review_request_id_label.grid()
            self.review_request_id_entry.grid()
            self.user_maker_label.grid()
            self.user_maker_entry.grid()
            self.user_approval_label.grid()
            self.user_approval_entry.grid()
        self.update_request_body()

class UserEntry(tk.Frame):
    def __init__(self, parent, row, update_callback):
        self.frame = ttk.Frame(parent)
        self.frame.grid(row=row, column=0, columnspan=4, pady=5, sticky="ew")

        ttk.Label(self.frame, text=f"User {row}:").grid(row=0, column=0, padx=5, pady=2, sticky="e")
        
        self.phone_entry = ttk.Entry(self.frame, width=20)
        self.phone_entry.grid(row=0, column=1, padx=5, pady=2, sticky="ew")
        
        self.amount_entry = ttk.Entry(self.frame, width=10)
        self.amount_entry.grid(row=0, column=2, padx=5, pady=2, sticky="ew")
        
        self.message_entry = ttk.Entry(self.frame, width=30)
        self.message_entry.grid(row=0, column=3, padx=5, pady=2, sticky="ew")

        # Configure columns to match parent
        self.frame.columnconfigure(1, weight=3)  # Phone Number
        self.frame.columnconfigure(2, weight=2)  # Amount
        self.frame.columnconfigure(3, weight=4)  # Message

        for entry in (self.phone_entry, self.amount_entry, self.message_entry):
            entry.bind('<KeyRelease>', update_callback)

    def get_data(self):
        phone_no = self.phone_entry.get()
        if len(phone_no) <= 10:
            phone_format = phone_no
        else:
            phone_format = str(Modules.checkvalidNumber(phone_no))        
        return {
            "phoneNo": phone_format,
            "amount": int(self.amount_entry.get()) if self.amount_entry.get() else 0,
            "message": self.message_entry.get()
        }

    def destroy(self):
        self.frame.destroy()
