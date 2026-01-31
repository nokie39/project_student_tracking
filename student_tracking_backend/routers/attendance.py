from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
import models, schemas, database, auth

router = APIRouter(tags=["Attendance"])

# ==========================================
# 1. ດຶງຂໍ້ມູນການເຊັກຊື່ (Returns Full Student List + Status)
# ==========================================
@router.get("/attendance/class/{class_id}")
def get_class_attendance(
    class_id: int,
    date_str: date, # FastAPI ຮັບມາເປັນ Date Object
    period: str = Query(default="DAILY"), 
    db: Session = Depends(database.get_db),
    current_user: dict = Depends(auth.get_current_user)
):
    # 1. ກວດສອບວ່າຫ້ອງຮຽນມີຢູ່ແທ້ບໍ່?
    cls = db.query(models.Class).filter(models.Class.id == class_id).first()
    if not cls:
        raise HTTPException(status_code=404, detail=f"Class ID {class_id} not found")

    # 2. ດຶງນັກຮຽນ + ຂໍ້ມູນ User (Join ຜ່ານ Enrollment)
    students = db.query(models.Student, models.User)\
        .join(models.User, models.User.id == models.Student.user_id)\
        .join(models.Enrollment, models.Enrollment.student_id == models.Student.id)\
        .filter(models.Enrollment.class_id == class_id)\
        .all()

    if not students:
        return []

    # ✅ ແກ້ໄຂ: ແປງ date object ເປັນ string ກ່ອນ query (ເພື່ອໃຫ້ກົງກັບ Database ທີ່ເປັນ VARCHAR)
    date_query = str(date_str) 

    # 3. ດຶງຂໍ້ມູນການເຊັກຊື່
    attendance_records = db.query(models.Attendance).filter(
        models.Attendance.class_id == class_id,
        models.Attendance.date == date_query, # <--- ໃຊ້ຕົວປ່ຽນທີ່ແປງເປັນ String ແລ້ວ
        models.Attendance.period == period
    ).all()

    # ສ້າງ Dictionary ເພື່ອໃຫ້ຄົ້ນຫາໄວຂຶ້ນ { student_id: record }
    att_map = {rec.student_id: rec for rec in attendance_records}

    results = []
    for std, usr in students:
        record = att_map.get(std.id)
        
        results.append({
            "student_id": std.id,
            "student_code": std.student_code,
            "full_name": usr.full_name,
            "gender": usr.gender if hasattr(usr, "gender") else "",
            "status": record.status if record else "PRESENT",
            "remark": record.remark if record else None
        })

    # ລຽງຕາມລະຫັດນັກຮຽນ 
    results.sort(key=lambda x: x['student_code'])
    
    return results

# ==========================================
# 2. ບັນທຶກການເຊັກຊື່ (Batch Save)
# ==========================================
@router.post("/attendance/save", status_code=status.HTTP_200_OK)
def save_attendance_batch(
    data: schemas.AttendanceBatchRequest,
    db: Session = Depends(database.get_db),
    current_user: dict = Depends(auth.get_current_user)
):
    if current_user['role'] not in ['teacher', 'admin', 'head_teacher']:
        raise HTTPException(status_code=403, detail="Not authorized")

    # ແປງວັນທີເປັນ String ຄືກັນ
    date_query = str(data.date)

    # ລຶບຂໍ້ມູນເກົ່າ
    db.query(models.Attendance).filter(
        models.Attendance.class_id == data.class_id,
        models.Attendance.date == date_query, # <--- ແກ້ບ່ອນນີ້
        models.Attendance.period == data.period
    ).delete()
    
    # ສ້າງຂໍ້ມູນໃໝ່
    new_records = []
    for item in data.students:
        new_records.append(models.Attendance(
            class_id=data.class_id,
            date=str(data.date), # <--- ແກ້ບ່ອນນີ້ (Save ເປັນ String)
            period=data.period,
            student_id=item.student_id,
            status=item.status,
            remark=item.remark
        ))
    
    db.add_all(new_records)
    db.commit()
    
    return {"message": f"Saved {len(new_records)} records successfully"}

# ... (ສ່ວນ get_student_attendance_history ບໍ່ຕ້ອງແກ້ກໍໄດ້ ຫຼື ຈະແກ້ເປັນ str() ຄືກັນກໍດີ) ...
@router.get("/attendance/student/{student_id}")
def get_student_attendance_history(
    student_id: int,
    db: Session = Depends(database.get_db),
    current_user: dict = Depends(auth.get_current_user)
):
    attendance = db.query(models.Attendance).filter(
        models.Attendance.student_id == student_id
    ).order_by(models.Attendance.date.desc()).all()
    return attendance