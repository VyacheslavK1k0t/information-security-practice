from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from jose import JWTError
from datetime import datetime, timezone  # Додано для аналізу часу входу (off-hours)

from app.database import get_db
from app.models import User
from app.security import hash_password, verify_password 
from app.auth.jwt_handler import create_access_token, create_refresh_token, verify_token
from app.auth.dependencies import get_current_user
from app.schemas import (
    UserCreate, 
    UserResponse, 
    LoginRequest, 
    TokenResponse, 
    TokenRefreshRequest, 
    UserInfo
)

# Імпортуємо лімітер із твого файлу middleware (Пункт 5.5)
from app.middleware.rate_limiter import limiter

# Імпорти системи аудиту та журналювання безпеки (Пункт 5.6)
from app.audit.logger import log_login_success, log_login_failed
from app.audit.detector import check_brute_force, check_off_hours_access

router = APIRouter(prefix="/auth", tags=["Authentication"])

# =====================================================================
# 1. РЕЄСТРАЦІЯ
# =====================================================================
@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Користувач вже існує")
    
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        full_name=user_data.full_name,
        password_hash=hash_password(user_data.password),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# =====================================================================
# 2. ВХІД (З лімітером, захистом від Brute Force та аудитом безпеки)
# =====================================================================
@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/minute")  # Обмеження slowapi: макс. 5 спроб за хвилину з однієї IP (Пункт 5.5)
def login(
    request: Request,  # ОБОВ'ЯЗКОВИЙ параметр для роботи декоратора slowapi та зчитування IP
    login_data: LoginRequest,  # Дані валідуються суворо через Pydantic-схему з JSON body
    db: Session = Depends(get_db)
):
    # Зчитуємо IP-адресу клієнта
    ip = request.client.host if request.client else "unknown"

    # [АУДИТ] 1. Перевірка на Brute Force ДО перевірки пароля та звернення до моделей
    if check_brute_force(db, ip):
        log_login_failed(db, login_data.username, ip, "brute_force_blocked")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Забагато невдалих спроб. Спробуйте пізніше."
        )

    # Шукаємо користувача за даними з JSON-моделі
    user = db.query(User).filter(User.username == login_data.username).first()
    
    # Перевірка наявності користувача та відповідності пароля
    if not user or not verify_password(login_data.password, user.password_hash):
        # [АУДИТ] Логуємо невдалу спробу через невірні облікові дані
        log_login_failed(db, login_data.username, ip, "invalid_credentials")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Невірний логін або пароль"
        )
    
    if not user.is_active:
        # [АУДИТ] Логуємо спробу входу у неактивний обліковий запис
        log_login_failed(db, login_data.username, ip, "account_deactivated")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Акаунт деактивовано"
        )
    
    # [АУДИТ] 2. Перевірка на вхід у нетиповий нічний час (00:00 - 06:00)
    check_off_hours_access(db, user.id, user.username, ip, datetime.now(timezone.utc).hour)

    # [АУДИТ] 3. Логуємо успішний вхід користувача в систему
    log_login_success(db, user.id, user.username, ip)
    
    role = user.roles[0].name if user.roles else "student"
    
    access_token = create_access_token(user.id, role)
    refresh_token = create_refresh_token(user.id)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token
    )

# =====================================================================
# 3. ОНОВЛЕННЯ ТОКЕНА
# =====================================================================
@router.post("/refresh", response_model=TokenResponse)
def refresh_token(body: TokenRefreshRequest, db: Session = Depends(get_db)):
    """Оновлення access токена за допомогою refresh токена."""
    try:
        payload = verify_token(body.refresh_token)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Невалідний або протермінований refresh token"
        )

    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Потрібен refresh token, а не access token"
        )

    user_id = int(payload["sub"])
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Користувача не знайдено")

    role = user.roles[0].name if user.roles else "student"
    new_access = create_access_token(user_id, role)
    new_refresh = create_refresh_token(user_id)

    return TokenResponse(
        access_token=new_access, 
        refresh_token=new_refresh
    )

# =====================================================================
# 4. ПРОФІЛЬ
# =====================================================================
@router.get("/me", response_model=UserInfo)
def get_me(current_user: User = Depends(get_current_user)):
    """Повертає інформацію про поточного увійшовшого користувача."""
    role = current_user.roles[0].name if current_user.roles else "student"
    return UserInfo(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        full_name=current_user.full_name,
        role=role
    )