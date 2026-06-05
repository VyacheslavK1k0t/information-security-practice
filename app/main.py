from fastapi import FastAPI
from app.database import engine, Base  # Імпортуйте engine та Base
from app.routers import auth

# Створюємо таблиці в БД при старті, якщо їх немає
def init_db():
    Base.metadata.create_all(bind=engine)

app = FastAPI()

# Викликаємо функцію створення таблиць
@app.on_event("startup")
def startup_event():
    init_db()

# Ваші роутери
app.include_router(auth.router)