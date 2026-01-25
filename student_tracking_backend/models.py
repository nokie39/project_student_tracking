from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Float, DateTime, Text, Table
from sqlalchemy.orm import relationship
from database import Base
from sqlalchemy.sql import func
from datetime import datetime

# ==========================================
# 0. ASSOCIATION TABLES (Many-to-Many)
# ==========================================

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
    student_profile = relationship("Student", back_populates="user", uselist=False)
    children = relationship(
        "Student",
        secondary=parent_student_link,
        back_populates="parents"
    )
    
    classes_teaching = relationship("Class", back_populates="teacher")
    teachers_supervised = relationship("TeacherSupervision", foreign_keys="TeacherSupervision.head_teacher_id", back_populates="head_teacher")
    supervisor_record = relationship("TeacherSupervision", foreign_keys="TeacherSupervision.teacher_id", back_populates="teacher")


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
    name = Column(String)
    is_active = Column(Boolean, default=False)

    classes = relationship("Class", back_populates="academic_year")

class Class(Base):
    __tablename__ = "classes"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    teacher_id = Column(Integer, ForeignKey("users.id"))
    year_id = Column(Integer, ForeignKey("academic_years.id"))
    
    is_grade_locked = Column(Boolean, default=False)
    
    teacher = relationship("User", back_populates="classes_teaching")
    academic_year = relationship("AcademicYear", back_populates="classes")
    enrollments = relationship("Enrollment", back_populates="classroom")
    schedules = relationship("Schedule", back_populates="classroom")
    assignments = relationship("Assignment", back_populates="classroom")
    grades = relationship("Grade", back_populates="classroom")

# ==========================================
# 3. STUDENTS & ENROLLMENT
# ==========================================
class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True, index=True)
    student_code = Column(String, unique=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    full_name = Column(String)
    date_of_birth = Column(String, nullable=True)

    # --- ຂໍ້ມູນຄອບຄົວ ---    
    parent_name = Column(String, nullable=True)
    parent_phone = Column(String, nullable=True)
    parent_email = Column(String, nullable=True)
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
    
    user = relationship("User", back_populates="student_profile")
    parents = relationship(
        "User",
        secondary=parent_student_link,
        back_populates="children"
    )

    enrollments = relationship("Enrollment", back_populates="student")
    grades = relationship("Grade", back_populates="student")
    behavior_logs = relationship("BehaviorLog", back_populates="student")
    
    # ✅ (1) ທີ່ Class Student ຕັ້ງຊື່ວ່າ "submissions"
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
# 4. GRADES
# ==========================================
class Grade(Base):
    __tablename__ = "grades"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    class_id = Column(Integer, ForeignKey("classes.id"))
    month_id = Column(Integer)
    subject_name = Column(String, default="GENERAL")
    attendance_score = Column(Float, default=0)
    homework_score = Column(Float, default=0)
    midterm_score = Column(Float, default=0)
    final_score = Column(Float, default=0)
    total_score = Column(Float, default=0)

    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    student = relationship("Student", back_populates="grades")
    classroom = relationship("Class", back_populates="grades")
    audit_logs = relationship("GradeAuditLog", back_populates="grade")

class GradeAuditLog(Base):
    __tablename__ = "grade_audit_logs"
    id = Column(Integer, primary_key=True, index=True)
    grade_id = Column(Integer, ForeignKey("grades.id"))
    old_score = Column(Float)
    new_score = Column(Float)
    updated_by = Column(Integer, ForeignKey("users.id"))
    reason = Column(Text)
    updated_at = Column(DateTime, default=datetime.utcnow)
    
    grade = relationship("Grade", back_populates="audit_logs")

# ==========================================
# 5. BEHAVIOR
# ==========================================
class BehaviorLog(Base):
    __tablename__ = "behavior_logs"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    teacher_id = Column(Integer, ForeignKey("users.id"))
    
    type = Column(String)
    title = Column(String)
    description = Column(Text, nullable=True)
    points = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    student = relationship("Student", back_populates="behavior_logs")

# ==========================================
# 6. SCHEDULES & ATTENDANCE
# ==========================================
class Schedule(Base):
    __tablename__ = "schedules"
    id = Column(Integer, primary_key=True, index=True)
    class_id = Column(Integer, ForeignKey("classes.id"))
    semester_id = Column(Integer, default=1)
    
    subject_name = Column(String)
    teacher_name = Column(String, nullable=True)
    day_of_week = Column(String)
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
    date = Column(String)
    status = Column(String)
    period = Column(String, default="DAILY") 
    remark = Column(String, nullable=True)

# ==========================================
# 7. TEACHER SUPERVISION
# ==========================================
class TeacherSupervision(Base):
    __tablename__ = "teacher_supervision"
    id = Column(Integer, primary_key=True, index=True)
    head_teacher_id = Column(Integer, ForeignKey("users.id"))
    teacher_id = Column(Integer, ForeignKey("users.id"))
    
    head_teacher = relationship("User", foreign_keys=[head_teacher_id], back_populates="teachers_supervised")
    teacher = relationship("User", foreign_keys=[teacher_id], back_populates="supervisor_record")

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
    
    # ✅ (2) ແກ້ໄຂ back_populates ໃຫ້ເປັນ "submissions" (ໃຫ້ກົງກັບທີ່ປະກາດໃນ class Student)
    student = relationship("Student", back_populates="submissions")