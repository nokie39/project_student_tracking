from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from pydantic import BaseModel
import models, database, auth
from datetime import datetime

router = APIRouter(
    prefix="/behavior",
    tags=["Behavior & Talents"]
)

# ==========================================
# SCHEMAS
# ==========================================
class BehaviorCreate(BaseModel):
    student_id: int
    type: str # 'POSITIVE' or 'NEGATIVE'
    title: str
    description: Optional[str] = ""
    points: int

class StudentBehaviorSummary(BaseModel):
    id: int
    full_name: str
    student_code: str
    current_points: int
    image: Optional[str] = None

class TalentUpdate(BaseModel):
    talents: str

# ==========================================
# API 1: ບັນທຶກພຶດຕິກຳໃໝ່
# ==========================================
@router.post("/add")
def add_behavior_log(
    log: BehaviorCreate,
    db: Session = Depends(database.get_db),
    current_user: dict = Depends(auth.get_current_user)
):
    if current_user['role'] not in ["teacher", "head_teacher", "admin"]:
        raise HTTPException(status_code=403, detail="ບໍ່ມີສິດໃນການບັນທຶກ")

    new_log = models.BehaviorLog(
        student_id=log.student_id,
        teacher_id=current_user['id'], 
        type=log.type,
        title=log.title,
        description=log.description,
        points=log.points,
        created_at=datetime.utcnow()
    )
    
    db.add(new_log)
    db.commit()
    db.refresh(new_log)
    
    return {"message": "ບັນທຶກພຶດຕິກຳສຳເລັດ", "data": new_log}

# ==========================================
# API 2: ດຶງນັກຮຽນໃນຫ້ອງມາໃຫ້ຄະແນນ (Teacher View)
# ==========================================
@router.get("/class/{class_id}/students", response_model=List[StudentBehaviorSummary])
def get_students_for_grading(
    class_id: int,
    db: Session = Depends(database.get_db),
    current_user: dict = Depends(auth.get_current_user)
):
    enrollments = db.query(models.Enrollment).filter(models.Enrollment.class_id == class_id).all()
    
    students_data = []
    for enroll in enrollments:
        std = enroll.student
        
        if std: 
            # 1. ຄິດໄລ່ຄະແນນ
            behavior_points = db.query(func.sum(models.BehaviorLog.points))\
                .filter(models.BehaviorLog.student_id == std.id).scalar() or 0
                
            total_score = 10 + behavior_points
            
            # 2. ✅ Logic ຫາຊື່ (ແກ້ໄຂບັນຫາຊື່ວ່າງ)
            display_name = std.full_name # ເອົາຈາກ Student ກ່ອນ
            
            # ຖ້າໃນ Student ບໍ່ມີ, ໃຫ້ໄປເອົາຈາກ User Login ທີ່ຜູກກັນ
            if not display_name and std.user:
                display_name = std.user.full_name
            
            # ຖ້າບໍ່ມີເລີຍ
            if not display_name:
                display_name = "Unknown Student"

            # 3. ✅ ປ້ອງກັນ Error ເລື່ອງຮູບ (AttributeError)
            image_url = getattr(std, "profile_image", None)

            students_data.append({
                "id": std.id,
                "full_name": display_name, # ໃຊ້ຊື່ທີ່ຫາໄດ້
                "student_code": std.student_code or "N/A",
                "current_points": total_score,
                "image": image_url 
            })
        
    return students_data

# ==========================================
# API 3: ລາຍງານພຶດຕິກຳ
# ==========================================
@router.get("/report/{student_id}")
def get_behavior_report(student_id: int, db: Session = Depends(database.get_db)):
    logs = db.query(models.BehaviorLog).filter(
        models.BehaviorLog.student_id == student_id
    ).order_by(models.BehaviorLog.created_at.desc()).all()
    
    positive_points = db.query(func.sum(models.BehaviorLog.points)).filter(
        models.BehaviorLog.student_id == student_id,
        models.BehaviorLog.type == "POSITIVE"
    ).scalar() or 0
    
    negative_points = db.query(func.sum(models.BehaviorLog.points)).filter(
        models.BehaviorLog.student_id == student_id,
        models.BehaviorLog.type == "NEGATIVE"
    ).scalar() or 0

    return {
        "logs": logs,
        "summary": {
            "positive": positive_points,
            "negative": negative_points,
            "total_merit": positive_points + negative_points
        }
    }

# ==========================================
# API 4: ອັບເດດພອນສະຫວັນ
# ==========================================
@router.put("/talents/{student_id}")
def update_student_talents(
    student_id: int,
    data: TalentUpdate,
    db: Session = Depends(database.get_db),
    current_user: dict = Depends(auth.get_current_user)
):
    if current_user['role'] not in ["teacher", "head_teacher", "admin"]:
        raise HTTPException(status_code=403, detail="ບໍ່ມີສິດແກ້ໄຂ")

    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="ບໍ່ພົບຂໍ້ມູນນັກຮຽນ")

    student.talents = data.talents
    db.commit()
    
    return {"message": "ອັບເດດພອນສະຫວັນສຳເລັດ"}