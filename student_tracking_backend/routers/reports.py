from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date
import models, database, auth

router = APIRouter(tags=["Reports"])

# 1. (Head Teacher) ດຶງສະຖິຕິລວມຂອງໂຮງຮຽນ (Dashboard Stats)
@router.get("/reports/dashboard/summary")
def get_dashboard_summary(
    db: Session = Depends(database.get_db),
    current_user: dict = Depends(auth.get_current_user)
):
    # ອະນຸຍາດສະເພາະ Head Teacher ແລະ Admin
    if current_user['role'] not in ['head_teacher', 'admin']:
        raise HTTPException(status_code=403, detail="Not authorized")

    # 1. ນັກຮຽນທັງໝົດ
    total_students = db.query(models.Student).count()

    # 2. ຄູທັງໝົດ
    total_teachers = db.query(models.User).filter(models.User.role == "teacher").count()

    # 3. ອັດຕາການມາຮຽນມື້ນີ້ (%)
    today = date.today()
    total_attendance_records = db.query(models.Attendance).filter(models.Attendance.date == today).count()
    present_count = db.query(models.Attendance).filter(
        models.Attendance.date == today, 
        models.Attendance.status == "PRESENT"
    ).count()

    attendance_rate = 0
    if total_attendance_records > 0:
        attendance_rate = round((present_count / total_attendance_records) * 100, 1)

    # 4. ວຽກບ້ານທັງໝົດທີ່ສັ່ງໄປ
    total_assignments = db.query(models.Assignment).count()

    return {
        "total_students": total_students,
        "total_teachers": total_teachers,
        "attendance_rate": attendance_rate,
        "total_assignments": total_assignments
    }

# 2. (Head Teacher) ດຶງສະຖິຕິການມາຮຽນແຍກຕາມຫ້ອງ (Attendance by Class)
@router.get("/reports/dashboard/class-attendance")
def get_class_attendance_stats(
    db: Session = Depends(database.get_db),
    current_user: dict = Depends(auth.get_current_user)
):
    if current_user['role'] not in ['head_teacher', 'admin']:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    today = date.today()
    classes = db.query(models.Class).all()
    results = []

    for cls in classes:
        # ນັບຈຳນວນນັກຮຽນທີ່ຖືກເຊັກຊື່ໃນຫ້ອງນີ້ ມື້ນີ້
        records = db.query(models.Attendance).join(models.Enrollment).filter(
            models.Enrollment.class_id == cls.id,
            models.Attendance.date == today
        ).all()
        
        total = len(records)
        present = sum(1 for r in records if r.status == 'PRESENT')
        rate = round((present / total) * 100, 1) if total > 0 else 0

        results.append({
            "class_name": cls.name,
            "attendance_rate": rate,
            "total_checked": total
        })
    
    return results

# 3. (Parent/Student) ລາຍງານສ່ວນຕົວ (Code ເກົ່າ)
@router.get("/reports/student/{student_id}")
def get_student_report(
    student_id: int,
    db: Session = Depends(database.get_db),
    current_user: dict = Depends(auth.get_current_user)
):
    # ... (Logic ເກົ່າທີ່ເຄີຍຂຽນໄວ້) ...
    # ດຶງຄະແນນ
    grades = db.query(models.Grade).filter(models.Grade.enrollment_id == student_id).all()
    
    # ດຶງສະຖິຕິການມາຮຽນ
    attendance_stats = db.query(
        models.Attendance.status, 
        func.count(models.Attendance.status)
    ).join(models.Enrollment).filter(models.Enrollment.student_id == student_id)\
     .group_by(models.Attendance.status).all()

    # ດຶງວຽກບ້ານທີ່ຄ້າງສົ່ງ
    # (Logic ຕົວຢ່າງ: ນັບ assignment ທີ່ຍັງບໍ່ມີ submission)
    # *ໝາຍເຫດ: Logic ນີ້ອາດຈະຕ້ອງປັບປຸງຖ້າຢາກໃຫ້ລະອຽດຂຶ້ນ
    pending_homework = 0 

    return {
        "grades": grades,
        "attendance": dict(attendance_stats),
        "missing_homework": pending_homework
    }