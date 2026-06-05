from passlib.context import CryptContext
 
# Налаштування контексту хешування
# schemes=["bcrypt"] — використовуємо Bcrypt як основний алгоритм
# deprecated="auto" — автоматично позначає старі алгоритми як застарілі
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
 
 
def hash_password(password: str) -> str:
	"""
	Хешує пароль за допомогою Bcrypt.
	Автоматично генерує унікальну сіль.
   
	Args:
    	password: Пароль у відкритому вигляді
	Returns:
    	Bcrypt-хеш (60 символів)
	"""
	return pwd_context.hash(password)
 
 
def verify_password(plain_password: str, hashed_password: str) -> bool:
	"""
	Перевіряє пароль проти збереженого хешу.
   
	Args:
    	plain_password: Пароль, введений користувачем
    	hashed_password: Хеш з бази даних
	Returns:
    	True якщо пароль правильний, False інакше
	"""
	return pwd_context.verify(plain_password, hashed_password)
