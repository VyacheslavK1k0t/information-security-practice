# app/schemas.py
import re
from pydantic import BaseModel, field_validator, EmailStr, Field

class UserCreate(BaseModel):
    username: str = Field(
        ..., 
        min_length=3, 
        max_length=30, 
        description="Логін користувача (3-30 символів)"
    )
    email: EmailStr = Field(..., description="Електронна пошта")
    full_name: str = Field(
        ..., 
        min_length=2, 
        max_length=100, 
        description="Повне ім'я/ПІБ (2-100 символів)"
    )
    password: str = Field(
        ..., 
        min_length=8, 
        max_length=128, 
        description="Пароль (мінімум 8 символів)"
    )

    @field_validator("username")
    @classmethod
    def validate_username(cls, v):
        """Дозволяємо лише безпечні символи: латиницю, цифри та знак підкреслення."""
        if not re.match(r"^[a-zA-Z0-9_]+$", v):
            raise ValueError("Логін може містити лише латинські літери, цифри та знак підкреслення (_)")
        return v

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, v):
        """Забороняємо небезпечні спецсимволи HTML-тегів та кавичок (захист від XSS)."""
        if re.search(r"[<>&\"']", v):
            raise ValueError("Повне ім'я не може містити спецсимволи < > & \" '")
        return v.strip()

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v):
        """Перевірка складності пароля на рівні бекенду."""
        if len(v) < 8:
            raise ValueError("Пароль має бути довшим за 8 символів")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Пароль має містити хоча б одну велику літеру")
        if not re.search(r"[a-z]", v):
            raise ValueError("Пароль має містити хоча б одну малу літеру")
        if not re.search(r"[0-9]", v):
            raise ValueError("Пароль має містити хоча б одну цифру")
        return v

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: str

    class Config:
        from_attributes = True  # Для Pydantic v2 (замість orm_mode)

class LoginRequest(BaseModel):
    # Додано обмеження довжини для захисту від DoS-атак довгими рядками
    username: str = Field(..., max_length=30)
    password: str = Field(..., max_length=128)

class LoginResponse(BaseModel):
    message: str
    user_id: int
    username: str
    roles: list[str]

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenRefreshRequest(BaseModel):
    refresh_token: str

class UserInfo(BaseModel):
    id: int
    username: str
    email: str
    full_name: str
    role: str

    class Config:
        from_attributes = True