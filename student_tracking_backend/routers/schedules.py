from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import models, schemas, database, auth

router = APIRouter(tags=["Schedules"])

# 1. ສ້າງຕາຕະລາງສອນ (Admin/Teacher)
@router.post("/schedules/")
def create_schedule(
    schedule: schemas.ScheduleCreate, 
    db: Session = Depends(database.get_db),
    current_user: dict = Depends(auth.get_current_user)
):
    # (ໃນອະນາຄົດສາມາດເພີ່ມ Logic ກວດສອບວ່າເວລາຊ້ອນກັນບໍ່ໄດ້ຢູ່ບ່ອນນີ້)
    new_schedule = models.ClassSchedule(**schedule.model_dump())
    db.add(new_schedule)
    db.commit()
    db.refresh(new_schedule)
    return new_schedule

# 2. ດຶງຕາຕະລາງຮຽນຂອງຫ້ອງ (Student/Parent View)
@router.get("/classes/{class_id}/schedules", response_model=list[schemas.ScheduleResponse])
def get_class_schedules(class_id: int, db: Session = Depends(database.get_db)):
    return db.query(models.ClassSchedule)\
        .filter(models.ClassSchedule.class_id == class_id)\
        .order_by(models.ClassSchedule.day_of_week, models.ClassSchedule.start_time)\
        .all()