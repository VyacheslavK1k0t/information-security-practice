from sqlalchemy import Column, Integer, String, DateTime, Text, Index
from datetime import datetime, timezone
from app.database import Base

class AuditLog(Base):
    """Таблиця аудиту безпеки. Зберігає кожну значиму подію за правилом 5W."""
    __tablename__ = "audit_log"

    id = Column(Integer, primary_key=True, index=True)

    # WHO — хто виконав дію
    user_id = Column(Integer, nullable=True)
    username = Column(String(50), nullable=True)
    ip_address = Column(String(45), nullable=False)

    # WHAT — що сталося
    action = Column(String(50), nullable=False)
    resource = Column(String(100), nullable=True)

    # WHEN — коли
    timestamp = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False, index=True
    )

    # WHERE — де (який ендпоінт)
    http_method = Column(String(10), nullable=True)
    endpoint = Column(String(200), nullable=True)

    # WHY — результат
    status_code = Column(Integer, nullable=True)
    status = Column(String(20), nullable=False)
    details = Column(Text, nullable=True)

    # Індекси для швидкого пошуку
    __table_args__ = (
        Index("ix_audit_action_ts", "action", "timestamp"),
        Index("ix_audit_user_ts", "user_id", "timestamp"),
        Index("ix_audit_ip_action", "ip_address", "action"),
    )