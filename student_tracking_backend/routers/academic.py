from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List
import models, schemas, database, auth

router = APIRouter(
    prefix="/academic",
    tags=["Academic Years & Classes"]
)

# ==========================================
# 1. ດຶງຂໍ້ມູນປີການສຶກສາທັງໝົດ
# ==========================================
@router.get("/years", response_model=List[schemas.AcademicYearResponse])
def get_academic_years(
    db: Session = Depends(database.get_db),
    current_user: dict = Depends(auth.get_current_user)
):
    return db.query(models.AcademicYear).order_by(models.AcademicYear.id.desc()).all()

# ==========================================
# 2. ສ້າງປີການສຶກສາໃໝ່ (Admin Only)
# ==========================================
@router.post("/years", status_code=status.HTTP_201_CREATED)
def create_academic_year(
    year: schemas.AcademicYearCreate,
    db: Session = Depends(database.get_db),
    current_user: dict = Depends(auth.get_current_user)
):
    if current_user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Not authorized")
    
    new_year = models.AcademicYear(name=year.name, is_active=year.is_active)
    
    # ຖ້າປີໃໝ່ເປັນ Active, ໃຫ້ປິດ Active ປີອື່ນໆ
    if year.is_active:
        db.query(models.AcademicYear).update({"is_active": False})
    
    db.add(new_year)
    db.commit()
    db.refresh(new_year)
    return new_year

# ==========================================
# 3. ແກ້ໄຂປີການສຶກສາ (Admin Only)
# ==========================================
@router.put("/years/{year_id}")
def update_academic_year(
    year_id: int,
    year_data: schemas.AcademicYearCreate,
    db: Session = Depends(database.get_db),
    current_user: dict = Depends(auth.get_current_user)
):
    if current_user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Not authorized")
        
    year = db.query(models.AcademicYear).filter(models.AcademicYear.id == year_id).first()
    if not year:
        raise HTTPException(status_code=404, detail="Year not found")
        
    year.name = year_data.name
    
    # ຖ້າຕັ້ງເປັນ Active, ປີອື່ນຕ້ອງ Inactive
    if year_data.is_active:
        db.query(models.AcademicYear).filter(models.AcademicYear.id != year_id).update({"is_active": False})
        year.is_active = True
    else:
        year.is_active = False
        
    db.commit()
    db.refresh(year)
    return year

# ==========================================
# 4. ລຶບປີການສຶກສາ (Admin Only)
# ==========================================
@router.delete("/years/{year_id}")
def delete_academic_year(
    year_id: int,
    db: Session = Depends(database.get_db),
    current_user: dict = Depends(auth.get_current_user)
):
    if current_user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Not authorized")
        
    year = db.query(models.AcademicYear).filter(models.AcademicYear.id == year_id).first()
    if not year:
        raise HTTPException(status_code=404, detail="Year not found")
        
    # ກວດສອບວ່າປີນີ້ມີຫ້ອງຮຽນໃຊ້ຢູ່ບໍ່? ຖ້າມີ ບໍ່ໃຫ້ລຶບ
    classes_count = db.query(models.Class).filter(models.Class.year_id == year_id).count()
    if classes_count > 0:
        raise HTTPException(status_code=400, detail="Cannot delete year with existing classes")
        
    db.delete(year)
    db.commit()
    return {"message": "Deleted successfully"}

# ==========================================
# 5. ດຶງລາຍຊື່ຄູ (Dropdown for Class Assignment)
# ==========================================
@router.get("/teachers-list")
def get_teachers_for_dropdown(
    db: Session = Depends(database.get_db),
    current_user: dict = Depends(auth.get_current_user)
):
    # ດຶງ User ທີ່ມີ role = teacher ທັງໝົດ
    teachers = db.query(models.User).filter(models.User.role == "teacher").all()
    return [{"id": t.id, "full_name": t.full_name} for t in teachers]

# ==========================================
# 🔥 6. ດຶງລາຍຊື່ຫ້ອງຮຽນ (ແກ້ໄຂ: Filter ຕາມ Role)
# ==========================================
@router.get("/classes", response_model=List[schemas.ClassResponse])
def get_all_classes(
    db: Session = Depends(database.get_db),
    current_user: dict = Depends(auth.get_current_user)
):
    query = db.query(models.Class).options(
        joinedload(models.Class.enrollments),
        joinedload(models.Class.academic_year),
        joinedload(models.Class.teacher)
    )

    # ✅ Logic: ຖ້າເປັນ Teacher ໃຫ້ເຫັນສະເພາະຫ້ອງທີ່ຕົນເອງຮັບຜິດຊອບ
    if current_user['role'] == 'teacher':
        query = query.filter(models.Class.teacher_id == current_user['id'])
    
    # ຖ້າເປັນ Admin ຫຼື Head Teacher ໃຫ້ເຫັນທັງໝົດ
    return query.all()

# ==========================================
# 7. ສ້າງຫ້ອງຮຽນໃໝ່ (Admin Only)
# ==========================================
@router.post("/classes", status_code=status.HTTP_201_CREATED)
def create_class(
    class_data: schemas.ClassCreate,
    db: Session = Depends(database.get_db),
    current_user: dict = Depends(auth.get_current_user)
):
    if current_user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Not authorized")
        
    new_class = models.Class(
        name=class_data.name,
        teacher_id=class_data.teacher_id,
        year_id=class_data.year_id
    )
    db.add(new_class)
    db.commit()
    db.refresh(new_class)
    return new_class

# ==========================================
# 8. ແກ້ໄຂຫ້ອງຮຽນ (Admin Only)
# ==========================================
@router.put("/classes/{class_id}")
def update_class(
    class_id: int,
    class_data: schemas.ClassCreate,
    db: Session = Depends(database.get_db),
    current_user: dict = Depends(auth.get_current_user)
):
    if current_user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Not authorized")
        
    cls = db.query(models.Class).filter(models.Class.id == class_id).first()
    if not cls:
        raise HTTPException(status_code=404, detail="Class not found")
        
    cls.name = class_data.name
    cls.teacher_id = class_data.teacher_id
    cls.year_id = class_data.year_id
    
    db.commit()
    db.refresh(cls)
    return cls

# ==========================================
# 9. ລຶບຫ້ອງຮຽນ (Admin Only)
# ==========================================
@router.delete("/classes/{class_id}")
def delete_class(
    class_id: int,
    db: Session = Depends(database.get_db),
    current_user: dict = Depends(auth.get_current_user)
):
    if current_user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Not authorized")
        
    cls = db.query(models.Class).filter(models.Class.id == class_id).first()
    if not cls:
        raise HTTPException(status_code=404, detail="Class not found")
    
    # ກວດສອບກ່ອນລຶບ: ຖ້າມີນັກຮຽນຢູ່ໃນຫ້ອງ ຫ້າມລຶບ!
    student_count = db.query(models.Enrollment).filter(models.Enrollment.class_id == class_id).count()
    if student_count > 0:
        raise HTTPException(status_code=400, detail="Cannot delete class with enrolled students")

    db.delete(cls)
    db.commit()
    return {"message": "Deleted successfully"}