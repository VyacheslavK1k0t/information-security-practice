# app/crypto/key_manager.py
import os
import sys

def get_encryption_key() -> bytes:
    """Отримує ключ шифрування зі змінної оточення."""
    key = os.getenv("ENCRYPTION_KEY")
    if not key:
        print("КРИТИЧНА ПОМИЛКА: ENCRYPTION_KEY не встановлено!")
        print("   Запустіть: python scripts/generate_key.py")
        sys.exit(1)
    return key.encode()