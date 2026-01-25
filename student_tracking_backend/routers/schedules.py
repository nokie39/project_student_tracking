from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import database, models, schemas, auth

# ✅ ກຳນົດ Prefix ໃຫ້ກົງກັບ Frontend (/lms/schedules)
router = APIRouter(
    prefix="/lms/schedules",
    tags=["Schedules"]
)

# 1. ດຶງຕາຕະລາງຮຽນ (Filter ຕາມ Class ແລະ Semester)
@router.get("/{class_id}", response_model=List[schemas.ScheduleResponse])
def get_schedules(
    class_id: int, 
    semester_id: int = 1,  # ✅ Default ເປັນພາກ 1 ຖ້າບໍ່ສົ່ງມາ
    db: Session = Depends(database.get_db)
):
    return db.query(models.Schedule).filter(
        models.Schedule.class_id == class_id,
        models.Schedule.semester_id == semester_id  # ✅ ກອງຂໍ້ມູນຕາມພາກຮຽນ
    ).all()

# 2. ສ້າງຕາຕະລາງສອນ (Create)
@router.post("/", response_model=schemas.ScheduleResponse)
def create_schedule(
    schedule: schemas.ScheduleCreate, 
    db: Session = Depends(database.get_db),
    current_user: dict = Depends(auth.get_current_user)
):
    # ✅ Logic: ກວດສອບວ່າມີວິຊາຮຽນໃນເວລານັ້ນຫຼືຍັງ?
    existing_schedule = db.query(models.Schedule).filter(
        models.Schedule.class_id == schedule.class_id,
        models.Schedule.semester_id == schedule.semester_id, # ກວດໃນພາກຮຽນດຽວກັນ
        models.Schedule.day_of_week == schedule.day_of_week,
        models.Schedule.start_time == schedule.start_time
    ).first()

    if existing_schedule:
        raise HTTPException(status_code=400, detail="ຊ່ວງເວລານີ້ມີວິຊາຮຽນແລ້ວ (Time slot occupied)")

    # ບັນທຶກຂໍ້ມູນ
    new_schedule = models.Schedule(**schedule.dict())
    db.add(new_schedule)
    db.commit()
    db.refresh(new_schedule)
    return new_schedule

# 3. ລຶບຕາຕະລາງ (Delete) - Frontend ຕ້ອງການອັນນີ້
@router.delete("/{id}")
def delete_schedule(
    id: int, 
    db: Session = Depends(database.get_db),
    current_user: dict = Depends(auth.get_current_user)
):
    schedule = db.query(models.Schedule).filter(models.Schedule.id == id).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    db.delete(schedule)
    db.commit()
    return {"message": "Deleted successfully"}