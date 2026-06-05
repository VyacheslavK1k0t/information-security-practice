# app/main.py
from fastapi import FastAPI
from app.database import engine, Base 

# 1. ПРАВИЛЬНИЙ ІМПОРТ: імпортуємо роутер з вашого файлу app/auth.py
from app.routers.auth import router as auth_router

# 2. Імпортуємо роутери з папки app/routes/
from app.routes.students import router as students_router
from app.routes.teachers import router as teachers_router
from app.routes.admin import router as admin_router


# Створюємо таблиці в БД при старті, якщо їх немає
def init_db():
    Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Електронний деканат API",
    version="1.0.0"
)

# Викликаємо функцію створення таблиць
@app.on_event("startup")
def startup_event():
    init_db()

# 3. ПРАВИЛЬНЕ ПІДКЛЮЧЕННЯ: передаємо саме ті змінні, які імпортували вище
app.include_router(auth_router)       # Підключаємо автентифікацію
app.include_router(students_router)   # Підключаємо студентів
app.include_router(teachers_router)   # Підключаємо викладачів
app.include_router(admin_router)      # Підключаємо адміна
