# app/audit/router.py

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from typing import Optional
from app.database import get_db
from app.auth.dependencies import require_role
from app.audit.models import AuditLog
from app.audit.detector import get_security_stats

router = APIRouter()

@router.get("/audit-log")
async def get_audit_log(
    action: Optional[str] = Query(None),
    username: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    hours: int = Query(24, ge=1, le=720),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user=Depends(require_role("admin")),
):
    """Перегляд журналу аудиту (тільки для адміністраторів)."""
    since = datetime.now(timezone.utc) - timedelta(hours=hours)
    query = db.query(AuditLog).filter(AuditLog.timestamp >= since)
    
    if action: 
        query = query.filter(AuditLog.action == action)
    if username: 
        query = query.filter(AuditLog.username == username)
    if status: 
        query = query.filter(AuditLog.status == status)
        
    total = query.count()
    logs = query.order_by(AuditLog.timestamp.desc()).offset(offset).limit(limit).all()
    
    return {
        "total": total,
        "logs": [
            {
                "id": l.id,
                "timestamp": l.timestamp.isoformat(),
                "action": l.action,
                "status": l.status,
                "user_id": l.user_id,
                "username": l.username,
                "ip_address": l.ip_address,
                "endpoint": l.endpoint,
                "details": l.details
            } for l in logs
        ]
    }

@router.get("/security-stats")
async def security_statistics(
    hours: int = Query(24, ge=1, le=720),
    db: Session = Depends(get_db),
    current_user=Depends(require_role("admin")),
):
    """Статистика безпеки за період."""
    return get_security_stats(db, hours)