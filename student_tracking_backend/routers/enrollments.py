from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import models, schemas, database, auth

router = APIRouter(
    prefix="/enrollments",
    tags=["Enrollments (Assign Student to Class)"]
)

# 1. ລົງທະບຽນນັກຮຽນເຂົ້າຫ້ອງຮຽນ (Enroll Student)
@router.post("/", status_code=status.HTTP_201_CREATED)
def enroll_student(
    enrollment_data: schemas.EnrollmentCreate, 
    db: Session = Depends(database.get_db),
    current_user: dict = Depends(auth.get_current_user)
):
    if current_user['role'] not in ['admin', 'head_teacher']:
        raise HTTPException(status_code=403, detail="Not authorized")

    # 1. ກວດສອບ Class
    class_obj = db.query(models.Class).filter(models.Class.id == enrollment_data.class_id).first()
    if not class_obj:
        raise HTTPException(status_code=404, detail="Class not found")

    # 2. ກວດສອບ Student
    student = db.query(models.Student).filter(models.Student.id == enrollment_data.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    # 3. ກວດສອບຊ້ຳ (Duplicate Check)
    existing = db.query(models.Enrollment).filter(
        models.Enrollment.student_id == enrollment_data.student_id,
        models.Enrollment.class_id == enrollment_data.class_id
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Student already enrolled in this class")

    # 4. ບັນທຶກ (ເອົາ academic_year_id ອອກ)
    new_enrollment = models.Enrollment(
        student_id=enrollment_data.student_id,
        class_id=enrollment_data.class_id
        # ❌ ລຶບແຖວນີ້ອອກ: academic_year_id=class_obj.year_id 
    )
    
    db.add(new_enrollment)
    db.commit()
    db.refresh(new_enrollment)

    return {"message": "Enrolled successfully", "id": new_enrollment.id}

# 2. ລຶບນັກຮຽນອອກຈາກຫ້ອງ (Un-enroll)
@router.delete("/{enrollment_id}")
def unenroll_student(
    enrollment_id: int,
    db: Session = Depends(database.get_db),
    current_user: dict = Depends(auth.get_current_user)
):
    if current_user['role'] not in ['admin', 'head_teacher']:
        raise HTTPException(status_code=403, detail="Not authorized")

    enrollment = db.query(models.Enrollment).filter(models.Enrollment.id == enrollment_id).first()
    if not enrollment:
        raise HTTPException(status_code=404, detail="Enrollment record not found")

    db.delete(enrollment)
    db.commit()

    return {"message": "Student removed from class"}