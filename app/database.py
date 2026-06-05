from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session # Додаємо Session

DATABASE_URL = "sqlite:///./data/app.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

class Base(DeclarativeBase):
    pass

def get_db():
    """Генератор сесій бази даних для Dependency Injection."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()