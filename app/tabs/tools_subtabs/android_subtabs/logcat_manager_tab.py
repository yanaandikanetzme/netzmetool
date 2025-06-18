#lokasi  app/tabs/tools_subtabs/android_subtabs/logcat_manager_tab.py
import tkinter as tk
from tkinter import ttk
import threading
import subprocess
import re
import queue
import os
import signal
import platform
import datetime
import time
from app.custom.custom_text import CustomText

class LogcatManager(ttk.Frame):
    def __init__(self, master=None, min_height=600):
        super().__init__(master)
        self.master = master
        self.word_wrap = tk.BooleanVar(value=True)
        self.log_font_size = 12  # Ukuran font yang lebih besar
        self.min_height = min_height
        self.processes = {}
        self.logcat_running = threading.Event()
        self.log_queue = queue.Queue()
        self.auto_scroll = True
        self.last_scroll_position = 1.0
        self.search_results = []
        self.current_match = -1
        self.search_active = False
        self.search_lock = threading.Lock()
        self.search_queue = queue.Queue()
        self.using_next_prev = False
        self.search_pattern = None
        self.search_index = "1.0"
        self.previously_selected_apps = set()
        self.v_scrollbar = None

        self.device_connected = False
        self.device_check_thread = None
        self.running_apps_check_thread = None
        self.stop_threads = threading.Event()

        self.create_widgets()
        self.configure_layout()
        self.after(100, self.update_running_apps)
        self.after(100, self.process_log_queue)
        self.after(100, self.process_search_queue)
        self.monitor_device_changes()
        self.monitor_running_apps()
        if not hasattr(self, 'v_scrollbar'):
            print("Warning: v_scrollbar was not initialized in create_widgets")

    def configure_layout(self):
        self.grid(sticky="nsew")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)  # Memberikan bobot ke baris log_frame

    def create_widgets(self):
        self.create_control_frame()
        self.create_filter_frame()
        self.create_log_frame()
        self.create_search_frame()
        #self.create_status_bar()

    def create_control_frame(self):
        control_frame = ttk.Frame(self, padding="5")
        control_frame.grid(row=0, column=0, sticky="ew")
        control_frame.columnconfigure(2, weight=1)

        self.logcat_btn = ttk.Button(control_frame, text="▶", width=3, command=self.toggle_logcat)
        self.logcat_btn.grid(row=0, column=0, padx=(0, 5))

        self.clear_btn = ttk.Button(control_frame, text="🗑", width=3, command=self.clear_logcat)
        self.clear_btn.grid(row=0, column=1, padx=(0, 5))

        self.word_wrap_check = ttk.Checkbutton(control_frame, text="Word Wrap", variable=self.word_wrap, command=self.toggle_word_wrap)
        self.word_wrap_check.grid(row=0, column=3, sticky="e")

    def create_filter_frame(self):
        filter_frame = ttk.Frame(self, padding="5")
        filter_frame.grid(row=1, column=0, sticky="ew")
        filter_frame.columnconfigure(1, weight=1)
        filter_frame.columnconfigure(3, weight=1)
        filter_frame.columnconfigure(5, weight=1)

        ttk.Label(filter_frame, text="App Filter:").grid(row=0, column=0, sticky="e", padx=(0, 5))
        self.app_filter = ttk.Combobox(filter_frame, values=["All Apps"], width=30)
        self.app_filter.grid(row=0, column=1, sticky="ew", padx=(0, 10))
        self.app_filter.set("All Apps")
        self.app_filter.bind("<<ComboboxSelected>>", self.restart_logcat)

        ttk.Label(filter_frame, text="Log Level:").grid(row=0, column=2, sticky="e", padx=(0, 5))
        self.log_level = ttk.Combobox(filter_frame, values=["All", "Verbose", "Debug", "Info", "Warn", "Error", "Assert"], width=10)
        self.log_level.grid(row=0, column=3, sticky="ew", padx=(0, 10))
        self.log_level.set("All")
        self.log_level.bind("<<ComboboxSelected>>", self.restart_logcat)

        ttk.Label(filter_frame, text="Log Mode:").grid(row=0, column=4, sticky="e", padx=(0, 5))
        self.log_mode = ttk.Combobox(filter_frame, values=["From Start", "From Now"], width=10)
        self.log_mode.grid(row=0, column=5, sticky="ew")
        self.log_mode.set("From Now")
        self.log_mode.bind("<<ComboboxSelected>>", self.restart_logcat)

    def create_log_frame(self):
        log_frame = ttk.Frame(self)
        log_frame.grid(row=2, column=0, sticky="nsew", padx=5, pady=5)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)

        self.log_area = CustomText(log_frame, wrap="word" if self.word_wrap.get() else "none", 
                                bg="black", fg="white", font=("Consolas", self.log_font_size))
        self.log_area.grid(row=0, column=0, sticky="nsew")

        self.v_scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_area.yview)
        self.v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar = ttk.Scrollbar(log_frame, orient="horizontal", command=self.log_area.xview)
        h_scrollbar.grid(row=1, column=0, sticky="ew")

        self.log_area.configure(yscrollcommand=self.update_scrollbar)
        self.log_area.configure(xscrollcommand=h_scrollbar.set)

        self.log_area.bind("<MouseWheel>", self.on_mouse_wheel)
        self.log_area.bind("<Button-4>", self.on_mouse_wheel)
        self.log_area.bind("<Button-5>", self.on_mouse_wheel)

        # Configure log area tags
        self.log_area.tag_configure("VERBOSE", foreground="white")
        self.log_area.tag_configure("DEBUG", foreground="cyan")
        self.log_area.tag_configure("INFO", foreground="light green")
        self.log_area.tag_configure("WARN", foreground="yellow")
        self.log_area.tag_configure("ERROR", foreground="red")
        self.log_area.tag_configure("ASSERT", foreground="red", underline=1)

        # Set minimum height for log_area
        self.log_area.config(height=20)  # Shows about 20 lines of text

    def create_search_frame(self):
        search_frame = ttk.Frame(self, padding="5")
        search_frame.grid(row=3, column=0, sticky="ew")
        search_frame.columnconfigure(1, weight=1)

        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        self.search_entry.grid(row=0, column=1, sticky="ew", padx=(0, 5))
        self.search_entry.bind("<Return>", self.search_logs)

        self.search_button = ttk.Button(search_frame, text="🔍", width=3, command=self.search_logs)
        self.search_button.grid(row=0, column=2, padx=(0, 5))

        self.prev_button = ttk.Button(search_frame, text="◀", width=3, command=self.goto_previous_match)
        self.next_button = ttk.Button(search_frame, text="▶", width=3, command=self.goto_next_match)
        self.clear_search_button = ttk.Button(search_frame, text="Clear", width=8, command=self.clear_search)
        self.match_counter = ttk.Label(search_frame, text="0/0 matches", width=15)

        self.case_sensitive_var = tk.BooleanVar(value=False)
        self.case_sensitive_check = ttk.Checkbutton(search_frame, text="Case Sensitive", variable=self.case_sensitive_var)
        self.case_sensitive_check.grid(row=0, column=3, padx=(5, 0))

        self.regex_var = tk.BooleanVar(value=False)
        self.regex_check = ttk.Checkbutton(search_frame, text="Regex", variable=self.regex_var)
        self.regex_check.grid(row=0, column=4, padx=5)

        self.toggle_search_elements(False)

    def create_status_bar(self):
        self.status_var = tk.StringVar()
        status_bar = ttk.Label(self, textvariable=self.status_var, relief="sunken", anchor="w")
        status_bar.grid(row=4, column=0, sticky="ew", pady=(5, 0))

    def toggle_word_wrap(self):
        new_wrap = "word" if self.word_wrap.get() else "none"
        self.log_area.configure(wrap=new_wrap)
    
    def update_scrollbar(self, *args):
        self.v_scrollbar.set(*args)
        self.check_scroll_position()

    def check_scroll_position(self):
        if hasattr(self, 'v_scrollbar'):
            current_position = float(self.v_scrollbar.get()[1])
            if current_position < 1.0:
                self.auto_scroll = False
            else:
                self.auto_scroll = True
            self.last_scroll_position = current_position
        else:
            print("Warning: v_scrollbar not found")

    def update_scrollbar(self, *args):
        if hasattr(self, 'v_scrollbar'):
            self.v_scrollbar.set(*args)
            self.check_scroll_position()
        else:
            print("Warning: v_scrollbar not found")

    def on_mouse_wheel(self, event):
        if self.v_scrollbar.get()[1] < 1.0:
            self.auto_scroll = False
        else:
            self.auto_scroll = True
            
    def process_search_queue(self):
        try:
            while True:
                message = self.search_queue.get_nowait()
                if self.search_active and self.search_pattern:
                    self.update_search(message)
        except queue.Empty:
            pass
        finally:
            self.after(100, self.process_search_queue)
    
    def search_logs(self, event=None):
        current_view = self.log_area.yview()
        self.using_next_prev = False
        search_term = self.search_var.get().strip()
        if not search_term:
            self.clear_search()
            self.toggle_search_elements(False)
            return
        
        self.toggle_search_elements(True)
        case_sensitive = self.case_sensitive_var.get()
        use_regex = self.regex_var.get()

        try:
            if use_regex:
                self.search_pattern = re.compile(search_term, 0 if case_sensitive else re.IGNORECASE)
            else:
                self.search_pattern = re.compile(re.escape(search_term), 0 if case_sensitive else re.IGNORECASE)
        except re.error:
            self.add_log("Invalid regex pattern", "ERROR")
            return

        self.last_search_term = search_term
        self.last_case_sensitive = case_sensitive
        self.last_use_regex = use_regex

        was_at_bottom = (self.last_scroll_position == 1.0)

        self.search_active = True
        self.find_all_matches()
        self.highlight_matches()
        self.update_match_counter()
        self.toggle_search_elements(True)
        if not self.using_next_prev and self.last_scroll_position < 1.0:
            self.log_area.yview_moveto(current_view[0])
        else:
            self.log_area.see(tk.END)

        if was_at_bottom:
            self.log_area.see(tk.END)
            self.last_scroll_position = 1.0
            self.auto_scroll = True

    def find_all_matches(self):
        with self.search_lock:
            content = self.log_area.get("1.0", tk.END)
            self.search_results = []
            for match in self.search_pattern.finditer(content):
                start = self.log_area.index(f"1.0 + {match.start()} chars")
                end = self.log_area.index(f"1.0 + {match.end()} chars")
                self.search_results.append((start, end))
            if not self.search_results:
                self.current_match = -1
            elif self.current_match == -1 or self.current_match >= len(self.search_results):
                self.current_match = 0
    
    def highlight_matches(self):
        self.log_area.tag_remove("search_highlight", "1.0", tk.END)
        self.log_area.tag_remove("current_match", "1.0", tk.END)
        for start, end in self.search_results:
            self.log_area.tag_add("search_highlight", start, end)
        self.log_area.tag_configure("search_highlight", background="yellow", foreground="black")
        self.log_area.tag_configure("current_match", background="orange", foreground="black")
        self.update_current_match()
    
    def update_current_match(self):
        if 0 <= self.current_match < len(self.search_results):
            start, end = self.search_results[self.current_match]
            self.log_area.tag_remove("current_match", "1.0", tk.END)
            self.log_area.tag_add("current_match", start, end)
            if self.using_next_prev:
                self.log_area.see(start)

    def update_match_counter(self):
        total_matches = len(self.search_results)
        current = self.current_match + 1 if self.current_match >= 0 else 0
        self.match_counter.config(text=f"{current}/{total_matches} matches")

    def goto_next_match(self):
        if self.search_results:
            self.using_next_prev = True
            self.current_match = (self.current_match + 1) % len(self.search_results)
            self.update_current_match()
            self.update_match_counter()
            self.using_next_prev = False

    def goto_previous_match(self):
        if self.search_results:
            self.using_next_prev = True
            self.current_match = (self.current_match - 1) % len(self.search_results)
            self.update_current_match()
            self.update_match_counter()
            self.using_next_prev = False

    def clear_search(self):
        self.log_area.tag_remove("search_highlight", "1.0", tk.END)
        self.log_area.tag_remove("current_match", "1.0", tk.END)
        self.search_results = []
        self.current_match = -1
        self.search_active = False
        self.search_pattern = None
        self.update_match_counter()
        self.toggle_search_elements(False)
        self.search_var.set("")  # Bersihkan input pencarian

    def on_mouse_wheel(self, event):
        if hasattr(self, 'v_scrollbar'):
            if self.v_scrollbar.get()[1] < 1.0:
                self.auto_scroll = False
            else:
                self.auto_scroll = True
        else:
            print("Warning: v_scrollbar not found")

    def process_log_queue(self):
        try:
            while True:
                process_name, message = self.log_queue.get_nowait()
                self.add_log_safe(process_name, message)
                
                if self.auto_scroll:
                    self.log_area.see(tk.END)
                elif self.search_active and self.search_var.get().strip():
                    self.search_logs()
        except queue.Empty:
            pass
        finally:
            self.after(100, self.process_log_queue)

    def toggle_search_elements(self, visible):
        widgets = [self.prev_button, self.next_button, self.clear_search_button, self.match_counter]
        
        if visible:
            if all(widgets):  # Ensure all widgets are created before using them
                self.prev_button.grid(row=0, column=5, padx=(5, 0))
                self.next_button.grid(row=0, column=6, padx=(5, 0))
                self.clear_search_button.grid(row=0, column=7, padx=(5, 0))
                self.match_counter.grid(row=0, column=8, padx=(5, 0))
        else:
            for widget in widgets:
                if widget is not None:  # Check if the widget is not None before calling grid_remove
                    widget.grid_remove()
        
    def toggle_logcat(self):
        if not self.logcat_running.is_set():
            self.start_logcat()
        else:
            self.stop_logcat()

    def start_logcat(self):
        if self.logcat_running.is_set():
            self.stop_logcat()
        
        if self.app_filter.get() == "No device connected":
            self.add_log("No device connected. Cannot start logcat.", "ERROR")
            return
        
        self.logcat_running.set()
        self.logcat_btn.config(text="⏹")
        app_filter = self.app_filter.get()
        log_level = self.log_level.get()
        log_mode = self.log_mode.get()

        command = ['adb', 'logcat']

        if log_mode == "From Now":
            current_time = datetime.datetime.now().strftime("%m-%d %H:%M:%S.%f")[:-3]
            command.extend(['-T', current_time])

        if app_filter != "All Apps":
            app_name = app_filter.split('(')[0]
            if "(not running)" in app_filter:
                self.add_log(f"Waiting for {app_name} to start...", "INFO")
                self.wait_for_app_start(app_name)
            
            pid = self.run_adb_command(['adb', 'shell', 'pidof', '-s', app_name]).strip()
            if pid:
                command.extend(['--pid', pid])
            else:
                self.add_log(f"Cannot find PID for {app_name}. Logging all apps.", "WARN")

        if log_level != "All":
            command.append(f"*:{log_level[0]}")

        threading.Thread(target=self.run_logcat, args=(command,), daemon=True).start()
        self.update_idletasks()

    def wait_for_app_start(self, app_name):
        while self.logcat_running.is_set():
            pid = self.run_adb_command(['adb', 'shell', 'pidof', '-s', app_name]).strip()
            if pid:
                self.add_log(f"{app_name} has started. Beginning logcat.", "INFO")
                return
            time.sleep(1)

    def monitor_running_apps(self):
        while not self.stop_threads.is_set() and self.device_connected:
            self.update_running_apps()
            self.stop_threads.wait(timeout=2)
    
    def monitor_device_changes(self):
        def run():
            while not self.stop_threads.is_set():
                try:
                    result = self.run_adb_command(['adb', 'devices'])
                    devices = [line.split()[0] for line in result.splitlines()[1:] if line.strip()]
                    
                    if devices and not self.device_connected:
                        self.device_connected = True
                        self.after(0, self.start_running_apps_check)
                    elif not devices and self.device_connected:
                        self.device_connected = False
                        self.after(0, self.stop_running_apps_check)
                        self.after(0, lambda: self.update_app_filter(["No device connected"]))
                    
                    if not devices:
                        # Jika tidak ada perangkat, tunggu lebih lama sebelum pengecekan berikutnya
                        self.stop_threads.wait(timeout=30)
                    else:
                        self.stop_threads.wait(timeout=5)
                except Exception as e:
                    self.after(0, lambda: self.add_log(f"Error checking for devices: {str(e)}", "ERROR"))
                    self.stop_threads.wait(timeout=30)

        self.device_check_thread = threading.Thread(target=run, daemon=True)
        self.device_check_thread.start()
    
    def start_running_apps_check(self):
        if self.running_apps_check_thread is None or not self.running_apps_check_thread.is_alive():
            self.running_apps_check_thread = threading.Thread(target=self.monitor_running_apps, daemon=True)
            self.running_apps_check_thread.start()

    def stop_running_apps_check(self):
        if self.running_apps_check_thread and self.running_apps_check_thread.is_alive():
            self.stop_threads.set()
            self.running_apps_check_thread.join(timeout=1)
            self.stop_threads.clear()
            self.running_apps_check_thread = None
        
    def stop_logcat(self):
        self.logcat_running.clear()
        if 'logcat' in self.processes:
            process = self.processes['logcat']
            if process.poll() is None:
                if platform.system() == 'Windows':
                    subprocess.call(['taskkill', '/F', '/T', '/PID', str(process.pid)])
                else:
                    os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                process.terminate()
            self.add_log("Logcat stopped.", "INFO")
        self.logcat_btn.config(text="▶")
        
        with self.log_queue.mutex:
            self.log_queue.queue.clear()
        
        self.update_idletasks()
        
        # Hentikan pemeriksaan aplikasi yang berjalan jika tidak ada perangkat yang terhubung
        if not self.device_connected:
            self.stop_running_apps_check()

    def restart_logcat(self, event=None):
        if event and event.widget == self.app_filter:
            self.stop_logcat()  # Hentikan logcat yang sedang berjalan (jika ada)
            self.start_logcat()  # Mulai logcat baru
        elif self.logcat_running.is_set():
            self.stop_logcat()
            self.start_logcat()

    def update_logcat_button_state(self):
        if self.logcat_running.is_set():
            self.logcat_btn.config(text="▶")
        else:
            self.logcat_btn.config(text="⏹")
    
    def clear_logcat(self):
        self.log_area.configure(state="normal")
        self.log_area.delete('1.0', tk.END)
        self.log_area.configure(state="disabled")

    def process_logcat_line(self, line):
        pattern = r'^(\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}\.\d{3})\s+(\d+)\s+(\d+)\s+([VDIWEF])\s+(.+?)\s*:\s(.*)$'
        match = re.match(pattern, line)
        if match:
            timestamp, pid, tid, level, tag, message = match.groups()
            
            # Menggabungkan tahun saat ini dengan timestamp yang ada
            current_year = datetime.datetime.now().year
            timestamp_with_year = f"{current_year}-{timestamp}"
            timestamp = datetime.datetime.strptime(timestamp_with_year, "%Y-%m-%d %H:%M:%S.%f")
            
            log_type = "INFO"
            if level == 'V':
                log_type = "VERBOSE"
            elif level == 'D':
                log_type = "DEBUG"
            elif level == 'W':
                log_type = "WARN"
            elif level == 'E':
                log_type = "ERROR"
            elif level == 'F':
                log_type = "ASSERT"
            
            formatted_timestamp = timestamp.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            self.add_log(f"[{formatted_timestamp}] [{tag}] {message}", log_type)

    def add_log_safe(self, process_name, message):
        if process_name == 'logcat':
            self.process_logcat_line(message)
        else:
            self.add_log(f"[{process_name.capitalize()}] {message}", "INFO")
        
        if self.search_active:
            self.search_queue.put(message)

    def update_search(self, new_line):
        with self.search_lock:
            # Get the current end index of the text widget
            end_index = self.log_area.index(tk.END)
            
            # Find the last line with content
            last_line = self.log_area.index(f"{end_index} linestart - 1 lines")
            
            adjusted_line, offset = self.adjust_line(new_line)
            matches = list(self.search_pattern.finditer(adjusted_line))
            
            if matches:
                for match in matches:
                    start_offset = match.start() + offset
                    end_offset = match.end() + offset
                    
                    start = f"{last_line} + {start_offset} chars"
                    end = f"{last_line} + {end_offset} chars"
                    
                    self.search_results.append((start, end))
                    self.apply_highlight(start, end)
            
            # Update all existing highlights
            self.update_all_highlights()
            
            self.update_match_counter()
    
    def update_all_highlights(self):
        self.log_area.tag_remove("search_highlight", "1.0", tk.END)
        for start, end in self.search_results:
            try:
                self.log_area.tag_add("search_highlight", start, end)
            except tk.TclError as e:
                print(f"Error applying highlight: {e}")
                print(f"Attempted to highlight from {start} to {end}")
    
    def apply_highlight(self, start, end):
        try:
            self.log_area.tag_add("search_highlight", start, end)
        except tk.TclError as e:
            print(f"Error applying highlight: {e}")
            print(f"Attempted to highlight from {start} to {end}")

    def adjust_line(self, line):
        # Fungsi ini tetap sama seperti sebelumnya
        emoji_pattern = re.compile(r'^\s*[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]')
        match = emoji_pattern.match(line)
        if match:
            emoji_length = len(match.group(0))
            return line[emoji_length:].lstrip(), emoji_length
        return line, 0

    def add_log(self, message, log_type="INFO"):
        self.log_area.configure(state="normal")
        self.log_area.insert(tk.END, message + "\n", log_type)
        self.log_area.configure(state="disabled")
        
        if self.auto_scroll:
            self.log_area.see(tk.END)
        self.update_idletasks()

    def on_scroll(self, *args):
        current_position = float(self.v_scrollbar.get()[1])
        if current_position < 1.0:
            self.auto_scroll = False
        else:
            self.auto_scroll = True
        self.last_scroll_position = current_position

    def run_command(self, command, process_name):
        if process_name not in self.processes or self.processes[process_name].poll() is not None:
            self.add_log(f"Running {process_name}: {' '.join(command)}", "INFO")
            try:
                if platform.system() == 'Windows':
                    self.processes[process_name] = subprocess.Popen(
                        command, 
                        stdout=subprocess.PIPE, 
                        stderr=subprocess.STDOUT,
                        creationflags=subprocess.CREATE_NO_WINDOW,
                    )
                else:
                    self.processes[process_name] = subprocess.Popen(
                        command,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        preexec_fn=os.setsid,
                    )
                threading.Thread(target=self.read_output, args=(self.processes[process_name], process_name), daemon=True).start()
            except Exception as e:
                self.add_log(f"Error starting {process_name}: {str(e)}", "ERROR")
        else:
            self.add_log(f"{process_name.capitalize()} process is already running, please wait for it to finish.", "INFO")

    def read_output(self, process, process_name):
        while True:
            try:
                line = process.stdout.readline()
                if not line:
                    break
                try:
                    decoded_line = line.decode('utf-8').strip()
                except UnicodeDecodeError:
                    try:
                        decoded_line = line.decode('iso-8859-1').strip()
                    except UnicodeDecodeError:
                        decoded_line = line.decode('utf-8', errors='replace').strip()
                
                if not self.logcat_running.is_set() and process_name == 'logcat':
                    break
                self.log_queue.put((process_name, decoded_line))
            except Exception as e:
                self.log_queue.put((process_name, f"Error reading output: {str(e)}"))
                break
        
        rc = process.wait()
        if rc != 0:
            self.log_queue.put((process_name, f"Error: {process_name.capitalize()} process exited with code {rc}"))
        else:
            self.log_queue.put((process_name, f"{process_name.capitalize()} process completed successfully"))
        del self.processes[process_name]
        if process_name == 'logcat':
            self.after(0, self.stop_logcat)  # Gunakan stop_logcat untuk memastikan tombol diperbarui

    def update_running_apps(self):
        try:
            if not self.device_connected:
                self.after(0, lambda: self.update_app_filter(["No device connected"]))
                return

            result = self.run_adb_command(['adb', 'shell', 'ps'])
            apps = ["All Apps"]
            current_apps = set()
            for line in result.splitlines():
                if 'S' in line:
                    parts = line.split()
                    pid = parts[1]
                    app_name = parts[-1]
                    if app_name.startswith('com.') and not app_name.startswith(('com.android.', 'com.google.', 'com.sec.', 'com.samsung.')):
                        app_entry = f"{app_name}({pid})"
                        apps.append(app_entry)
                        current_apps.add(app_name)
            
            for app in self.previously_selected_apps:
                if app.split('(')[0] not in current_apps:
                    apps.append(f"{app.split('(')[0]}(not running)")
            
            self.after(0, lambda: self.update_app_filter(apps))
        except Exception as e:
            self.after(0, lambda: self.add_log(f"Failed to get list of running apps: {str(e)}", "ERROR"))


    def update_app_filter(self, apps):
        current_value = self.app_filter.get()
        self.app_filter.config(values=apps)
        # If the current value is not in the new list of apps
        if current_value not in apps:
            # Check if it's a previously selected app (now not running)
            app_name = current_value.split('(')[0]
            not_running_entry = f"{app_name}(not running)"
            if not_running_entry in apps:
                self.app_filter.set(not_running_entry)
            else:
                self.app_filter.set("All Apps")
        else:
            self.app_filter.set(current_value)
        
        # Update the set of previously selected apps
        if current_value != "All Apps" and current_value != "No device connected":
            self.previously_selected_apps.add(current_value.split('(')[0])
        
        if apps == ["No device connected"] and self.logcat_running.is_set():
            self.stop_logcat()

    def run_adb_command(self, command):
        adb_path = self.find_adb()
        if adb_path is None:
            self.add_log("Error: adb command not found. Please ensure Android SDK is installed and adb is in your PATH.", "ERROR")
            return ""

        if command[0] == "adb":
            command[0] = adb_path

        try:
            result = subprocess.run(command, check=True, capture_output=True, text=True)
            return result.stdout
        except subprocess.CalledProcessError as e:
            self.add_log(f"Error executing ADB command: {e}", "ERROR")
            return e.stderr
        
    def find_adb(self):
        possible_locations = [
            '/usr/local/bin/adb',
            '/opt/homebrew/bin/adb',
            os.path.expanduser('~/Library/Android/sdk/platform-tools/adb'),
            os.path.expanduser('~/Android/Sdk/platform-tools/adb'),
            '/Users/Shared/Android/platform-tools/adb',
        ]
        
        path_dirs = os.environ.get('PATH', '').split(os.pathsep)
        for dir in path_dirs:
            possible_locations.append(os.path.join(dir, 'adb'))
        
        for location in possible_locations:
            if os.path.isfile(location):
                return location
        
        return None
    
    def run_logcat(self, command):
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            bufsize=1,
            universal_newlines=False  # Ubah ke False agar kita bisa menangani bytes
        )

        for line in iter(process.stdout.readline, b''):  # Baca sebagai bytes
            if not self.logcat_running.is_set():
                break
            try:
                decoded_line = line.decode('utf-8').strip()
            except UnicodeDecodeError:
                try:
                    decoded_line = line.decode('iso-8859-1').strip()
                except UnicodeDecodeError:
                    decoded_line = line.decode('utf-8', errors='replace').strip()
            
            self.log_queue.put(('logcat', decoded_line))

        process.terminate()
        process.wait()