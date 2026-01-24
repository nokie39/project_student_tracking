from database import SessionLocal, engine
import models
from datetime import time, datetime, timedelta

# ==========================================
# 0. SETUP DATABASE
# ==========================================
# ⚠️ ລຶບ Table ເກົ່າ ແລະ ສ້າງໃໝ່ (ເພື່ອໃຫ້ Table ໃໝ່ຢ່າງ Parents ເຮັດວຽກ)
models.Base.metadata.drop_all(bind=engine)
models.Base.metadata.create_all(bind=engine)
db = SessionLocal()

def seed_data():
    print("🌱 Seeding data for OTP Auth System...")

    # ==========================================
    # 1. ACADEMIC STRUCTURE (ປີຮຽນ)
    # ==========================================
    year = models.AcademicYear(name="2025-2026", is_active=True)
    db.add(year)
    db.commit()

    # ==========================================
    # 2. USERS (Teacher & Head)
    # ==========================================
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

    db.add_all([head_user, teacher_user])
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
    # ⚠️ ໝາຍເຫດ: ໃສ່ day_of_week ເປັນພາສາອັງກິດ Monday, Tuesday...
    schedules_data = [
        { "subject": "Mathematics", "teacher": "Ajan Somsak", "day": "Monday", "start": "08:00", "end": "09:30", "room": "A101", "note": "ກຽມເຄື່ອງຄິດເລກ" },
        { "subject": "English", "teacher": "Ajan John", "day": "Tuesday", "start": "08:00", "end": "09:30", "room": "Lab 1", "note": "Quiz Chapter 1" },
        { "subject": "Physics", "teacher": "Ajan Phone", "day": "Wednesday", "start": "10:00", "end": "11:30", "room": "Sci-2", "note": "" }
    ]

    for sch in schedules_data:
        new_sch = models.ClassSchedule(
            class_id=cls.id,
            subject_name=sch["subject"],
            teacher_name=sch["teacher"],
            day_of_week=sch["day"], # ✅ ແກ້ເປັນ String: Monday
            start_time=sch["start"], # ✅ ແກ້ເປັນ String: 08:00
            end_time=sch["end"],
            room=sch["room"],
            note=sch["note"]
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
        file_url="https://example.com/math_worksheet.pdf",
        due_date=datetime.utcnow() + timedelta(days=3),
        class_id=cls.id
    )

    assign2 = models.Assignment(
        title="Lao Language: Essay",
        description="ຂຽນບົດພັນລະນາທຳມະຊາດ",
        file_url="", # ບໍ່ມີໄຟລ໌
        due_date=datetime.utcnow() + timedelta(days=7),
        class_id=cls.id
    )
    
    db.add(assign1)
    db.add(assign2)
    db.commit()

    # ==========================================
    # 6. PARENTS (✅ ເພີ່ມໃໝ່)
    # ==========================================
    print("   -> Creating Parent User...")
    
    # 1. ສ້າງ User ສຳລັບ Login
    parent_user = models.User(
        email="parent@school.la",
        full_name="Thao Bounmy (Parent)",
        role="parent"
    )
    db.add(parent_user)
    db.commit()

    # 2. ສ້າງ Profile ຜູ້ປົກຄອງ
    parent_profile = models.Parent(
        user_id=parent_user.id,
        phone_number="020 99998888"
    )
    db.add(parent_profile)
    db.commit()


    # ==========================================
    # 7. STUDENTS & SUBMISSIONS
    # ==========================================
    students_list = [
        { "email": "std1@school.la", "name": "Khamla Sithavong", "code": "S001", "blood": "O", "talent": "ແຕ້ມຮູບ", "village": "Naxay" },
        { "email": "std2@school.la", "name": "Somsy Keo", "code": "S002", "blood": "A", "talent": "ຮ້ອງເພງ", "village": "Sonsai" }
    ]

    for s in students_list:
        # 1. ສ້າງ User (ສຳລັບ Login OTP)
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
            
            # ✅ ເຊື່ອມໂຍງກັບ Parent ທີ່ສ້າງໄວ້ຂ້າງເທິງ
            parent_id=parent_profile.id,
            parent_name=parent_user.full_name,
            parent_phone=parent_profile.phone_number,

            date_of_birth="2010-05-15",
            blood_type=s["blood"],
            talents=s["talent"],
            village=s["village"],
            district="Xaysettha",
            province="Vientiane"
        )
        db.add(student)
        db.commit()

        # 3. ລົງທະບຽນເຂົ້າຫ້ອງ
        enroll = models.Enrollment(student_id=student.id, class_id=cls.id)
        db.add(enroll)
        db.commit()

        # 4. ຂໍ້ມູນສະເພາະ S001 (Behavior + Submission)
        if s["code"] == "S001":
            # 4.1 ບັນທຶກພຶດຕິກຳ
            logs = [
                models.BehaviorLog(
                    student_id=student.id, teacher_id=teacher_user.id, 
                    type="POSITIVE", title="Good Helper", 
                    description="Helped clean the room", points=10
                ),
                models.BehaviorLog(
                    student_id=student.id, teacher_id=teacher_user.id, 
                    type="NEGATIVE", title="Late", 
                    description="Arrived late 15 mins", points=-5
                )
            ]
            db.add_all(logs)

            # 4.2 ສ້າງຂໍ້ມູນການສົ່ງວຽກ (Submission)
            submission = models.Submission(
                assignment_id=assign1.id,
                student_id=student.id,
                file_url="https://example.com/homework_answer.jpg",
                score=None, 
                feedback=None
            )
            db.add(submission)

    db.commit()
    print("✅ Seed Data Success!")
    print("---------------------------------------")
    print("Use these emails to request OTP:")
    print(f"👉 Head Teacher: head@school.la")
    print(f"👉 Teacher:      teacher@school.la")
    print(f"👉 Student:      std1@school.la")
    print(f"👉 Parent:       parent@school.la  (Has 2 children)")
    print("---------------------------------------")

if __name__ == "__main__":
    try:
        seed_data()
    except Exception as e:
        print(f"⚠️ Error: {e}")
    finally:
        db.close()