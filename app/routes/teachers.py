# app/routes/teachers.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
 
from app.database import get_db
from app.models import User, Grade
from app.auth.dependencies import require_role
 
router = APIRouter(prefix="/teachers", tags=["Teachers"])
 
 
@router.get("/students/{student_id}/grades")
def get_student_grades(
	student_id: int,
	current_user: User = Depends(require_role("teacher", "admin")),
	db: Session = Depends(get_db),
):
	"""Викладач або адмін може переглянути оцінки будь-якого студента."""
	grades = db.query(Grade).filter(Grade.student_id == student_id).all()
	return {"student_id": student_id, "grades": [
    	{"subject_id": g.subject_id, "value": g.value} for g in grades
	]}
