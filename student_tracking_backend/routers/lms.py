from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from sqlalchemy import and_
import shutil, os
from datetime import datetime
from typing import List, Optional
import models, schemas, database, auth

# 1. ຕັ້ງຄ່າບ່ອນເກັບໄຟລ໌
UPLOAD_DIR = "static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True) # ສ້າງ Folder ອັດຕະໂນມັດຖ້າຍັງບໍ່ມີ

router = APIRouter(prefix="/lms", tags=["LMS (Assignments & Grading)"])

# ==========================================
# 1. TEACHER: ສ້າງວຽກບ້ານ (Create Assignment)
# ==========================================
@router.post("/assignments")
def create_assignment(
    # ✅ ໃຊ້ Form(...) ເພາະ Frontend ສົ່ງມາແບບ FormData
    class_id: int = Form(...),
    title: str = Form(...),
    description: Optional[str] = Form(None),
    due_date: str = Form(...), # format: "YYYY-MM-DDTHH:MM"
    file: UploadFile = File(None), # ໄຟລ໌ໂຈດ (Optional)
    db: Session = Depends(database.get_db),
    current_user: dict = Depends(auth.get_current_user)
):
    if current_user['role'] not in ['teacher', 'head_teacher', 'admin']:
        raise HTTPException(status_code=403, detail="Not authorized")

    file_path = None
    
    # ບັນທຶກໄຟລ໌ໂຈດ (ຖ້າມີ)
    if file:
        try:
            timestamp = int(datetime.now().timestamp())
            # ລ້າງຊື່ໄຟລ໌ໃຫ້ປອດໄພ (ປ່ຽນຍະຫວ່າງເປັນ _)
            safe_filename = file.filename.replace(" ", "_")
            filename = f"{timestamp}_{safe_filename}"
            file_location = os.path.join(UPLOAD_DIR, filename)
            
            with open(file_location, "wb+") as file_object:
                shutil.copyfileobj(file.file, file_object)
            
            # ໃຊ້ Path ແບບ Relative
            file_path = f"static/uploads/{filename}"
        except Exception as e:
            print(f"Upload Error: {e}")

    # ແປງວັນທີ (ປ້ອງກັນ Error)
    try:
        parsed_due_date = datetime.fromisoformat(due_date)
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid date format")

    # ຈັດການ Description (ກັນພາດສົ່ງ string 'null' ມາ)
    final_desc = description
    if description == "null":
        final_desc = ""

    new_assign = models.Assignment(
        class_id=class_id,
        title=title,
        description=final_desc,
        file_url=file_path,
        due_date=parsed_due_date
    )
    db.add(new_assign)
    db.commit()
    db.refresh(new_assign)
    
    return {"message": "Assignment created", "id": new_assign.id}

# ==========================================
# 2. TEACHER: ດຶງວຽກບ້ານຕາມຫ້ອງ (ສຳລັບ Frontend Filter)
# ==========================================
@router.get("/assignments/class/{class_id}", response_model=List[schemas.AssignmentResponse])
def get_assignments_by_class(
    class_id: int, 
    db: Session = Depends(database.get_db)
):
    assignments = db.query(models.Assignment)\
        .filter(models.Assignment.class_id == class_id)\
        .order_by(models.Assignment.created_at.desc())\
        .all()
        
    for a in assignments:
        if a.classroom:
            a.class_name = a.classroom.name
            
    return assignments

# ==========================================
# 3. TEACHER: ລຶບວຽກບ້ານ
# ==========================================
@router.delete("/assignments/{id}")
def delete_assignment(
    id: int,
    db: Session = Depends(database.get_db),
    current_user: dict = Depends(auth.get_current_user)
):
    if current_user['role'] not in ['teacher', 'admin']:
        raise HTTPException(status_code=403, detail="Not authorized")

    assign = db.query(models.Assignment).filter(models.Assignment.id == id).first()
    if not assign:
        raise HTTPException(status_code=404, detail="Assignment not found")

    # (Optional) ລຶບໄຟລ໌ອອກຈາກ Disk ນຳ
    if assign.file_url:
        try:
            file_path = assign.file_url.replace("/", os.sep)
            if os.path.exists(file_path):
                os.remove(file_path)
        except:
            pass

    db.delete(assign)
    db.commit()
    return {"message": "Deleted successfully"}

# ==========================================
# 4. STUDENT: ສົ່ງວຽກ (Upload Submission)
# ==========================================
@router.post("/submissions/")
def submit_homework(
    assignment_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(database.get_db),
    current_user: dict = Depends(auth.get_current_user)
):
    if current_user['role'] != 'student':
        raise HTTPException(status_code=403, detail="Student only")

    # ຊອກຫາ Student ID ຈາກ User Login
    student = db.query(models.Student).filter(models.Student.user_id == current_user['id']).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")
    
    # ບັນທຶກໄຟລ໌ຄຳຕອບ
    timestamp = int(datetime.now().timestamp())
    safe_filename = file.filename.replace(" ", "_")
    filename = f"sub_{student.id}_{timestamp}_{safe_filename}"
    file_location = os.path.join(UPLOAD_DIR, filename)
    
    with open(file_location, "wb+") as file_object:
        shutil.copyfileobj(file.file, file_object)

    file_path = f"static/uploads/{filename}"

    # ກວດສອບວ່າເຄີຍສົ່ງແລ້ວບໍ່? (Update or Create)
    existing_sub = db.query(models.Submission).filter(
        models.Submission.assignment_id == assignment_id,
        models.Submission.student_id == student.id
    ).first()

    if existing_sub:
        existing_sub.file_url = file_path
        existing_sub.submitted_at = datetime.utcnow()
        db.commit()
        return {"message": "Submission updated", "file_url": file_path}
    else:
        submission = models.Submission(
            assignment_id=assignment_id,
            student_id=student.id,
            file_url=file_path
        )
        db.add(submission)
        db.commit()
        return {"message": "Submitted successfully", "file_url": file_path}

# ==========================================
# 5. TEACHER: ດຶງລາຍຊື່ນັກຮຽນທີ່ສົ່ງວຽກ (Grading)
# ==========================================
@router.get("/assignments/{assignment_id}/submissions")
def get_submissions_by_assignment(
    assignment_id: int,
    db: Session = Depends(database.get_db),
    current_user: dict = Depends(auth.get_current_user)
):
    if current_user['role'] not in ['teacher', 'admin']:
        raise HTTPException(status_code=403, detail="Not authorized")

    assignment = db.query(models.Assignment).filter(models.Assignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    # 1. ດຶງນັກຮຽນທັງໝົດໃນຫ້ອງ
    students = db.query(models.Student).join(models.Enrollment).filter(
        models.Enrollment.class_id == assignment.class_id
    ).all()

    results = []
    for std in students:
        # 2. ດຶງ Submission ຖ້າມີ
        sub = db.query(models.Submission).filter(
            models.Submission.assignment_id == assignment_id,
            models.Submission.student_id == std.id
        ).first()

        status = "MISSING"
        if sub:
            status = "SUBMITTED"
        elif assignment.due_date and assignment.due_date < datetime.now():
            status = "LATE"
        
        # ຫາຊື່ (Logic ປ້ອງກັນຊື່ວ່າງ)
        full_name = std.full_name
        if not full_name and std.user_id:
            user = db.query(models.User).filter(models.User.id == std.user_id).first()
            if user: full_name = user.full_name
        
        if not full_name: full_name = "Unknown Student"

        results.append({
            "id": sub.id if sub else None, # submission_id
            "student_id": std.id,
            "full_name": full_name,
            "student_code": std.student_code or "N/A",
            "status": status,
            "file_url": sub.file_url if sub else None,
            "submitted_at": sub.submitted_at if sub else None,
            "score": sub.score if sub else None,
            "feedback": sub.feedback if sub else None
        })
        
    return results

# ==========================================
# 6. TEACHER: ໃຫ້ຄະແນນ (Grade Submission)
# ==========================================
@router.post("/grade")
def grade_submission(
    grade_data: schemas.SubmissionGrade,
    db: Session = Depends(database.get_db),
    current_user: dict = Depends(auth.get_current_user)
):
    if current_user['role'] not in ['teacher', 'admin']:
        raise HTTPException(status_code=403, detail="Not authorized")

    if grade_data.submission_id:
        sub = db.query(models.Submission).filter(models.Submission.id == grade_data.submission_id).first()
        if sub:
            sub.score = grade_data.score
            sub.feedback = grade_data.feedback
            db.commit()
            return {"message": "Graded successfully"}
    
    raise HTTPException(status_code=404, detail="Submission not found")

# ==========================================
# 7. UTILS: ດຶງລາຍຊື່ຫ້ອງຮຽນຂອງຄູ (Dropdown)
# ==========================================
@router.get("/my-classes")
def get_teacher_classes(
    db: Session = Depends(database.get_db),
    current_user: dict = Depends(auth.get_current_user)
):
    if current_user['role'] not in ['teacher', 'admin']:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    query = db.query(models.Class)
    if current_user['role'] == 'teacher':
        query = query.filter(models.Class.teacher_id == current_user['id'])
        
    return query.all()

# ==========================================
# 9. STUDENT: ດຶງວຽກບ້ານຂອງຂ້ອຍ (ພ້ອມສະຖານະ)
# ==========================================
@router.get("/student/assignments", response_model=List[schemas.StudentAssignmentResponse])
def get_my_assignments(
    db: Session = Depends(database.get_db),
    current_user: dict = Depends(auth.get_current_user)
):
    if current_user['role'] != 'student':
        raise HTTPException(status_code=403, detail="Student only")

    # 1. ຫາ Student
    student = db.query(models.Student).filter(models.Student.user_id == current_user['id']).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")

    # 2. ຫາ Enrollment
    enrollment = db.query(models.Enrollment).filter(models.Enrollment.student_id == student.id).first()
    if not enrollment:
        return []

    # 3. ດຶງ Assignments
    assignments = db.query(models.Assignment)\
        .filter(models.Assignment.class_id == enrollment.class_id)\
        .order_by(models.Assignment.created_at.desc())\
        .all()

    results = []
    for assign in assignments:
        # Check Submission
        sub = db.query(models.Submission).filter(
            models.Submission.assignment_id == assign.id,
            models.Submission.student_id == student.id
        ).first()

        assign_data = schemas.StudentAssignmentResponse(
            **assign.__dict__,
            class_name=assign.classroom.name if assign.classroom else "Unknown",
            submission=sub 
        )
        results.append(assign_data)

    return results