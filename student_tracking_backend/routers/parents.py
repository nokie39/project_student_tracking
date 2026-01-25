from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
import database, models, auth

router = APIRouter(
    prefix="/parents",
    tags=["Parents"]
)

# ==========================================
# SCHEMAS
# ==========================================
class ChildSummary(BaseModel):
    id: int
    name: str
    student_code: str
    class_name: str = "N/A"
    photo_url: Optional[str] = None 

# ==========================================
# API 1: ດຶງລາຍຊື່ລູກທັງໝົດ
# ==========================================
@router.get("/children", response_model=List[ChildSummary])
def get_my_children(
    db: Session = Depends(database.get_db),
    current_user: dict = Depends(auth.get_current_user)
):
    if current_user['role'] != 'parent':
        raise HTTPException(status_code=403, detail="Parent access only")

    # 1. ດຶງ User ຜູ້ປົກຄອງ
    parent_user = db.query(models.User).filter(models.User.id == current_user['id']).first()
    
    if not parent_user:
        raise HTTPException(status_code=404, detail="User not found")

    # 2. ດຶງຂໍ້ມູນລູກ
    results = []
    
    for child in parent_user.children:
        
        # ດຶງຊື່ຫ້ອງຮຽນ
        class_name = "N/A"
        enrollment = db.query(models.Enrollment).filter(models.Enrollment.student_id == child.id).first()
        if enrollment:
            classroom = db.query(models.Class).filter(models.Class.id == enrollment.class_id).first()
            if classroom:
                class_name = classroom.name

        # Logic ດຶງຊື່
        display_name = child.full_name
        
        if not display_name and child.user_id:
             student_user = db.query(models.User).filter(models.User.id == child.user_id).first()
             if student_user:
                 display_name = student_user.full_name
        
        if not display_name:
            display_name = "ບໍ່ລະບຸຊື່"

        results.append({
            "id": child.id,
            "name": display_name,
            "student_code": child.student_code or "N/A",
            "class_name": class_name,
            "photo_url": getattr(child, 'profile_image', None) 
        })

    return results

# ==========================================
# API 2: ດຶງ Dashboard ຂອງລູກ
# ==========================================
@router.get("/student/{student_id}/dashboard")
def get_child_dashboard_data(
    student_id: int,
    db: Session = Depends(database.get_db),
    current_user: dict = Depends(auth.get_current_user)
):
    if current_user['role'] != 'parent':
        raise HTTPException(status_code=403, detail="Parent access only")

    # 1. ດຶງ User Parent
    parent_user = db.query(models.User).filter(models.User.id == current_user['id']).first()

    # 2. Security Check
    target_student = next((child for child in parent_user.children if child.id == student_id), None)

    if not target_student:
        raise HTTPException(status_code=404, detail="Child not found or unauthorized")

    # ດຶງຊື່ທີ່ຖືກຕ້ອງ
    student_name = target_student.full_name
    if not student_name and target_student.user_id:
        student_user = db.query(models.User).filter(models.User.id == target_student.user_id).first()
        if student_user:
            student_name = student_user.full_name
    
    if not student_name: student_name = "Unknown"

    # 3. ດຶງຂໍ້ມູນການຮຽນ
    enrollment = db.query(models.Enrollment).filter(models.Enrollment.student_id == target_student.id).first()
    
    # ຖ້າຍັງບໍ່ໄດ້ເຂົ້າຫ້ອງຮຽນ
    if not enrollment:
        return {
            "student_info": {
                "name": student_name,
                "class_name": "N/A",
                "total_points": 0
            },
            "assignments": [],
            "schedule": []
        }

    # 1. ຄະແນນພຶດຕິກຳ
    behavior_points = db.query(func.sum(models.BehaviorLog.points))\
        .filter(models.BehaviorLog.student_id == target_student.id).scalar() or 0
    
    # 2. ວຽກບ້ານຄ້າງສົ່ງ
    all_assignments = db.query(models.Assignment)\
        .filter(models.Assignment.class_id == enrollment.class_id)\
        .filter(models.Assignment.due_date > datetime.now())\
        .all()
    
    pending_assignments = []
    for assign in all_assignments:
        submission = db.query(models.Submission).filter(
            models.Submission.assignment_id == assign.id,
            models.Submission.student_id == target_student.id
        ).first()
        
        if not submission:
            pending_assignments.append({
                "id": assign.id,
                "title": assign.title,
                "due_date": assign.due_date
            })

    # 3. ຕາຕະລາງຮຽນມື້ນີ້
    today_weekday = str(datetime.now().weekday() + 1)
    
    # ✅✅✅ ແກ້ໄຂບ່ອນນີ້: ປ່ຽນ models.ClassSchedule ເປັນ models.Schedule ✅✅✅
    schedules = db.query(models.Schedule)\
        .filter(models.Schedule.class_id == enrollment.class_id)\
        .filter(models.Schedule.day_of_week == today_weekday) \
        .order_by(models.Schedule.start_time)\
        .all()

    classroom = db.query(models.Class).filter(models.Class.id == enrollment.class_id).first()

    return {
        "student_info": {
            "name": student_name,
            "class_name": classroom.name if classroom else "Unknown",
            "code": target_student.student_code,
            "total_points": behavior_points,
            "photo_url": getattr(target_student, 'profile_image', None)
        },
        "assignments": pending_assignments,
        "schedule": schedules
    }

# ==========================================
# API 3: ດຶງປະຫວັດຄະແນນຂອງລູກ (Grades)
# ==========================================
@router.get("/student/{student_id}/grades")
def get_child_grades(
    student_id: int,
    db: Session = Depends(database.get_db),
    current_user: dict = Depends(auth.get_current_user)
):
    if current_user['role'] != 'parent':
        raise HTTPException(status_code=403, detail="Parent access only")

    parent_user = db.query(models.User).filter(models.User.id == current_user['id']).first()
    
    target_student = next((child for child in parent_user.children if child.id == student_id), None)
    if not target_student:
        raise HTTPException(status_code=404, detail="Child not found")

    grades = db.query(models.Grade).filter(models.Grade.student_id == target_student.id).all()
    
    results = []
    months_map = {9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec", 1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "May"}

    for g in grades:
        grade_char = "F"
        if g.total_score >= 80: grade_char = "A"
        elif g.total_score >= 70: grade_char = "B"
        elif g.total_score >= 60: grade_char = "C"
        elif g.total_score >= 50: grade_char = "D"
        
        results.append({
            "month_name": months_map.get(g.month_id, f"Month {g.month_id}"),
            "score": g.total_score,
            "grade": grade_char,
            "midterm": g.midterm_score,
            "final": g.final_score
        })

    return results

# ==========================================
# API 4: ດຶງວຽກບ້ານທັງໝົດຂອງລູກ (Assignments History)
# ==========================================
@router.get("/student/{student_id}/assignments")
def get_child_assignments_history(
    student_id: int,
    db: Session = Depends(database.get_db),
    current_user: dict = Depends(auth.get_current_user)
):
    if current_user['role'] != 'parent':
        raise HTTPException(status_code=403, detail="Parent access only")

    parent_user = db.query(models.User).filter(models.User.id == current_user['id']).first()
    
    target_student = next((child for child in parent_user.children if child.id == student_id), None)
    if not target_student:
        raise HTTPException(status_code=404, detail="Child not found")

    enrollment = db.query(models.Enrollment).filter(models.Enrollment.student_id == target_student.id).first()
    if not enrollment:
        return []

    assignments = db.query(models.Assignment)\
        .filter(models.Assignment.class_id == enrollment.class_id)\
        .order_by(models.Assignment.due_date.desc())\
        .all()

    results = []
    for assign in assignments:
        submission = db.query(models.Submission).filter(
            models.Submission.assignment_id == assign.id,
            models.Submission.student_id == target_student.id
        ).first()

        status = "PENDING"
        if submission:
            status = "SUBMITTED"
        elif assign.due_date < datetime.now():
            status = "LATE"

        results.append({
            "id": assign.id,
            "title": assign.title,
            "description": assign.description,
            "due_date": assign.due_date,
            "status": status,
            "score": submission.score if submission else None
        })

    return results