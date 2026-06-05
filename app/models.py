from datetime import datetime
from sqlalchemy import (Column, Integer, String, Float, DateTime, ForeignKey, Table, Text, Boolean)
from sqlalchemy.orm import relationship
from app.database import Base
from app.crypto.encryption import encrypt_field, decrypt_field

# Зв’язок User <-> Role (M:N)
user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("role_id", Integer, ForeignKey("roles.id"), primary_key=True),
)

# Зв’язок Role <-> Permission (M:N)
role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", Integer, ForeignKey("roles.id"), primary_key=True),
    Column("permission_id", Integer, ForeignKey("permissions.id"), primary_key=True),
)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)  # Додано для виправлення AttributeError

    group_id = Column(Integer, ForeignKey("groups.id"), nullable=True)

    # Зашифровані поля
    _encrypted_email = Column("encrypted_email", String, nullable=False)
    _encrypted_phone = Column("encrypted_phone", String, nullable=True)

    # Зв'язки
    roles = relationship("Role", secondary=user_roles, back_populates="users")
    group = relationship("Group", back_populates="students")
    grades = relationship("Grade", back_populates="student", foreign_keys="[Grade.student_id]")

    @property
    def email(self) -> str:
        return decrypt_field(self._encrypted_email)

    @email.setter
    def email(self, value: str):
        self._encrypted_email = encrypt_field(value)

    @property
    def phone(self) -> str:
        if self._encrypted_phone:
            return decrypt_field(self._encrypted_phone)
        return None

    @phone.setter
    def phone(self, value: str):
        if value:
            self._encrypted_phone = encrypt_field(value)

class Role(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text, nullable=True)

    users = relationship("User", secondary=user_roles, back_populates="roles")
    permissions = relationship("Permission", secondary=role_permissions, back_populates="roles")

class Permission(Base):
    __tablename__ = "permissions"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)

    roles = relationship("Role", secondary=role_permissions, back_populates="permissions")

class Group(Base):
    __tablename__ = "groups"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(20), unique=True, nullable=False)
    department = Column(String(100), nullable=False)
    year = Column(Integer, nullable=False)

    students = relationship("User", back_populates="group")

class Subject(Base):
    __tablename__ = "subjects"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    credits = Column(Float, nullable=False)
    semester = Column(Integer, nullable=False)

    grades = relationship("Grade", back_populates="subject")

class Grade(Base):
    __tablename__ = "grades"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    grade = Column(Integer, nullable=False)
    date_assigned = Column(DateTime, default=datetime.utcnow)
    assigned_by = Column(Integer, ForeignKey("users.id"), nullable=False)

    student = relationship("User", back_populates="grades", foreign_keys=[student_id])
    subject = relationship("Subject", back_populates="grades")
    teacher = relationship("User", foreign_keys=[assigned_by])