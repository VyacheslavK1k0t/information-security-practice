# app/audit/detector.py

from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.audit.models import AuditLog
from app.audit.logger import log_event

def check_brute_force(db: Session, ip_address: str,
                      threshold: int = 5, window_minutes: int = 5) -> bool:
    """Перевіряє ознаки Brute Force з даної IP. True = поріг перевищено."""
    since = datetime.now(timezone.utc) - timedelta(minutes=window_minutes)
    
    failed_count = db.query(func.count(AuditLog.id)).filter(
        AuditLog.action == "login_failed",
        AuditLog.ip_address == ip_address,
        AuditLog.timestamp >= since,
    ).scalar()
    
    if failed_count >= threshold:
        log_event(
            db=db, 
            action="brute_force_detected", 
            status="warning",
            ip_address=ip_address,
            details={"failed_attempts": failed_count, "window_minutes": window_minutes}
        )
        return True
    return False


def check_off_hours_access(db, user_id, username, ip, hour):
    """Перевіряє вхід у нетиповий час (між 00:00 та 06:00)."""
    if 0 <= hour < 6:
        log_event(
            db=db, 
            action="off_hours_login", 
            status="warning",
            user_id=user_id, 
            username=username, 
            ip_address=ip,
            details={"login_hour": hour}
        )
        return True
    return False


def get_security_stats(db: Session, hours: int = 24) -> dict:
    """Статистика безпеки за останні N годин."""
    since = datetime.now(timezone.utc) - timedelta(hours=hours)
    
    total = db.query(func.count(AuditLog.id)).filter(
        AuditLog.timestamp >= since
    ).scalar()
    
    failed = db.query(func.count(AuditLog.id)).filter(
        AuditLog.action == "login_failed",
        AuditLog.timestamp >= since
    ).scalar()
    
    denied = db.query(func.count(AuditLog.id)).filter(
        AuditLog.action == "access_denied",
        AuditLog.timestamp >= since
    ).scalar()
    
    brute = db.query(func.count(AuditLog.id)).filter(
        AuditLog.action == "brute_force_detected",
        AuditLog.timestamp >= since
    ).scalar()
    
    grades = db.query(func.count(AuditLog.id)).filter(
        AuditLog.action == "grade_update",
        AuditLog.timestamp >= since
    ).scalar()
    
    return {
        "period_hours": hours, 
        "total_events": total,
        "failed_logins": failed, 
        "access_denied": denied,
        "brute_force_alerts": brute, 
        "grade_changes": grades
    }