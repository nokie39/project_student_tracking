from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from datetime import date
import models, schemas, database, auth

router = APIRouter(prefix="/attendance", tags=["Attendance"])

# ==========================================
# 1. ດຶງຂໍ້ມູນການເຊັກຊື່ (Returns Full Student List + Status)
# ==========================================
@router.get("/class/{class_id}", response_model=List[schemas.AttendanceLogView])
def get_class_attendance(
    class_id: int,
    date_str: date, # format: YYYY-MM-DD
    period: str = Query(default="DAILY"), # ✅ ເພີ່ມ: ຮັບຄ່າ Period (ຖ້າບໍ່ສົ່ງມາຈະເປັນ DAILY)
    db: Session = Depends(database.get_db),
    current_user: dict = Depends(auth.get_current_user)
):
    # ກວດສອບສິດ (Teacher ຕ້ອງສອນຫ້ອງນີ້, Admin ເບິ່ງໄດ້ໝົດ)
    if current_user['role'] == 'teacher':
        cls = db.query(models.Class).filter(models.Class.id == class_id).first()
        if not cls or cls.teacher_id != current_user['id']:
            raise HTTPException(status_code=403, detail="Not authorized for this class")

    # 1. ດຶງນັກຮຽນທັງໝົດໃນຫ້ອງ (Join Student + User + Enrollment)
    students = db.query(models.Student, models.User)\
        .join(models.User, models.User.id == models.Student.user_id)\
        .join(models.Enrollment, models.Enrollment.student_id == models.Student.id)\
        .filter(models.Enrollment.class_id == class_id)\
        .all()

    # 2. ດຶງຂໍ້ມູນການເຊັກຊື່ຂອງມື້ນັ້ນ + ຕາມ Period ນັ້ນໆ (ຖ້າມີ)
    attendance_records = db.query(models.Attendance).filter(
        models.Attendance.class_id == class_id,
        models.Attendance.date == date_str,
        models.Attendance.period == period # ✅ ເພີ່ມ: ກອງຕາມ Period
    ).all()

    # ສ້າງ Dictionary ເພື່ອໃຫ້ຄົ້ນຫາໄວຂຶ້ນ { student_id: record }
    att_map = {rec.student_id: rec for rec in attendance_records}

    results = []
    for student, user in students:
        # ຖ້າມີຂໍ້ມູນການເຊັກຊື່ແລ້ວ ໃຫ້ໃຊ້ຂໍ້ມູນນັ້ນ, ຖ້າບໍ່ມີ ໃຫ້ Default ເປັນ "PRESENT"
        record = att_map.get(student.id)
        
        results.append({
            "student_id": student.id,
            "student_code": student.student_code,
            "full_name": user.full_name,
            "status": record.status if record else "PRESENT", # Default Value
            "remark": record.remark if record else None
        })
    
    # ລຽງຕາມລະຫັດນັກຮຽນ
    results.sort(key=lambda x: x['student_code'])
    
    return results

# ==========================================
# 2. ບັນທຶກການເຊັກຊື່ (Batch Save)
# ==========================================
@router.post("/save", status_code=status.HTTP_200_OK)
def save_attendance_batch(
    data: schemas.AttendanceBatchRequest,
    db: Session = Depends(database.get_db),
    current_user: dict = Depends(auth.get_current_user)
):
    if current_user['role'] not in ['teacher', 'admin', 'head_teacher']:
        raise HTTPException(status_code=403, detail="Not authorized")

    # 1. ລຶບຂໍ້ມູນເກົ່າຂອງວັນນັ້ນ + Period ນັ້ນ ອອກກ່ອນ (Update ແບບລ້າງແລ້ວສ້າງໃໝ່)
    # ⚠️ ຕ້ອງລະບຸ period ດ້ວຍ ບໍ່ດັ່ງນັ້ນມັນຈະລຶບຂອງວິຊາອື່ນໄປນຳ
    db.query(models.Attendance).filter(
        models.Attendance.class_id == data.class_id,
        models.Attendance.date == data.date,
        models.Attendance.period == data.period # ✅ ເພີ່ມ: ລຶບສະເພາະ Period ນີ້
    ).delete()
    
    # 2. ສ້າງຂໍ້ມູນໃໝ່
    new_records = []
    for item in data.students:
        new_records.append(models.Attendance(
            class_id=data.class_id,
            date=data.date,
            period=data.period, # ✅ ເພີ່ມ: ບັນທຶກ Period
            student_id=item.student_id,
            status=item.status,
            remark=item.remark
        ))
    
    db.add_all(new_records)
    db.commit()
    
    return {"message": f"Saved {len(new_records)} records successfully for period: {data.period}"}