from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List
import models, schemas, auth, database
from email_utils import send_otp_email # ✅ Import ຟັງຊັນສົ່ງເມວ

router = APIRouter(tags=["Users & Authentication"])

# ==========================================
# 🔐 SECTION 1: AUTHENTICATION (Login/OTP)
# ==========================================

# 1. ຂໍ OTP (Step 1) - Login ດ້ວຍ Email
@router.post("/auth/login")
def request_otp(request: schemas.LoginRequest, db: Session = Depends(database.get_db)):
    # ກວດວ່າ User ມີໃນລະບົບບໍ່
    user = db.query(models.User).filter(models.User.email == request.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Email not found in system")

    # ສ້າງ OTP
    otp = auth.generate_otp()
    
    # ບັນທຶກ OTP ລົງ DB
    expires_at = datetime.utcnow() + timedelta(minutes=5) # ອາຍຸ 5 ນາທີ
    new_otp = models.OTPCode(email=request.email, code=otp, expires_at=expires_at)
    db.add(new_otp)
    db.commit()

    # ====================================================
    # ✅ UPDATE: ສົ່ງ Email ແທ້ (ແທນການ Print)
    # ====================================================
    email_sent = send_otp_email(request.email, otp)

    if email_sent:
        return {"message": "✅ ສົ່ງ OTP ໄປທາງ Email ສຳເລັດແລ້ວ! (Sent to Email)"}
    else:
        # ⚠️ ກໍລະນີສົ່ງບໍ່ໄດ້ (Fallback): ໃຫ້ Print ອອກ Console ຄືເກົ່າ ເພື່ອບໍ່ໃຫ້ລະບົບຕິດຂັດ
        print(f"=============================")
        print(f"❌ Email Sending Failed!")
        print(f"🔑 Backup OTP for {request.email}: {otp}")
        print(f"=============================")
        return {"message": "⚠️ ສົ່ງ Email ບໍ່ໄດ້! ກະລຸນາເບິ່ງລະຫັດໃນ Console (Server Log)"}


# 2. ຢືນຢັນ OTP ແລະ ຮັບ Token (Step 2)
@router.post("/auth/verify", response_model=schemas.TokenResponse)
def verify_otp(request: schemas.VerifyOTPRequest, db: Session = Depends(database.get_db)):
    # ຊອກຫາ OTP ລ່າສຸດຂອງ Email ນີ້
    otp_record = db.query(models.OTPCode).filter(
        models.OTPCode.email == request.email,
        models.OTPCode.code == request.otp_code,
        models.OTPCode.is_used == False
    ).first()

    if not otp_record:
        raise HTTPException(status_code=400, detail="Invalid OTP")
    
    if datetime.utcnow() > otp_record.expires_at:
        raise HTTPException(status_code=400, detail="OTP Expired")

    # ໝາຍວ່າໃຊ້ແລ້ວ
    otp_record.is_used = True
    db.commit()

    # ດຶງຂໍ້ມູນ User ເພື່ອເອົາ Role
    user = db.query(models.User).filter(models.User.email == request.email).first()

    # ສ້າງ JWT Token
    access_token = auth.create_access_token(data={"sub": user.email, "role": user.role})
    
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "role": user.role
    }

# ==========================================
# 👤 SECTION 2: USER PROFILE
# ==========================================

# 3. ດຶງຂໍ້ມູນໂຕເອງ (Profile)
@router.get("/users/me", response_model=schemas.UserResponse)
def read_users_me(current_user: dict = Depends(auth.get_current_user), db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.email == current_user['email']).first()
    return user

# ==========================================
# 🛠️ SECTION 3: ADMIN MANAGEMENT (CRUD)
# ==========================================

# 4. ດຶງ User ທັງໝົດ (Admin Only)
@router.get("/users/", response_model=List[schemas.UserResponse])
def get_all_users(
    role: str = None, 
    db: Session = Depends(database.get_db),
    current_user: dict = Depends(auth.get_current_user)
):
    if current_user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Not authorized")
    
    query = db.query(models.User)
    if role:
        query = query.filter(models.User.role == role)
    
    return query.all()

# 5. ສ້າງ User ໃໝ່ (Admin Only) - ❌ NO PASSWORD
@router.post("/users/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserResponse)
def create_user(
    user_in: schemas.UserCreate,
    db: Session = Depends(database.get_db),
    current_user: dict = Depends(auth.get_current_user)
):
    if current_user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Not authorized")
    
    existing = db.query(models.User).filter(models.User.email == user_in.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already exists")
    
    # ✅ ສ້າງ User ໂດຍບໍ່ມີ Password (ເພາະໃຊ້ OTP)
    new_user = models.User(
        email=user_in.email,
        full_name=user_in.full_name,
        role=user_in.role,
        is_active=True
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # 🔥🔥 Logic: ຖ້າເລືອກລູກມາ (student_ids) ໃຫ້ອັບເດດ parent_email ຂອງນັກຮຽນ 🔥🔥
    if user_in.student_ids and len(user_in.student_ids) > 0:
        students = db.query(models.Student).filter(models.Student.id.in_(user_in.student_ids)).all()
        for std in students:
            std.parent_email = new_user.email # ✅ ຜູກ Email
        db.commit()

    return new_user

# 6. ແກ້ໄຂ User (Admin Only) - ❌ NO PASSWORD Update
@router.put("/users/{user_id}", response_model=schemas.UserResponse)
def update_user(
    user_id: int,
    user_in: schemas.UserUpdate,
    db: Session = Depends(database.get_db),
    current_user: dict = Depends(auth.get_current_user)
):
    if current_user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Not authorized")
    
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # ເກັບ Email ເກົ່າໄວ້ກ່ອນ
    old_email = user.email
    
    # ອັບເດດຂໍ້ມູນ
    update_data = user_in.dict(exclude_unset=True)
    
    # ດຶງ student_ids ອອກມາແຍກຕ່າງຫາກ (ເພາະບໍ່ມີໃນ Table User)
    student_ids = update_data.pop("student_ids", None)

    for key, value in update_data.items():
        setattr(user, key, value)
    
    # 🔥🔥 Logic: ອັບເດດລູກ (ຖ້າມີການສົ່ງ student_ids ມາ) 🔥🔥
    new_email = user.email # Email ປັດຈຸບັນ (ອາດຈະຖືກປ່ຽນ ຫຼື ບໍ່)

    if student_ids is not None: # ຖ້າ User ສົ່ງ list ມາ (ເຖິງຈະ empty list ກໍຕາມ)
        # 1. (Optional) ລ້າງ parent_email ເກົ່າທີ່ເຄີຍຜູກກັບ Email ເກົ່າ
        # db.query(models.Student).filter(models.Student.parent_email == old_email).update({"parent_email": None})
        
        # 2. ຜູກ Email ໃໝ່ກັບນັກຮຽນທີ່ເລືອກ
        if len(student_ids) > 0:
            students = db.query(models.Student).filter(models.Student.id.in_(student_ids)).all()
            for std in students:
                std.parent_email = new_email
    
    # ຖ້າປ່ຽນ Email ແຕ່ບໍ່ໄດ້ສົ່ງ student_ids ມາ -> ໃຫ້ອັບເດດລູກເກົ່າໃຫ້ເປັນ Email ໃໝ່
    elif old_email != new_email: 
        db.query(models.Student).filter(models.Student.parent_email == old_email).update({"parent_email": new_email})

    db.commit()
    db.refresh(user)
    return user

# 7. ລຶບ User (Admin Only)
@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(database.get_db),
    current_user: dict = Depends(auth.get_current_user)
):
    if current_user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Not authorized")
    
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    db.delete(user)
    db.commit()
    return {"message": "Deleted successfully"}

# ==========================================
# 🔗 SECTION 4: LINKING & ADVANCED
# ==========================================

# 8. (Admin Only) ຕັ້ງຫົວໜ້າຄູ ໃຫ້ເບິ່ງແຍງຄູ (Max 3 ຄົນ)
@router.post("/users/assign-supervision")
def assign_teacher_supervision(
    request: schemas.AssignTeacherRequest,
    db: Session = Depends(database.get_db),
    current_user: dict = Depends(auth.get_current_user)
):
    if current_user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Not authorized")

    count = db.query(models.TeacherSupervision).filter(
        models.TeacherSupervision.head_teacher_id == request.head_teacher_id
    ).count()

    if count >= 3:
        raise HTTPException(status_code=400, detail="Error: This Head Teacher already supervises 3 teachers.")

    new_link = models.TeacherSupervision(
        head_teacher_id=request.head_teacher_id,
        teacher_id=request.teacher_id
    )
    db.add(new_link)
    db.commit()
    return {"message": "Assigned teacher successfully"}

# 9. (Admin Only) ຜູກຜູ້ປົກຄອງ ໃສ່ກັບນັກຮຽນ (Manual Link)
@router.post("/users/link-parent")
def link_parent_to_student(
    request: schemas.AssignParentRequest,
    db: Session = Depends(database.get_db),
    current_user: dict = Depends(auth.get_current_user)
):
    if current_user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Not authorized")

    # ອັບເດດ parent_email ໃນຕາຕະລາງ Student
    student = db.query(models.Student).filter(models.Student.student_code == request.student_code).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    student.parent_email = request.parent_email
    db.commit()
    
    return {"message": f"Linked parent {request.parent_email} to student {student.student_code}"}

# (Optional) ສ້າງ User ທົດສອບ
@router.post("/seed/create-admin")
def create_test_admin(db: Session = Depends(database.get_db)):
    # ກວດວ່າສ້າງໄປແລ້ວບໍ່
    if db.query(models.User).filter(models.User.email == "admin@school.la").first():
        return {"message": "Admin already exists"}

    fake_admin = models.User(
        email="admin@school.la", 
        full_name="Admin Somsak", 
        role="admin"
    )
    db.add(fake_admin)
    db.commit()
    return {"message": "Created Admin User: admin@school.la"}