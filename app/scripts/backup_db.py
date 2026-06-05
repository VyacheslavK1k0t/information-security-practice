# scripts/backup_db.py
 
import shutil, os
from datetime import datetime
from cryptography.fernet import Fernet
from app.crypto.key_manager import get_encryption_key
 
 
def create_backup():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    db_path = "/app_code/data/app.db"
    backup_dir = "/app_code/data/backups"
    os.makedirs(backup_dir, exist_ok=True)
 
    # 1. Копіюємо файл БД
    backup_path = f"{backup_dir}/dekanat_backup_{timestamp}.db"
    shutil.copy2(db_path, backup_path)
 
    # 2. Шифруємо копію
    f = Fernet(get_encryption_key())
    with open(backup_path, "rb") as file:
        data = file.read()
    encrypted_data = f.encrypt(data)
    encrypted_path = f"{backup_path}.enc"
    with open(encrypted_path, "wb") as file:
        file.write(encrypted_data)
 
    # 3. Видаляємо незашифровану копію
    os.remove(backup_path)
    print(f"Зашифрована копія: {encrypted_path}")
    return encrypted_path
 
 
if __name__ == "__main__":
    create_backup()
