import models, database
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

def seed_data():
    db = database.SessionLocal()
    print("🌱 Seeding data (OTP System)...")

    # ==========================================
    # 0. RESET DATABASE
    # ==========================================
    # ລຶບຕາຕະລາງເກົ່າ ແລະ ສ້າງໃໝ່ (ເພື່ອລ້າງຂໍ້ມູນເກົ່າທີ່ອາດມີບັນຫາ)
    models.Base.metadata.drop_all(bind=database.engine)
    models.Base.metadata.create_all(bind=database.engine)

    # ==========================================
    # 1. ACADEMIC STRUCTURE (ປີຮຽນ)
    # ==========================================
    year = models.AcademicYear(name="2025-2026", is_active=True)
    db.add(year)
    db.commit()

    # ==========================================
    # 2. USERS (Admin, Head, Teacher) - NO PASSWORD
    # ==========================================
    admin_user = models.User(
        email="admin@school.la", 
        full_name="Admin User", 
        role="admin"
    )

    head_user = models.User(
        email="head@school.la", 
        full_name="Ajan Keo (Head)", 
        role="head_teacher"
    )
    
    teacher_user = models.User(
        email="teacher@school.la", 
        full_name="Ajan Somsak", 
        role="teacher"
    )

    db.add_all([admin_user, head_user, teacher_user])
    db.commit()

    # ==========================================
    # 3. CLASS & SUPERVISION
    # ==========================================
    # ຫົວໜ້າຄູ ຕິດຕາມ ຄູສອນ
    supervision = models.TeacherSupervision(head_teacher_id=head_user.id, teacher_id=teacher_user.id)
    db.add(supervision)

    # ສ້າງຫ້ອງຮຽນ
    cls = models.Class(name="M.4/1", teacher_id=teacher_user.id, year_id=year.id)
    db.add(cls)
    db.commit()

    # ==========================================
    # 4. SCHEDULES (ຕາຕະລາງຮຽນ)
    # ==========================================
    schedules_data = [
        { "subject": "Mathematics", "teacher": "Ajan Somsak", "day": "Monday", "start": "08:00", "end": "09:30", "room": "A101" },
        { "subject": "English", "teacher": "Ajan John", "day": "Tuesday", "start": "08:00", "end": "09:30", "room": "Lab 1" },
        { "subject": "Physics", "teacher": "Ajan Phone", "day": "Wednesday", "start": "10:00", "end": "11:30", "room": "Sci-2" }
    ]

    for sch in schedules_data:
        new_sch = models.ClassSchedule(
            class_id=cls.id,
            subject_name=sch["subject"],
            teacher_name=sch["teacher"],
            day_of_week=sch["day"], 
            start_time=sch["start"], 
            end_time=sch["end"],
            room=sch["room"]
        )
        db.add(new_sch)
    db.commit()

    # ==========================================
    # 5. ASSIGNMENTS (ວຽກບ້ານ)
    # ==========================================
    print("   -> Creating Assignments...")
    
    assign1 = models.Assignment(
        title="Math Homework: Algebra",
        description="ຈົ່ງແກ້ສົມຜົນຂັ້ນສອງ ຂໍ້ 1-10 ໜ້າ 45",
        file_url="https://example.com/math.pdf",
        due_date=datetime.utcnow() + timedelta(days=3),
        class_id=cls.id
    )

    assign2 = models.Assignment(
        title="Lao Language: Essay",
        description="ຂຽນບົດພັນລະນາທຳມະຊາດ",
        due_date=datetime.utcnow() + timedelta(days=7),
        class_id=cls.id
    )
    
    db.add(assign1)
    db.add(assign2)
    db.commit()

    # ==========================================
    # 6. PARENTS (User Role Only)
    # ==========================================
    print("   -> Creating Parent User...")
    
    # ສ້າງ User ຜູ້ປົກຄອງ (ບໍ່ມີ Password)
    parent_user = models.User(
        email="parent@school.la",
        full_name="Thao Bounmy (Parent)",
        role="parent"
    )
    db.add(parent_user)
    db.commit()

    # ==========================================
    # 7. STUDENTS & DATA
    # ==========================================
    students_list = [
        { "email": "std1@school.la", "name": "Khamla Sithavong", "code": "S001", "blood": "O", "talent": "ແຕ້ມຮູບ", "village": "Naxay" },
        { "email": "std2@school.la", "name": "Somsy Keo", "code": "S002", "blood": "A", "talent": "ຮ້ອງເພງ", "village": "Sonsai" },
        { "email": "std3@school.la", "name": "Vong Vongsa", "code": "S003", "blood": "B", "talent": "ເຕະບານ", "village": "Thongkhankham" }
    ]

    for s in students_list:
        # 1. ສ້າງ User ນັກຮຽນ (ບໍ່ມີ Password)
        user = models.User(
            email=s["email"], 
            full_name=s["name"], 
            role="student"
        )
        db.add(user)
        db.commit()
        
        # 2. ສ້າງ Profile ນັກຮຽນ
        student = models.Student(
            user_id=user.id, 
            student_code=s["code"], 
            full_name=s["name"],
            
            # ຂໍ້ມູນຜູ້ປົກຄອງ (Text ສຳລັບຕິດຕໍ່ດ່ວນ)
            parent_name=parent_user.full_name,
            parent_phone="020 99998888",
            parent_email=parent_user.email,

            blood_type=s["blood"],
            talents=s["talent"],
            village=s["village"]
        )
        
        # ✅ ເຊື່ອມໂຍງຜູ້ປົກຄອງເຂົ້າກັບນັກຮຽນ (Many-to-Many)
        student.parents.append(parent_user)
        
        db.add(student)
        db.commit()

        # 3. ລົງທະບຽນເຂົ້າຫ້ອງ
        enroll = models.Enrollment(student_id=student.id, class_id=cls.id)
        db.add(enroll)

        # 4. ສ້າງຄະແນນຕົວຢ່າງ (✅ ແຍກວິຊາ subject_name)
        db.add(models.Grade(
            student_id=student.id, class_id=cls.id, month_id=9, 
            subject_name="GENERAL", # ວິຊາລວມ
            attendance_score=10, homework_score=15, midterm_score=20, final_score=30
        ))
        db.add(models.Grade(
            student_id=student.id, class_id=cls.id, month_id=9, 
            subject_name="MATH", # ວິຊາຄະນິດສາດ
            attendance_score=8, homework_score=18, midterm_score=25, final_score=35
        ))

        # 5. ສ້າງຂໍ້ມູນເຊັກຊື່ (✅ ແຍກ Period)
        db.add(models.Attendance(
            student_id=student.id, class_id=cls.id, date="2026-01-24",
            status="PRESENT", period="DAILY"
        ))

    db.commit()
    print("✅ Seed Data Success (OTP Mode)!")
    print("---------------------------------------")
    print(f"👉 Admin:    admin@school.la")
    print(f"👉 Head:     head@school.la")
    print(f"👉 Teacher:  teacher@school.la")
    print(f"👉 Student:  std1@school.la")
    print(f"👉 Parent:   parent@school.la")
    print("---------------------------------------")
    print("ℹ️ Note: Use OTP Login (Enter email -> Get OTP from Console -> Verify)")

if __name__ == "__main__":
    try:
        seed_data()
    except Exception as e:
        print(f"⚠️ Error: {e}")