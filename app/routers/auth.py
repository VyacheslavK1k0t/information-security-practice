from fastapi import APIRouter, Depends, HTTPException, status, Request  # Додано Request
from sqlalchemy.orm import Session
from jose import JWTError

from app.database import get_db
from app.models import User
from app.security import hash_password, verify_password 
from app.auth.jwt_handler import create_access_token, create_refresh_token, verify_token
from app.auth.dependencies import get_current_user
from app.schemas import (
    UserCreate, 
    UserResponse, 
    LoginRequest,  # Додано для суворої валідації входу
    TokenResponse, 
    TokenRefreshRequest, 
    UserInfo
)

# Імпортуємо лімітер із нашого файлу middleware (Пункт 5.5)
from app.middleware.rate_limiter import limiter

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
# 2. ВХІД (З захистом від Brute Force та JSON-валідацією)
# =====================================================================
@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/minute")  # Обмеження: макс. 5 спроб входу за хвилину з однієї IP (Пункт 5.5)
def login(
    request: Request,  # ОБОВ'ЯЗКОВИЙ параметр для роботи декоратора slowapi
    login_data: LoginRequest,  # Дані тепер валідуються суворо через Pydantic-схему з JSON body
    db: Session = Depends(get_db)
):
    # Шукаємо користувача за даними з JSON-моделі
    user = db.query(User).filter(User.username == login_data.username).first()
    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Невірний логін або пароль"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Акаунт деактивовано"
        )
    
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