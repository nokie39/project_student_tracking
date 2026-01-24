from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
import models, schemas, database, auth
from typing import List
from datetime import datetime

router = APIRouter(prefix="/students", tags=["Students & Portfolio"])

# ==========================================
# 1. ດຶງລາຍຊື່ນັກຮຽນທັງໝົດ (Admin/Head Only)
# ==========================================
@router.get("/", response_model=List[schemas.StudentFullReport])
def get_all_students(
    db: Session = Depends(database.get_db),
    current_user: dict = Depends(auth.get_current_user)
):
    if current_user['role'] not in ['admin', 'head_teacher']:
        raise HTTPException(status_code=403, detail="Not authorized")

    students = db.query(models.Student).all()
    results = []
    
    for s in students:
        user = db.query(models.User).filter(models.User.id == s.user_id).first()
        logs = db.query(models.BehaviorLog).filter(models.BehaviorLog.student_id == s.id).all()
        pos_pts = sum(l.points for l in logs if l.type == "POSITIVE")
        neg_pts = sum(l.points for l in logs if l.type == "NEGATIVE")
        
        # ດຶງ Email ນັກຮຽນ (Login Email)
        student_email = user.email if user else None

        results.append({
            "id": s.id,
            "student_code": s.student_code,
            "full_name": user.full_name if user else s.full_name, 
            "email": student_email, 
            "parent_email": s.parent_email,
            "parent_name": s.parent_name,
            "parent_phone": s.parent_phone,
            "blood_type": s.blood_type,
            "talents": s.talents,
            "address_summary": f"ບ້ານ {s.village or ''}, {s.district or ''}",
            "total_merit_points": pos_pts + neg_pts,
            "behavior_logs": logs
        })
    return results

# ==========================================
# 2. ລົງທະບຽນນັກຮຽນໃໝ່ (Create) - ✅ Auto Create Parent User
# ==========================================
@router.post("/register", response_model=schemas.StudentResponse)
def register_student(
    student_in: schemas.StudentRegister, 
    db: Session = Depends(database.get_db),
    current_user: dict = Depends(auth.get_current_user)
):
    if current_user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Only Admin can register students")

    # 1. ກວດສອບ Email ແລະ Student Code ຊ້ຳ
    existing_user = db.query(models.User).filter(models.User.email == student_in.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email ນັກຮຽນນີ້ມີຢູ່ໃນລະບົບແລ້ວ")
        
    existing_code = db.query(models.Student).filter(models.Student.student_code == student_in.student_code).first()
    if existing_code:
        raise HTTPException(status_code=400, detail="ລະຫັດນັກຮຽນນີ້ມີຢູ່ໃນລະບົບແລ້ວ")

    # 2. ສ້າງ User ໃຫ້ນັກຮຽນ (Role: Student)
    new_user = models.User(
        email=student_in.email,
        full_name=student_in.full_name,
        role="student",
        is_active=True
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # 3. ສ້າງຂໍ້ມູນນັກຮຽນ (Student Profile)
    new_student = models.Student(
        user_id=new_user.id,
        student_code=student_in.student_code,
        full_name=student_in.full_name,
        date_of_birth=student_in.date_of_birth,
        parent_name=student_in.parent_name,
        parent_phone=student_in.parent_phone,
        parent_email=student_in.parent_email, 
        blood_type=student_in.blood_type,
        allergies=student_in.allergies,
        address=student_in.address,
        village=student_in.village,
        district=student_in.district,
        province=student_in.province,
        talents=student_in.talents,
        health_info=student_in.health_info
    )
    db.add(new_student)
    db.commit()
    db.refresh(new_student)

    # 🔥🔥🔥 4. Logic ພິເສດ: ສ້າງ User ໃຫ້ຜູ້ປົກຄອງອັດຕະໂນມັດ (ຖ້າມີ Parent Email) 🔥🔥🔥
    if student_in.parent_email:
        # ກວດວ່າມີ User ຜູ້ປົກຄອງນີ້ແລ້ວບໍ່?
        parent_user = db.query(models.User).filter(models.User.email == student_in.parent_email).first()
        
        if not parent_user:
            # ຖ້າບໍ່ມີ -> ສ້າງໃໝ່ເລີຍ (Role: Parent)
            parent_user = models.User(
                email=student_in.parent_email,
                full_name=student_in.parent_name or "Parent", 
                role="parent",
                is_active=True
            )
            db.add(parent_user)
            db.commit()
            db.refresh(parent_user)
        
        # ✅ ເຊື່ອມໂຍງ ຜູ້ປົກຄອງ <-> ນັກຮຽນ (Many-to-Many Relationship)
        if parent_user not in new_student.parents:
            new_student.parents.append(parent_user)
            db.commit()

    return {
        "id": new_student.id,
        "student_code": new_student.student_code,
        "full_name": new_user.full_name
    }

# ==========================================
# 🔥 2.1 ອັບເດດຂໍ້ມູນນັກຮຽນ (Update) - ✅ Auto Update Parent Logic
# ==========================================
@router.put("/{student_id}", response_model=schemas.StudentResponse)
def update_student(
    student_id: int, 
    student_update: schemas.StudentUpdate, 
    db: Session = Depends(database.get_db),
    current_user: dict = Depends(auth.get_current_user)
):
    if current_user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Not authorized")

    db_student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not db_student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    db_user = db.query(models.User).filter(models.User.id == db_student.user_id).first()

    # ເກັບ Email ຜູ້ປົກຄອງເກົ່າໄວ້ທຽບ
    old_parent_email = db_student.parent_email
    
    # ຂໍ້ມູນທີ່ຈະອັບເດດ
    update_data = student_update.dict(exclude_unset=True)
    new_parent_email = update_data.get("parent_email")
    
    # 1. ອັບເດດຂໍ້ມູນ User (ນັກຮຽນ)
    if db_user:
        if "full_name" in update_data:
            db_user.full_name = update_data["full_name"]
        if "email" in update_data:
            db_user.email = update_data["email"]

    # 2. ອັບເດດຂໍ້ມູນ Student Profile
    for key, value in update_data.items():
        if key not in ["full_name", "email"] and hasattr(db_student, key):
            setattr(db_student, key, value)

    # 🔥🔥🔥 3. Logic ພິເສດ: ຖ້າ Parent Email ປ່ຽນ -> ຈັດການ User ຜູ້ປົກຄອງ 🔥🔥🔥
    if new_parent_email and new_parent_email != old_parent_email:
        parent_user = db.query(models.User).filter(models.User.email == new_parent_email).first()
        
        if not parent_user:
            parent_user = models.User(
                email=new_parent_email,
                full_name=update_data.get("parent_name") or "Parent",
                role="parent",
                is_active=True
            )
            db.add(parent_user)
            db.commit()
            db.refresh(parent_user)
        
        if parent_user not in db_student.parents:
            db_student.parents.append(parent_user)

    db.commit()
    db.refresh(db_student)
    
    return {
        "id": db_student.id,
        "student_code": db_student.student_code,
        "full_name": db_user.full_name if db_user else ""
    }

# ==========================================
# 🔥 2.2 ລຶບນັກຮຽນ (Delete)
# ==========================================
@router.delete("/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_student(
    student_id: int, 
    db: Session = Depends(database.get_db),
    current_user: dict = Depends(auth.get_current_user)
):
    if current_user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Not authorized")

    db_student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not db_student:
        raise HTTPException(status_code=404, detail="Student not found")

    if db_student.user_id:
        db_user = db.query(models.User).filter(models.User.id == db_student.user_id).first()
        if db_user:
            db.delete(db_user)

    db.delete(db_student)
    db.commit()
    
    return None

# ==========================================
# 3. ບັນທຶກພຶດຕິກຳ (Teacher Only - Restricted)
# ==========================================
@router.post("/behavior/", response_model=schemas.BehaviorLogResponse)
def create_behavior_log(
    log_in: schemas.BehaviorLogCreate,
    db: Session = Depends(database.get_db),
    current_user: dict = Depends(auth.get_current_user)
):
    if current_user['role'] not in ['admin', 'teacher', 'head_teacher']:
        raise HTTPException(status_code=403, detail="Not authorized")

    # ✅ Logic ເພີ່ມເຕີມ: ຖ້າເປັນ Teacher ຕ້ອງສອນຫ້ອງນັ້ນຈຶ່ງໃຫ້ຄະແນນໄດ້
    if current_user['role'] == 'teacher':
        enrollment = db.query(models.Enrollment).filter(models.Enrollment.student_id == log_in.student_id).first()
        if not enrollment:
             raise HTTPException(status_code=404, detail="Student not enrolled in any class")
        
        classroom = db.query(models.Class).filter(models.Class.id == enrollment.class_id).first()
        if classroom.teacher_id != current_user['id']:
             raise HTTPException(status_code=403, detail="ທ່ານບໍ່ສາມາດໃຫ້ຄະແນນນັກຮຽນຕ່າງຫ້ອງໄດ້")

    new_log = models.BehaviorLog(
        student_id=log_in.student_id,
        teacher_id=current_user['id'],
        type=log_in.type,
        title=log_in.title,
        description=log_in.description,
        points=log_in.points
    )
    db.add(new_log)
    db.commit()
    db.refresh(new_log)
    return new_log

# ==========================================
# 4. ດຶງຂໍ້ມູນ Portfolio ລວມ
# ==========================================
@router.get("/{student_id}/portfolio", response_model=schemas.StudentFullReport)
def get_student_portfolio(student_id: int, db: Session = Depends(database.get_db)):
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    user = db.query(models.User).filter(models.User.id == student.user_id).first()
    logs = db.query(models.BehaviorLog).filter(models.BehaviorLog.student_id == student_id).all()
    
    pos_pts = sum(l.points for l in logs if l.type == "POSITIVE")
    neg_pts = sum(l.points for l in logs if l.type == "NEGATIVE")

    class_name = "N/A"
    academic_year = "N/A"

    enrollment = db.query(models.Enrollment).filter(models.Enrollment.student_id == student.id).first()
    if enrollment:
        classroom = db.query(models.Class).filter(models.Class.id == enrollment.class_id).first()
        if classroom:
            class_name = classroom.name
            year = db.query(models.AcademicYear).filter(models.AcademicYear.id == classroom.year_id).first()
            if year:
                academic_year = year.name

    return {
        "id": student.id,
        "student_code": student.student_code,
        "full_name": user.full_name if user else "Unknown",
        "email": user.email if user else None,
        "parent_email": student.parent_email,
        "parent_name": student.parent_name,
        "parent_phone": student.parent_phone,
        "blood_type": student.blood_type,
        "talents": student.talents,
        "address_summary": f"ບ້ານ {student.village or ''}, {student.district or ''}, {student.province or ''}",
        "total_merit_points": pos_pts + neg_pts,
        "behavior_logs": logs,
        "class_name": class_name,
        "academic_year": academic_year
    }

# ==========================================
# 5. ດຶງຂໍ້ມູນ Profile ໂຕເອງ (Student Only)
# ==========================================
@router.get("/me")
def get_my_student_profile(
    db: Session = Depends(database.get_db),
    current_user: dict = Depends(auth.get_current_user)
):
    if current_user['role'] != 'student':
        raise HTTPException(status_code=403, detail="Not authorized")

    student = db.query(models.Student).filter(models.Student.user_id == current_user['id']).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")
    
    info = db.query(
        models.Class.name.label("class_name"),
        models.Class.id.label("class_id"),
        models.AcademicYear.name.label("academic_year")
    ).join(models.Enrollment, models.Enrollment.class_id == models.Class.id)\
     .join(models.AcademicYear, models.AcademicYear.id == models.Class.year_id)\
     .filter(models.Enrollment.student_id == student.id)\
     .first()
    
    return {
        "id": student.id,
        "full_name": current_user['full_name'],
        "student_code": student.student_code,
        "class_id": info.class_id if info else None,
        "class_name": info.class_name if info else "N/A",
        "academic_year": info.academic_year if info else "N/A",
        "details": {
            "parent": student.parent_name,
            "talents": student.talents,
            "health": student.blood_type
        }
    }

# ==========================================
# 6. ດຶງນັກຮຽນໃນຫ້ອງ (For Class View - Restricted for Teachers)
# ==========================================
@router.get("/class/{class_id}", response_model=List[schemas.StudentFullReport])
def get_students_by_class(
    class_id: int, 
    db: Session = Depends(database.get_db),
    current_user: dict = Depends(auth.get_current_user)
):
    # ✅ Logic ປ້ອງກັນ: ຖ້າເປັນ Teacher ແລະ ບໍ່ແມ່ນຫ້ອງຂອງໂຕເອງ -> ຫ້າມເຂົ້າ
    if current_user['role'] == 'teacher':
        target_class = db.query(models.Class).filter(models.Class.id == class_id).first()
        if not target_class or target_class.teacher_id != current_user['id']:
            raise HTTPException(status_code=403, detail="ທ່ານບໍ່ມີສິດເຂົ້າເຖິງຂໍ້ມູນນັກຮຽນຫ້ອງນີ້")

    query_results = db.query(models.Student, models.User)\
        .join(models.User, models.User.id == models.Student.user_id)\
        .join(models.Enrollment, models.Enrollment.student_id == models.Student.id)\
        .filter(models.Enrollment.class_id == class_id)\
        .all()

    results = []
    for student, user in query_results:
        logs = db.query(models.BehaviorLog).filter(models.BehaviorLog.student_id == student.id).all()
        pos_pts = sum(l.points for l in logs if l.type == "POSITIVE")
        neg_pts = sum(l.points for l in logs if l.type == "NEGATIVE")

        results.append({
            "id": student.id,
            "student_code": student.student_code,
            "full_name": user.full_name,
            "email": user.email,
            "parent_email": student.parent_email,
            "parent_name": student.parent_name,
            "parent_phone": student.parent_phone,
            "blood_type": student.blood_type,
            "talents": student.talents,
            "address_summary": f"ບ້ານ {student.village or ''}, {student.district or ''}",
            "total_merit_points": pos_pts + neg_pts,
            "behavior_logs": logs
        })
    
    return results

# ==========================================
# 7. DASHBOARD (Student Only)
# ==========================================
@router.get("/dashboard")
def get_student_dashboard(
    db: Session = Depends(database.get_db),
    current_user: dict = Depends(auth.get_current_user)
):
    if current_user['role'] != 'student':
        raise HTTPException(status_code=403, detail="Not authorized")

    student = db.query(models.Student).filter(models.Student.user_id == current_user['id']).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    enrollment = db.query(models.Enrollment).filter(models.Enrollment.student_id == student.id).first()
    
    class_name = "N/A"
    upcoming_assignments = []
    today_schedule = []
    total_points = 0

    if enrollment:
        cls = db.query(models.Class).filter(models.Class.id == enrollment.class_id).first()
        if cls:
            class_name = cls.name

        upcoming_assignments = db.query(models.Assignment)\
            .filter(models.Assignment.class_id == enrollment.class_id)\
            .filter(models.Assignment.due_date >= datetime.now())\
            .order_by(models.Assignment.due_date.asc())\
            .limit(5).all()

        today_weekday = datetime.now().weekday() + 1
        
        today_schedule = db.query(models.ClassSchedule)\
            .filter(models.ClassSchedule.class_id == enrollment.class_id)\
            .filter(models.ClassSchedule.day_of_week == str(today_weekday))\
            .order_by(models.ClassSchedule.start_time.asc()).all()

        if not today_schedule:
             today_schedule = db.query(models.ClassSchedule)\
                .filter(models.ClassSchedule.class_id == enrollment.class_id)\
                .order_by(models.ClassSchedule.day_of_week.asc(), models.ClassSchedule.start_time.asc())\
                .all()

    logs = db.query(models.BehaviorLog).filter(models.BehaviorLog.student_id == student.id).all()
    pos_pts = sum(l.points for l in logs if l.type == "POSITIVE")
    neg_pts = sum(l.points for l in logs if l.type == "NEGATIVE")
    total_points = pos_pts + neg_pts

    return {
        "student_info": {
            "name": current_user['full_name'],
            "code": student.student_code,
            "class_name": class_name,
            "total_points": total_points
        },
        "assignments": upcoming_assignments,
        "schedule": today_schedule,
        "message": "Data loaded successfully"
    }

# ==========================================
# 8. FULL SCHEDULE
# ==========================================
@router.get("/schedule")
def get_full_schedule(
    db: Session = Depends(database.get_db),
    current_user: dict = Depends(auth.get_current_user)
):
    if current_user['role'] != 'student':
        raise HTTPException(status_code=403, detail="Not authorized")

    student = db.query(models.Student).filter(models.Student.user_id == current_user['id']).first()
    enrollment = db.query(models.Enrollment).filter(models.Enrollment.student_id == student.id).first()
    
    if not enrollment:
        return []

    schedules = db.query(models.ClassSchedule)\
        .filter(models.ClassSchedule.class_id == enrollment.class_id)\
        .order_by(models.ClassSchedule.day_of_week.asc(), models.ClassSchedule.start_time.asc())\
        .all()
        
    return schedules

# ==========================================
# 9. GET ALL ASSIGNMENTS
# ==========================================
@router.get("/assignments")
def get_student_assignments(
    db: Session = Depends(database.get_db),
    current_user: dict = Depends(auth.get_current_user)
):
    if current_user['role'] != 'student':
        raise HTTPException(status_code=403, detail="Not authorized")

    student = db.query(models.Student).filter(models.Student.user_id == current_user['id']).first()
    enrollment = db.query(models.Enrollment).filter(models.Enrollment.student_id == student.id).first()
    
    if not enrollment:
        return []

    assignments = db.query(models.Assignment)\
        .filter(models.Assignment.class_id == enrollment.class_id)\
        .order_by(models.Assignment.due_date.desc())\
        .all()
        
    return assignments

# ==========================================
# 10. ✅ GET MY GRADES (For Student Mobile App)
# ==========================================
@router.get("/me/grades")
def get_my_grades(
    db: Session = Depends(database.get_db),
    current_user: dict = Depends(auth.get_current_user)
):
    if current_user['role'] != 'student':
        raise HTTPException(status_code=403, detail="Not authorized")

    # 1. ຫາ Student ID ຂອງ User ນີ້
    student = db.query(models.Student).filter(models.Student.user_id == current_user['id']).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")

    # 2. ດຶງຄະແນນທັງໝົດ
    grades = db.query(models.Grade).filter(models.Grade.student_id == student.id).all()
    
    results = []
    months_map = {9: "ກັນຍາ", 10: "ຕຸລາ", 11: "ພະຈິກ", 12: "ທັນວາ", 1: "ມັງກອນ", 2: "ກຸມພາ", 3: "ມີນາ", 4: "ເມສາ", 5: "ພຶດສະພາ"}

    for g in grades:
        # ຄິດໄລ່ເກຣດ
        grade_char = "F"
        if g.total_score >= 80: grade_char = "A"
        elif g.total_score >= 70: grade_char = "B"
        elif g.total_score >= 60: grade_char = "C"
        elif g.total_score >= 50: grade_char = "D"

        results.append({
            "id": g.id,
            "month_name": months_map.get(g.month_id, f"ເດືອນ {g.month_id}"),
            "total_score": g.total_score,
            "grade": grade_char,
            "details": {
                "attendance": g.attendance_score,
                "homework": g.homework_score,
                "midterm": g.midterm_score,
                "final": g.final_score
            }
        })
    
    return results