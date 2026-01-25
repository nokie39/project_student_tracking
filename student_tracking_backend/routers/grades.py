from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
import models, schemas, database, auth

router = APIRouter(
    prefix="/grades",
    tags=["Grades & Evaluation"]
)

# ==========================================
# 🏆 STANDARD SCORING CONFIGURATION (ມາດຕະຖານຄະແນນ)
# ==========================================
# ທ່ານສາມາດປັບຕົວເລກຢູ່ບ່ອນນີ້ບ່ອນດຽວ ຖ້າມີການປ່ຽນແປງຫຼັກການ
MAX_SCORE_ATTENDANCE = 10
MAX_SCORE_HOMEWORK = 20
MAX_SCORE_MIDTERM = 30
MAX_SCORE_FINAL = 40

def validate_score(score_type: str, value: float):
    """
    ຟັງຊັນກວດສອບວ່ານະແນນເກີນມາດຕະຖານຫຼືບໍ່
    """
    if value < 0:
        raise HTTPException(status_code=400, detail="ຄະແນນບໍ່ສາມາດຕິດລົບໄດ້")

    if score_type == "ATTENDANCE" and value > MAX_SCORE_ATTENDANCE:
        raise HTTPException(status_code=400, detail=f"ຄະແນນມາຮຽນ ຫ້າມເກີນ {MAX_SCORE_ATTENDANCE}")
    
    if score_type == "HOMEWORK" and value > MAX_SCORE_HOMEWORK:
        raise HTTPException(status_code=400, detail=f"ຄະແນນວຽກບ້ານ ຫ້າມເກີນ {MAX_SCORE_HOMEWORK}")
    
    if score_type == "MIDTERM" and value > MAX_SCORE_MIDTERM:
        raise HTTPException(status_code=400, detail=f"ຄະແນນກາງພາກ ຫ້າມເກີນ {MAX_SCORE_MIDTERM}")
    
    if score_type == "FINAL" and value > MAX_SCORE_FINAL:
        raise HTTPException(status_code=400, detail=f"ຄະແນນທ້າຍພາກ ຫ້າມເກີນ {MAX_SCORE_FINAL}")

# ==========================================
# 🔒 ADMIN MANUAL LOCK (ລະບົບລັອກໂດຍ Admin)
# ==========================================

# 1. API ສຳລັບ Admin ກົດ ລັອກ/ປົດລັອກ
@router.post("/lock-toggle/{class_id}")
def toggle_class_lock(
    class_id: int,
    db: Session = Depends(database.get_db),
    current_user: dict = Depends(auth.get_current_user)
):
    # ສະເພາະ Admin ຫຼື Head Teacher
    if current_user['role'] not in ['admin', 'head_teacher']:
        raise HTTPException(status_code=403, detail="Not authorized")

    cls = db.query(models.Class).filter(models.Class.id == class_id).first()
    if not cls:
        raise HTTPException(status_code=404, detail="Class not found")
    
    # ສະລັບຄ່າ True <-> False
    cls.is_grade_locked = not cls.is_grade_locked
    db.commit()
    
    status_text = "LOCKED" if cls.is_grade_locked else "UNLOCKED"
    return {"message": f"Class is now {status_text}", "is_locked": cls.is_grade_locked}

# 2. API ກວດສອບສະຖານະການລັອກຂອງຫ້ອງ
@router.get("/lock-status/{class_id}")
def get_lock_status(
    class_id: int,
    db: Session = Depends(database.get_db)
):
    cls = db.query(models.Class).filter(models.Class.id == class_id).first()
    if not cls:
        return {"is_manual_locked": False}
    return {"is_manual_locked": cls.is_grade_locked}


# ==========================================
# 1. ດຶງຄະແນນຫ້ອງຮຽນປະຈຳເດືອນ (View Class Grades)
# ==========================================
@router.get("/view-class/{class_id}/{month_id}")
def view_class_grades(
    class_id: int, 
    month_id: int, 
    subject_name: str = "GENERAL", # ✅ ຮັບຄ່າວິຊາ (Default = GENERAL)
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
        
        # 3. ດຶງຄະແນນທີ່ມີຢູ່ແລ້ວ (✅ ກອງຕາມວິຊາ subject_name)
        existing_grade = db.query(models.Grade).filter(
            models.Grade.student_id == stu.id,
            models.Grade.class_id == class_id,
            models.Grade.month_id == month_id,
            models.Grade.subject_name == subject_name 
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

    # ລຽງລຳດັບຕາມລະຫັດນັກຮຽນ
    results.sort(key=lambda x: x['student_code'])
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

    # ✅ 1. ກວດສອບມາດຕະຖານຄະແນນ (Validation)
    validate_score(grade_data.score_type, grade_data.score_value)

    # ✅ 2. ຊອກຫາ Record ເກົ່າ (ຕ້ອງກອງ subject_name ນຳ)
    grade_record = db.query(models.Grade).filter(
        models.Grade.student_id == grade_data.student_id,
        models.Grade.class_id == grade_data.class_id,
        models.Grade.month_id == grade_data.month_id,
        models.Grade.subject_name == grade_data.subject_name
    ).first()

    # 3. ຖ້າບໍ່ມີໃຫ້ສ້າງໃໝ່ (Initialize Grade Record)
    if not grade_record:
        grade_record = models.Grade(
            student_id=grade_data.student_id,
            class_id=grade_data.class_id,
            month_id=grade_data.month_id,
            subject_name=grade_data.subject_name, # ✅ ບັນທຶກຊື່ວິຊາ
            attendance_score=0,
            homework_score=0,
            midterm_score=0,
            final_score=0,
            total_score=0
        )
        db.add(grade_record)
        db.commit()
        db.refresh(grade_record)

    # 4. Update Logic
    old_val = 0
    val = grade_data.score_value

    if grade_data.score_type == "ATTENDANCE":
        old_val = grade_record.attendance_score
        grade_record.attendance_score = val

    elif grade_data.score_type == "HOMEWORK":
        old_val = grade_record.homework_score
        grade_record.homework_score = val

    elif grade_data.score_type == "MIDTERM":
        old_val = grade_record.midterm_score
        grade_record.midterm_score = val

    elif grade_data.score_type == "FINAL":
        old_val = grade_record.final_score
        grade_record.final_score = val
    
    # 5. ຄຳນວນຄະແນນລວມ (Total Score)
    grade_record.total_score = (
        grade_record.attendance_score + 
        grade_record.homework_score + 
        grade_record.midterm_score + 
        grade_record.final_score
    )

    # 6. ບັນທຶກ Audit Log (ຖ້າຄະແນນມີການປ່ຽນແປງ)
    if old_val != val:
        log = models.GradeAuditLog(
            grade_id=grade_record.id,
            old_score=old_val,
            new_score=val,
            updated_by=current_user['id'],
            reason=grade_data.reason or f"Updated {grade_data.score_type} for {grade_data.subject_name}"
        )
        db.add(log)

    db.commit()
    db.refresh(grade_record)
    
    return {
        "message": "Grade updated successfully", 
        "total_score": grade_record.total_score,
        "subject": grade_record.subject_name
    }

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
    # 1. ດຶງຂໍ້ມູນ Grades ທັງໝົດຂອງນັກຮຽນໃນເດືອນນີ້ (ເພື່ອເອົາຊື່ວິຊາ)
    grades = db.query(models.Grade).filter(
        models.Grade.student_id == student_id,
        models.Grade.month_id == month_id
    ).all()
    
    if not grades:
        return []

    # ✅ ສ້າງ Dictionary ເພື່ອທຽບ grade_id -> subject_name
    grade_map = {g.id: g.subject_name for g in grades}
    grade_ids = list(grade_map.keys())

    # 2. ດຶງ Logs
    logs = db.query(models.GradeAuditLog).filter(
        models.GradeAuditLog.grade_id.in_(grade_ids)
    ).order_by(models.GradeAuditLog.updated_at.desc()).all()
    
    # 3. Map ຂໍ້ມູນສົ່ງກັບ
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
            "subject_name": grade_map.get(log.grade_id, "Unknown"), # ✅ ໃສ່ຊື່ວິຊາບ່ອນນີ້
            "updated_at": log.updated_at
        })
    
    return results