# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base 

# Імпорти роутерів
from app.routers.auth import router as auth_router
from app.routes.students import router as students_router
from app.routes.teachers import router as teachers_router
from app.routes.admin import router as admin_router

# Імпорти системи аудиту та журналювання безпеки (Пункт 5.7)
from app.audit.middleware import AuditMiddleware
from app.audit.router import router as audit_router

# Імпорти для систем безпеки та лімітування запитів (Пункти 5.4, 5.5, 5.6)
from app.middleware.security_headers import SecurityHeadersMiddleware
from app.middleware.rate_limiter import limiter
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler

# Створюємо таблиці в БД при старті, якщо їх немає
def init_db():
    Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Електронний деканат API",
    version="1.0.0"
)

# Налаштування Rate Limiter (Пункт 5.5)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# 1. Підключаємо HTTP Security Headers Middleware (Пункт 5.4)
app.add_middleware(SecurityHeadersMiddleware)

# 2. Налаштування суворого CORS (Пункт 5.6)
# Забороняємо універсальну зірочку (*). Дозволяємо доступ лише локальному фронтенду та нашому API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",   # Стандартний порт для React / Vue фронтенду
        "http://localhost:3010",   # Твій Docker-порт бекенду (щоб працював Swagger)
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

# 3. Підключаємо Audit Middleware для автоматичного логування запитів (Пункт 5.7)
app.add_middleware(AuditMiddleware)

# Викликаємо функцію створення таблиць
@app.on_event("startup")
def startup_event():
    init_db()

# Підключення роутерів
app.include_router(auth_router)       # Підключаємо автентифікацію (вже з лімітером та аудитом)
app.include_router(students_router)   # Підключаємо студентів
app.include_router(teachers_router)   # Підключаємо викладачів
app.include_router(admin_router)      # Підключаємо адміна

# Підключаємо адмін-роутер журналу аудиту безпеки (Пункт 5.7)
app.include_router(audit_router, prefix="/admin", tags=["audit"])