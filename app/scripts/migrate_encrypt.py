# scripts/migrate_encrypt.py
 
from app.database import SessionLocal
from app.crypto.encryption import encrypt_field
from sqlalchemy import text
 
 
def migrate():
    db = SessionLocal()
    try:
        result = db.execute(text("SELECT id, email FROM users WHERE encrypted_email IS NULL"))
        users = result.fetchall()
        print(f"Знайдено {len(users)} записів для міграції")
 
        for user_id, email in users:
            encrypted = encrypt_field(email)
            db.execute(
                text("UPDATE users SET encrypted_email = :enc WHERE id = :id"),
                {"enc": encrypted, "id": user_id}
            )
            print(f"  User #{user_id}: email зашифровано")
 
        db.commit()
        print(f"Міграція завершена: {len(users)} записів зашифровано")
    except Exception as e:
        db.rollback()
        print(f"Помилка міграції: {e}")
    finally:
        db.close()
 
 
if __name__ == "__main__":
    migrate()
