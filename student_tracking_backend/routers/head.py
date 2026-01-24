from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date
import models, database, auth

router = APIRouter(
    prefix="/head",
    tags=["Head Teacher Management"]
)

# ==========================================
# 1. ພາບລວມປະຈຳວັນ (Dashboard Stats) ✅ Frontend ຕ້ອງການອັນນີ້
# ==========================================
@router.get("/daily-stats")
def get_daily_stats(
    db: Session = Depends(database.get_db),
    current_user: dict = Depends(auth.get_current_user)
):
    if current_user['role'] not in ['head_teacher', 'admin']:
        raise HTTPException(status_code=403, detail="Not authorized")

    today_str = str(date.today())

    # 1. ຈຳນວນນັກຮຽນທັງໝົດ
    total_students = db.query(models.Student).count()

    # 2. ຈຳນວນທີ່ມາຮຽນມື້ນີ້ (PRESENT + LATE)
    present_count = db.query(models.Attendance).filter(
        models.Attendance.date == today_str,
        models.Attendance.status.in_(['PRESENT', 'LATE'])
    ).count()

    # 3. ຄິດໄລ່ເປີເຊັນ
    attendance_rate = 0
    if total_students > 0:
        attendance_rate = round((present_count / total_students) * 100, 1)

    # 4. ຈຳນວນຄູທັງໝົດ
    total_teachers = db.query(models.User).filter(models.User.role == 'teacher').count()

    return {
        "total_students": total_students,
        "present_today": present_count,
        "attendance_rate": attendance_rate,
        "total_teachers": total_teachers
    }

# ==========================================
# 2. ຕິດຕາມການກວດກາຂອງຄູ (Attendance Monitor) ✅ Frontend ຕ້ອງການອັນນີ້
# ==========================================
@router.get("/attendance-monitor")
def get_attendance_monitor(
    db: Session = Depends(database.get_db),
    current_user: dict = Depends(auth.get_current_user)
):
    if current_user['role'] not in ['head_teacher', 'admin']:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    today_str = str(date.today())

    # ດຶງທຸກຫ້ອງຮຽນ
    classes = db.query(models.Class).all()
    
    results = []
    for cls in classes:
        # ກວດວ່າມີ Record Attendance ຂອງຫ້ອງນີ້ໃນມື້ນີ້ບໍ່?
        has_checked = db.query(models.Attendance).filter(
            models.Attendance.class_id == cls.id,
            models.Attendance.date == today_str
        ).first() is not None

        # ຫາຊື່ຄູປະຈຳຫ້ອງ
        teacher_name = "Unknown"
        teacher = db.query(models.User).filter(models.User.id == cls.teacher_id).first()
        if teacher:
            teacher_name = teacher.full_name

        results.append({
            "class_name": cls.name,
            "teacher_name": teacher_name,
            "status": "CHECKED" if has_checked else "PENDING"
        })
        
    return results

# ==========================================
# 3. ດຶງລາຍຊື່ຄູທັງໝົດ (Teacher List)
# ==========================================
@router.get("/teachers/list")
def get_all_teachers(
    db: Session = Depends(database.get_db),
    current_user: dict = Depends(auth.get_current_user)
):
    if current_user['role'] not in ['head_teacher', 'admin', 'teacher']: # teacher ອາດຈະໃຊ້ເບິ່ງໄດ້
        raise HTTPException(status_code=403, detail="Not authorized")

    teachers = db.query(models.User).filter(models.User.role == "teacher").all()
    
    return [
        {
            "id": t.id,
            "full_name": t.full_name,
            "email": t.email
        } 
        for t in teachers
    ]

# ==========================================
# 4. ຕິດຕາມສະຖານະການສອນແບບລະອຽດ (Detailed Monitor)
# ==========================================
@router.get("/monitor/summary") 
def monitor_teachers_summary(
    db: Session = Depends(database.get_db),
    current_user: dict = Depends(auth.get_current_user)
):
    if current_user['role'] not in ['head_teacher', 'admin']:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    today_str = str(date.today())
    teachers = db.query(models.User).filter(models.User.role == "teacher").all()
    
    results = []
    for teacher in teachers:
        # 1. ຫາຫ້ອງຮຽນທີ່ຄູຄົນນີ້ຮັບຜິດຊອບ
        assigned_class = db.query(models.Class).filter(models.Class.teacher_id == teacher.id).first()
        
        class_name = "No Class"
        attendance_done = False
        total_students = 0
        is_alert = False

        if assigned_class:
            class_name = assigned_class.name
            
            # 2. ກວດວ່າມື້ນີ້ມີການບັນທຶກ Attendance ຂອງຫ້ອງນີ້ແລ້ວບໍ່?
            check_attn = db.query(models.Attendance).filter(
                models.Attendance.class_id == assigned_class.id,
                models.Attendance.date == today_str
            ).first()

            attendance_done = check_attn is not None
            is_alert = not attendance_done 

            # 3. ນັບຈຳນວນນັກຮຽນໃນຫ້ອງ
            total_students = db.query(models.Enrollment).filter(
                models.Enrollment.class_id == assigned_class.id
            ).count()

        # 4. ຄວາມຄືບໜ້າການປ້ອນຄະແນນ (Check GradeAuditLog)
        logs_count = db.query(models.GradeAuditLog).filter(
            models.GradeAuditLog.updated_by == teacher.id
        ).count()
        
        progress = min(logs_count * 5, 100) 

        results.append({
            "id": teacher.id,
            "full_name": teacher.full_name,
            "class_name": class_name,
            "subjects_today": ["General"],
            "attendance_done": attendance_done,
            "grade_progress": progress,
            "is_alert": is_alert,
            "total_students": total_students
        })

    return results