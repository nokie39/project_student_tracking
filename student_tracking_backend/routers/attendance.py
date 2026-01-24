from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import date
import database, models, auth, schemas # ✅ Import schemas ເຂົ້າມາ

router = APIRouter(
    prefix="/attendance",
    tags=["Attendance"]
)

# ==========================================
# API 1: ດຶງຂໍ້ມູນການມາຮຽນຂອງຫ້ອງ (ຕາມວັນທີ)
# ==========================================
@router.get("/class/{class_id}")
def get_class_attendance(
    class_id: int,
    date_str: str = Query(default=str(date.today())), 
    db: Session = Depends(database.get_db),
    current_user: dict = Depends(auth.get_current_user)
):
    # 1. ດຶງນັກຮຽນທຸກຄົນໃນຫ້ອງ
    enrollments = db.query(models.Enrollment).filter(models.Enrollment.class_id == class_id).all()
    
    results = []
    for enroll in enrollments:
        std = enroll.student
        if not std: continue # ກັນພາດ

        # 2. ຫາເບິ່ງວ່າເຄີຍບັນທຶກໄວ້ແລ້ວບໍ່?
        attn = db.query(models.Attendance).filter(
            models.Attendance.student_id == std.id,
            models.Attendance.class_id == class_id,
            models.Attendance.date == date_str
        ).first()
        
        # ✅ Logic ຫາຊື່ (ແກ້ໄຂບັນຫາຊື່ວ່າງ ຫຼື Unknown)
        display_name = std.full_name
        if not display_name and std.user:
            display_name = std.user.full_name
        if not display_name:
            display_name = "Unknown Student"
        
        results.append({
            "student_id": std.id,
            "full_name": display_name,
            "student_code": std.student_code or "N/A",
            "status": attn.status if attn else "PRESENT" # Default ໃຫ້ເປັນ "ມາ"
        })
        
    return results

# ==========================================
# API 2: ບັນທຶກການມາຮຽນ (Bulk Save)
# ==========================================
@router.post("/save")
def save_attendance(
    data: schemas.AttendanceRequest, # ✅ ໃຊ້ Schema ຈາກ schemas.py (ທີ່ມີ field 'students')
    db: Session = Depends(database.get_db),
    current_user: dict = Depends(auth.get_current_user)
):
    if current_user['role'] not in ['teacher', 'head_teacher', 'admin']:
        raise HTTPException(status_code=403, detail="Not authorized")

    # ✅ Loop ຂໍ້ມູນຈາກ data.students (ໃຫ້ກົງກັບ Frontend)
    for item in data.students:
        # ກວດວ່າມີແລ້ວບໍ່?
        existing = db.query(models.Attendance).filter(
            models.Attendance.student_id == item.student_id,
            models.Attendance.class_id == data.class_id,
            models.Attendance.date == data.date
        ).first()

        if existing:
            existing.status = item.status # ອັບເດດ
        else:
            new_attn = models.Attendance(
                student_id=item.student_id,
                class_id=data.class_id,
                date=data.date,
                status=item.status
            )
            db.add(new_attn)
    
    db.commit()
    return {"message": "Attendance saved successfully"}