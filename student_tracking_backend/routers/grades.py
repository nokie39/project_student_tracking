from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
import models, schemas, database, auth

router = APIRouter(
    prefix="/grades",
    tags=["Grades & Evaluation"]
)

# ==========================================
# 1. ດຶງຄະແນນຫ້ອງຮຽນປະຈຳເດືອນ (View Class Grades)
# ==========================================
@router.get("/view-class/{class_id}/{month_id}")
def view_class_grades(
    class_id: int, 
    month_id: int, 
    db: Session = Depends(database.get_db),
    current_user: dict = Depends(auth.get_current_user)
):
    # ດຶງ Student ໂດຍກົງ (Join Enrollment)
    students_in_class = db.query(models.Student).join(models.Enrollment).filter(
        models.Enrollment.class_id == class_id
    ).all()
    
    if not students_in_class:
        return []

    results = []

    for stu in students_in_class:
        # --- Safety Check (ກວດສອບຊື່) ---
        student_name = "Unknown Student"
        student_code = stu.student_code
        
        # 1. ລອງດຶງຈາກ User (ຖ້າມີ)
        if hasattr(stu, 'user') and stu.user:
            student_name = stu.user.full_name
        # 2. ຖ້າບໍ່ມີ User, ລອງດຶງຈາກ Field full_name ໃນ Student
        elif hasattr(stu, 'full_name') and stu.full_name:
            student_name = stu.full_name
        
        # 3. ດຶງຄະແນນທີ່ມີຢູ່ແລ້ວ
        existing_grade = db.query(models.Grade).filter(
            models.Grade.student_id == stu.id,
            models.Grade.class_id == class_id,
            models.Grade.month_id == month_id
        ).first()

        # 4. ຈັດຮູບແບບຂໍ້ມູນສົ່ງກັບ
        results.append({
            "student_id": stu.id,
            "student_code": student_code,
            "full_name": student_name, 
            "attendance_score": existing_grade.attendance_score if existing_grade else 0,
            "homework_score": existing_grade.homework_score if existing_grade else 0,
            "midterm_score": existing_grade.midterm_score if existing_grade else 0,
            "final_score": existing_grade.final_score if existing_grade else 0,
            "total_score": existing_grade.total_score if existing_grade else 0,
        })

    return results

# ==========================================
# 2. ອັບເດດຄະແນນ (Update Single Grade + Audit Log)
# ==========================================
@router.post("/update")
def update_grade(
    grade_data: schemas.GradeUpdate,
    db: Session = Depends(database.get_db),
    current_user: dict = Depends(auth.get_current_user)
):
    if current_user['role'] not in ['teacher', 'head_teacher', 'admin']:
        raise HTTPException(status_code=403, detail="Not authorized")

    # ຊອກຫາ Record ເກົ່າ
    grade_record = db.query(models.Grade).filter(
        models.Grade.student_id == grade_data.student_id,
        models.Grade.class_id == grade_data.class_id,
        models.Grade.month_id == grade_data.month_id
    ).first()

    # ຖ້າບໍ່ມີໃຫ້ສ້າງໃໝ່ (Initialize Grade Record)
    if not grade_record:
        grade_record = models.Grade(
            student_id=grade_data.student_id,
            class_id=grade_data.class_id,
            month_id=grade_data.month_id,
            attendance_score=0,
            homework_score=0,
            midterm_score=0,
            final_score=0,
            total_score=0
        )
        db.add(grade_record)
        db.commit()
        db.refresh(grade_record)

    # --- 🔥 Validation & Update Logic 🔥 ---
    old_val = 0
    val = grade_data.score_value

    if grade_data.score_type == "ATTENDANCE":
        if val > 10: # Max 10
            raise HTTPException(status_code=400, detail="ຄະແນນມາຮຽນ ຫ້າມເກີນ 10")
        old_val = grade_record.attendance_score
        grade_record.attendance_score = val

    elif grade_data.score_type == "HOMEWORK":
        if val > 20: # Max 20
            raise HTTPException(status_code=400, detail="ຄະແນນວຽກບ້ານ ຫ້າມເກີນ 20")
        old_val = grade_record.homework_score
        grade_record.homework_score = val

    elif grade_data.score_type == "MIDTERM":
        if val > 30: # Max 30
            raise HTTPException(status_code=400, detail="ຄະແນນກາງພາກ ຫ້າມເກີນ 30")
        old_val = grade_record.midterm_score
        grade_record.midterm_score = val

    elif grade_data.score_type == "FINAL":
        if val > 40: # Max 40
            raise HTTPException(status_code=400, detail="ຄະແນນທ້າຍພາກ ຫ້າມເກີນ 40")
        old_val = grade_record.final_score
        grade_record.final_score = val
    
    # ຄຳນວນຄະແນນລວມ (Total Score)
    grade_record.total_score = (
        grade_record.attendance_score + 
        grade_record.homework_score + 
        grade_record.midterm_score + 
        grade_record.final_score
    )

    # ບັນທຶກ Audit Log (ຖ້າຄະແນນມີການປ່ຽນແປງ)
    if old_val != val:
        log = models.GradeAuditLog(
            grade_id=grade_record.id,
            old_score=old_val,
            new_score=val,
            updated_by=current_user['id'],
            reason=grade_data.reason or f"Updated {grade_data.score_type}"
        )
        db.add(log)

    db.commit()
    db.refresh(grade_record)
    return {"message": "Grade updated successfully", "total_score": grade_record.total_score}

# ==========================================
# 3. ເບິ່ງປະຫວັດການແກ້ໄຂ (Audit Logs)
# ==========================================
@router.get("/logs/{student_id}/{month_id}", response_model=List[schemas.GradeLogResponse])
def get_grade_logs(
    student_id: int,
    month_id: int,
    db: Session = Depends(database.get_db),
    current_user: dict = Depends(auth.get_current_user)
):
    # 1. ຊອກຫາ Grade ID
    grade = db.query(models.Grade).filter(
        models.Grade.student_id == student_id,
        models.Grade.month_id == month_id
    ).first()
    
    if not grade:
        return []

    # 2. ດຶງ Logs ທັງໝົດ
    logs = db.query(models.GradeAuditLog).filter(
        models.GradeAuditLog.grade_id == grade.id
    ).order_by(models.GradeAuditLog.updated_at.desc()).all()
    
    # 3. Map ID -> Name
    results = []
    for log in logs:
        editor = db.query(models.User).filter(models.User.id == log.updated_by).first()
        
        results.append({
            "id": log.id,
            "old_score": log.old_score,
            "new_score": log.new_score,
            "updated_by": log.updated_by,
            "updated_by_name": editor.full_name if editor else "Unknown User",
            "reason": log.reason,
            "updated_at": log.updated_at
        })
    
    return results