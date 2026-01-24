from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Float, DateTime, Text, Table
from sqlalchemy.orm import relationship
from database import Base
from sqlalchemy.sql import func
from datetime import datetime

# ==========================================
# 0. ASSOCIATION TABLES (Many-to-Many)
# ==========================================

# ຕາຕະລາງເຊື່ອມໂຍງ ຜູ້ປົກຄອງ <-> ນັກຮຽນ (Many-to-Many)
# ເພາະ: ຜູ້ປົກຄອງ 1 ຄົນ ມີລູກໄດ້ຫຼາຍຄົນ / ນັກຮຽນ 1 ຄົນ ອາດມີຜູ້ປົກຄອງ 2 ຄົນ (ພໍ່+ແມ່)
parent_student_link = Table(
    'parent_student_link',
    Base.metadata,
    Column('parent_user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('student_id', Integer, ForeignKey('students.id'), primary_key=True)
)

# ==========================================
# 1. USERS & AUTH
# ==========================================
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    full_name = Column(String)
    role = Column(String) # admin, teacher, head_teacher, parent, student
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    student = relationship("Student", back_populates="user", uselist=False)
    
    # ✅ ສຳລັບຜູ້ປົກຄອງ: ເຊື່ອມຫາລູກຫຼາຍຄົນຜ່ານ Table ກາງ
    children = relationship(
        "Student",
        secondary=parent_student_link,
        back_populates="parents"
    )

class OTPCode(Base):
    __tablename__ = "otp_codes"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, index=True)
    code = Column(String)
    expires_at = Column(DateTime)
    is_used = Column(Boolean, default=False)

# ==========================================
# 2. ACADEMIC STRUCTURE
# ==========================================
class AcademicYear(Base):
    __tablename__ = "academic_years"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String) # e.g., "2025-2026"
    is_active = Column(Boolean, default=False)
    
    classes = relationship("Class", back_populates="academic_year")

class Class(Base):
    __tablename__ = "classes"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String) # e.g., "M.4/1"
    teacher_id = Column(Integer, ForeignKey("users.id"))
    year_id = Column(Integer, ForeignKey("academic_years.id"))
    
    academic_year = relationship("AcademicYear", back_populates="classes")
    enrollments = relationship("Enrollment", back_populates="classroom")
    schedules = relationship("ClassSchedule", back_populates="classroom")
    assignments = relationship("Assignment", back_populates="classroom")

# ==========================================
# 3. STUDENTS & ENROLLMENT
# ==========================================
class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True, index=True)
    student_code = Column(String, unique=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True) # Login Account (ຖ້າມີ)

    # --- ຂໍ້ມູນສ່ວນຕົວ ---
    full_name = Column(String)
    date_of_birth = Column(String, nullable=True)
    
    # --- ຂໍ້ມູນຄອບຄົວ (ເກັບໄວ້ຕິດຕໍ່) ---
    parent_name = Column(String, nullable=True)
    parent_phone = Column(String, nullable=True)
    parent_email = Column(String, nullable=True) # ✅ ເພີ່ມຕາມທີ່ທ່ານຂໍ
    
    # --- ຂໍ້ມູນສຸຂະພາບ ---
    blood_type = Column(String, nullable=True)
    allergies = Column(Text, nullable=True)
    health_info = Column(Text, nullable=True)
    
    # --- ທີ່ຢູ່ ---
    address = Column(String, nullable=True)
    village = Column(String, nullable=True)
    district = Column(String, nullable=True)
    province = Column(String, nullable=True)
    
    # --- ພອນສະຫວັນ ---
    talents = Column(Text, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="student")
    
    # ✅ Relationship ກັບ Parent (Many-to-Many)
    parents = relationship(
        "User",
        secondary=parent_student_link,
        back_populates="children"
    )

    enrollments = relationship("Enrollment", back_populates="student")
    grades = relationship("Grade", back_populates="student")
    behavior_logs = relationship("BehaviorLog", back_populates="student")
    submissions = relationship("Submission", back_populates="student")

class Enrollment(Base):
    __tablename__ = "enrollments"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    class_id = Column(Integer, ForeignKey("classes.id"))
    enrolled_at = Column(DateTime, default=datetime.utcnow)

    student = relationship("Student", back_populates="enrollments")
    classroom = relationship("Class", back_populates="enrollments")

# ==========================================
# 4. GRADES (Core Grading System)
# ==========================================
class Grade(Base):
    __tablename__ = "grades"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    class_id = Column(Integer, ForeignKey("classes.id"))
    month_id = Column(Integer) # 1=Sep, 2=Oct...
    
    attendance_score = Column(Float, default=0)
    homework_score = Column(Float, default=0)
    midterm_score = Column(Float, default=0)
    final_score = Column(Float, default=0)
    total_score = Column(Float, default=0)

    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    student = relationship("Student", back_populates="grades")

class GradeAuditLog(Base):
    __tablename__ = "grade_audit_logs"
    id = Column(Integer, primary_key=True, index=True)
    grade_id = Column(Integer, ForeignKey("grades.id"))
    old_score = Column(Float)
    new_score = Column(Float)
    updated_by = Column(Integer, ForeignKey("users.id"))
    reason = Column(Text)
    updated_at = Column(DateTime, default=datetime.utcnow)

# ==========================================
# 5. BEHAVIOR & ACTIVITIES
# ==========================================
class BehaviorLog(Base):
    __tablename__ = "behavior_logs"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    teacher_id = Column(Integer, ForeignKey("users.id"))
    
    type = Column(String) # POSITIVE / NEGATIVE
    title = Column(String)
    description = Column(Text, nullable=True)
    points = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    student = relationship("Student", back_populates="behavior_logs")

# ==========================================
# 6. SCHEDULES & ATTENDANCE
# ==========================================
class ClassSchedule(Base):
    __tablename__ = "class_schedules"
    id = Column(Integer, primary_key=True, index=True)
    class_id = Column(Integer, ForeignKey("classes.id"))
    subject_name = Column(String)
    teacher_name = Column(String, nullable=True)
    day_of_week = Column(String) # ✅ String (Monday, Tuesday...)
    start_time = Column(String) 
    end_time = Column(String)   
    room = Column(String)
    note = Column(Text, nullable=True)
    
    classroom = relationship("Class", back_populates="schedules")

class Attendance(Base):
    __tablename__ = "attendance"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    class_id = Column(Integer, ForeignKey("classes.id"))
    date = Column(String) # "YYYY-MM-DD"
    status = Column(String) # "PRESENT", "ABSENT", "LATE"

    # ✅ ເພີ່ມ: ເກັບຄາບຮຽນ (ເຊັ່ນ: 1, 2, 3 ຫຼື ຊື່ວິຊາ)
    period = Column(String, default="DAILY") 
    remark = Column(String, nullable=True)

# ==========================================
# 7. TEACHER SUPERVISION
# ==========================================
class TeacherSupervision(Base):
    __tablename__ = "teacher_supervisions"
    id = Column(Integer, primary_key=True, index=True)
    head_teacher_id = Column(Integer, ForeignKey("users.id"))
    teacher_id = Column(Integer, ForeignKey("users.id"))

# ==========================================
# 8. LMS & ASSIGNMENTS
# ==========================================
class Assignment(Base):
    __tablename__ = "assignments"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(Text, nullable=True)
    file_url = Column(String, nullable=True)
    due_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    class_id = Column(Integer, ForeignKey("classes.id"))
    
    classroom = relationship("Class", back_populates="assignments")
    submissions = relationship("Submission", back_populates="assignment")

class Submission(Base):
    __tablename__ = "submissions"
    id = Column(Integer, primary_key=True, index=True)
    assignment_id = Column(Integer, ForeignKey("assignments.id"))
    student_id = Column(Integer, ForeignKey("students.id"))
    file_url = Column(String)
    score = Column(Float, nullable=True)
    feedback = Column(Text, nullable=True)
    submitted_at = Column(DateTime, default=datetime.utcnow)
    
    assignment = relationship("Assignment", back_populates="submissions")
    student = relationship("Student", back_populates="submissions")