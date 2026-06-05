import re
from pydantic import BaseModel, field_validator, EmailStr

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    full_name: str
    password: str

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v):
        """Перевірка складності пароля."""
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
        from_attributes = True # Для Pydantic v2 (замість orm_mode)

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    message: str
    user_id: int
    username: str
    roles: list[str]
