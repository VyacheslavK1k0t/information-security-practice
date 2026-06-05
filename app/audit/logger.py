# app/audit/logger.py
 
import json, logging
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.audit.models import AuditLog
 
logger = logging.getLogger("security_audit")
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter(
	'{"timestamp":"%(asctime)s","level":"%(levelname)s","message":%(message)s}'
))
logger.addHandler(handler)
logger.setLevel(logging.INFO)
 
 
def log_event(db: Session, action: str, status: str, ip_address: str,
          	user_id=None, username=None, http_method=None,
          	endpoint=None, status_code=None, resource=None, details=None):
	"""Запис події безпеки у таблицю audit_log та у структурований лог."""
 
	# 1. Запис у БД
	log_entry = AuditLog(
    	user_id=user_id, username=username, ip_address=ip_address,
    	action=action, status=status, http_method=http_method,
    	endpoint=endpoint, status_code=status_code, resource=resource,
    	details=json.dumps(details, ensure_ascii=False) if details else None,
	)
	db.add(log_entry)
	db.commit()
 
	# 2. Вивід у stdout (для Docker logs / SIEM)
	log_data = {"event_type": action, "status": status,
            	"user_id": user_id, "ip_address": ip_address}
	level = logging.WARNING if status == "failure" else logging.INFO
	logger.log(level, json.dumps(log_data, ensure_ascii=False))
 
 
def log_login_success(db, user_id, username, ip):
	log_event(db, action="login_success", status="success",
          	user_id=user_id, username=username, ip_address=ip,
          	http_method="POST", endpoint="/auth/login", status_code=200)
 
 
def log_login_failed(db, username, ip, reason="invalid_credentials"):
	log_event(db, action="login_failed", status="failure",
          	username=username, ip_address=ip,
          	http_method="POST", endpoint="/auth/login", status_code=401,
          	details={"reason": reason})
 
 
def log_access_denied(db, user_id, username, ip, endpoint):
	log_event(db, action="access_denied", status="failure",
          	user_id=user_id, username=username, ip_address=ip,
          	endpoint=endpoint, status_code=403)
 
 
def log_grade_change(db, user_id, username, ip,
                 	student_id, subject, old_grade, new_grade):
	log_event(db, action="grade_update", status="success",
          	user_id=user_id, username=username, ip_address=ip,
          	http_method="PUT", endpoint=f"/grades/{student_id}",
          	status_code=200, resource=f"grades.student_id={student_id}",
          	details={"student_id": student_id, "subject": subject,
                   	"old_grade": old_grade, "new_grade": new_grade})