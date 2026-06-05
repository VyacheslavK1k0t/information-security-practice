# scripts/generate_key.py
 
from cryptography.fernet import Fernet
 
key = Fernet.generate_key()
print(f"Згенерований ключ Fernet:")
print(f"ENCRYPTION_KEY={key.decode()}")
print("-" * 30)
print("Цей ключ — єдиний спосіб розшифрувати дані.")
print("Втрата ключа = втрата всіх зашифрованих даних.")
print("Ніколи не додавайте його у Git!")
