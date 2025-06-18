# app/tabs/android_install_tab.py
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import subprocess
import threading
import platform
import signal
import re
from src.modules import Modules
from app.tabs.popup import ResponseOpenAPI
from app.custom.custom_text import CustomText
import shutil

class AndroidInstallTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding="20")
        self.processes = {}
        self.create_widgets()

    def create_widgets(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        # Android Mirror Button
        self.android_mirror_btn = ttk.Button(self, text="Open Android Mirror", command=self.open_android_mirror)
        self.android_mirror_btn.grid(row=0, column=0, sticky="w", pady=(0, 10))

        # Install APK Frame
        install_frame = ttk.LabelFrame(self, text="Install APK", padding="10")
        install_frame.grid(row=1, column=0, sticky="nsew")
        install_frame.columnconfigure(1, weight=1)

        # File Browser
        self.file_path = tk.StringVar()
        ttk.Button(install_frame, text="Browse", command=self.open_file).grid(row=0, column=0, sticky="w", pady=5)
        ttk.Entry(install_frame, textvariable=self.file_path, state="readonly").grid(row=0, column=1, sticky="ew", padx=(5, 0), pady=5)

        # Install/Stop Button
        self.install_stop_btn = ttk.Button(install_frame, text="Install APK", command=self.toggle_install_stop)
        self.install_stop_btn.grid(row=1, column=0, columnspan=2, pady=10)
        self.install_stop_btn.config(state="disabled")

        # ADB Wireless Connection Frame
        wireless_frame = ttk.LabelFrame(self, text="ADB Wireless Connection", padding="10")
        wireless_frame.grid(row=2, column=0, sticky="nsew", pady=(10, 0))
        wireless_frame.columnconfigure(1, weight=1)

        # IP Address entry
        tk.Label(wireless_frame, text="Device IP:").grid(row=0, column=0, sticky="w", pady=5)
        self.ip_entry = ttk.Entry(wireless_frame)
        self.ip_entry.grid(row=0, column=1, sticky="ew", padx=(5, 0), pady=5)

        # Konfigurasi kolom di wireless_frame
        for i in range(4):
            wireless_frame.columnconfigure(i, weight=1)

        # Tombol-tombol disusun berjejer
        ttk.Button(wireless_frame, text="Enable TCP Mode", command=lambda: threading.Thread(target=self.enable_tcp).start()).grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        ttk.Button(wireless_frame, text="Connect Device", command=lambda: threading.Thread(target=self.connect_device).start()).grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        ttk.Button(wireless_frame, text="List Devices", command=lambda: threading.Thread(target=self.list_devices).start()).grid(row=1, column=2, padx=5, pady=5, sticky="ew")
        ttk.Button(wireless_frame, text="Disconnect", command=lambda: threading.Thread(target=self.disconnect_device).start()).grid(row=1, column=3, padx=5, pady=5, sticky="ew")
        
        # Output Area
        self.output_area = CustomText(self, height=10, wrap="word")
        self.output_area.grid(row=3, column=0, sticky="nsew", pady=(10, 0))

        # Scrollbar for Output Area
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.output_area.yview)
        scrollbar.grid(row=3, column=1, sticky="ns", pady=(10, 0))
        self.output_area.configure(yscrollcommand=scrollbar.set)

    def open_file(self):
        file_path = filedialog.askopenfilename(filetypes=[('APK Files', '*.apk')])
        if file_path:
            self.file_path.set(file_path)
            self.install_stop_btn.config(state="normal", text="Install APK")

    def open_android_mirror(self):
        self.run_command('scrcpy', 'mirror')

    def toggle_install_stop(self):
        if self.install_stop_btn["text"] == "Install APK":
            self.install_apk_android()
        else:
            self.stop_installation()

    def install_apk_android(self):
        path_install = self.file_path.get()
        if path_install:
            self.output_area.delete('1.0', tk.END)
            self.install_stop_btn.config(text="Stop Installation")
            
            command = ["adb", "install", "-r", path_install]
            self.update_output(f"Running command: {' '.join(command)}")
            
            threading.Thread(target=self.run_install_command, args=(command,), daemon=True).start()
        else:
            messagebox.showinfo('Response', 'Please select an APK file first')
    
    def run_install_command(self, command):
        try:
            output = self.run_adb_command(command)
            for line in output.splitlines():
                self.update_output(line)
            
            if "Success" in output:
                self.update_output("APK installed successfully.")
            else:
                self.update_output("Installation may have failed. Please check the output above.")
        except Exception as e:
            self.update_output(f"Error during installation: {str(e)}")
        finally:
            self.install_stop_btn.config(text="Install APK")
            
    def stop_installation(self):
        if 'install' in self.processes:
            process = self.processes['install']
            if process.poll() is None:  # Check if process is still running
                if platform.system() == 'Windows':
                    subprocess.call(['taskkill', '/F', '/T', '/PID', str(process.pid)])
                else:
                    os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                self.update_output("Installation process stopped by user.")
            self.install_stop_btn.config(text="Install APK")

    def run_command(self, command, process_name):
        if process_name == 'install':
            adb_path = self.find_adb()
            if adb_path is None:
                self.update_output("Error: adb command not found. Please ensure Android SDK is installed and adb is in your PATH.")
                return
            command = command.replace('adb', adb_path)

        if process_name not in self.processes or self.processes[process_name].poll() is not None:
            self.update_output(f"Running {process_name}: {command}")
            if platform.system() == 'Windows':
                self.processes[process_name] = subprocess.Popen(
                    command, 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.STDOUT,
                    shell=True,
                    text=True,
                    bufsize=1,
                    universal_newlines=True
                )
            else:
                self.processes[process_name] = subprocess.Popen(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    shell=True,
                    text=True,
                    bufsize=1,
                    universal_newlines=True,
                    preexec_fn=os.setsid
                )
            threading.Thread(target=self.execute_command, args=(self.processes[process_name], process_name), daemon=True).start()
        else:
            self.update_output(f"{process_name.capitalize()} process is already running, please wait for it to finish.")

    def execute_command(self, process, process_name):
        for line in iter(process.stdout.readline, ''):
            self.update_output(f"[{process_name.capitalize()}] {line.strip()}")
        rc = process.wait()
        if rc != 0:
            self.update_output(f"Error: {process_name.capitalize()} process exited with code {rc}")
        else:
            self.update_output(f"{process_name.capitalize()} process completed successfully")
        del self.processes[process_name]
        if process_name == 'install':
            self.install_stop_btn.config(text="Install APK")

    def update_output(self, text):
        self.output_area.configure(state="normal")
        self.output_area.insert(tk.END, text + "\n")
        self.output_area.configure(state="disabled")
        self.output_area.see(tk.END)
        self.update_idletasks()

    # New methods for ADB Wireless Connection
    def validate_ip(self, ip):
        pattern = r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$"
        return re.match(pattern, ip) is not None

    def run_adb_command(self, command):
        adb_path = self.find_adb()
        if adb_path is None:
            return "Error: adb command not found. Please ensure Android SDK is installed and adb is in your PATH."
        if command[0] == "adb":
            command[0] = adb_path
        try:
            print(f'Running adb command : {command}')
            result = subprocess.run(command, check=True, capture_output=True, text=True)
            return result.stdout
        except subprocess.CalledProcessError as e:
            return e.stderr

    def enable_tcp(self):
        output = self.run_adb_command(["adb", "tcpip", "5555"])
        self.update_output(output or "ADB TCP mode enabled on port 5555")

    def connect_device(self):
        ip = self.ip_entry.get()
        if not self.validate_ip(ip):
            self.update_output("Error: Invalid IP address")
            return
        
        # Start the ADB server
        start_output = self.run_adb_command(["adb", "start-server"])
        self.update_output("ADB server started.")
        
        # Connect to the device
        output = self.run_adb_command(["adb", "connect", f"{ip}:5555"])
        self.update_output(f"Connection Result: {output}")

    def disconnect_device(self):
        ip = self.ip_entry.get()
        if not self.validate_ip(ip):
            self.update_output("Error: Invalid IP address")
            return
        
        # Disconnect the specific device
        output = self.run_adb_command(["adb", "disconnect", f"{ip}:5555"])
        self.update_output(f"Disconnection Result: {output}")
        
        # Kill the ADB server
        kill_output = self.run_adb_command(["adb", "kill-server"])
        self.update_output("ADB server killed. All connections have been reset.")
        
    def list_devices(self):
        output = self.run_adb_command(["adb", "devices", "-l"])
        devices = output.strip().split('\n')[1:]  # Skip the first line (header)
        
        if not devices:
            self.update_output("No devices connected.")
        else:
            self.update_output("Connected Devices:")
            for device in devices:
                if device.strip():
                    parts = device.split()
                    device_id = parts[0]
                    if ':5555' in device_id:  # This is a Wi-Fi connected device
                        ip = device_id.split(':')[0]
                        self.update_output(f"  IP: {ip} (Wi-Fi)")
                    else:
                        self.update_output(f"  {device}")

    def find_adb(self):
        # Daftar kemungkinan lokasi ADB
        possible_locations = [
            '/usr/local/bin/adb',
            '/opt/homebrew/bin/adb',
            os.path.expanduser('~/Library/Android/sdk/platform-tools/adb'),
            os.path.expanduser('~/Android/Sdk/platform-tools/adb'),
            '/Users/Shared/Android/platform-tools/adb',
        ]
        
        # Cek PATH
        path_dirs = os.environ.get('PATH', '').split(os.pathsep)
        for dir in path_dirs:
            possible_locations.append(os.path.join(dir, 'adb'))
        
        for location in possible_locations:
            if os.path.isfile(location):
                return location
        
        return None