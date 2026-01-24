from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime, time, date

# ===========================
# 🔐 AUTH & USERS SCHEMAS
# ===========================

class LoginRequest(BaseModel):
    email: EmailStr

class VerifyOTPRequest(BaseModel):
    email: EmailStr
    otp_code: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    role: str

class UserCreate(BaseModel):
    email: EmailStr
    full_name: str
    role: str  # 'admin', 'teacher', 'head_teacher'
    student_ids: Optional[List[int]] = [] # ຮັບ ID ນັກຮຽນຫຼາຍຄົນໄດ້

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None
    student_ids: Optional[List[int]] = []

class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    role: str
    is_active: bool = True 
    class Config:
        from_attributes = True

# --- Admin Linking ---
class AssignTeacherRequest(BaseModel):
    head_teacher_id: int
    teacher_id: int

class AssignParentRequest(BaseModel):
    parent_email: str
    student_code: str


# ===========================
# 📅 ACADEMIC & CLASS
# ===========================

class AcademicYearCreate(BaseModel):
    name: str
    is_active: bool = False 

class AcademicYearResponse(BaseModel):
    id: int
    name: str
    is_active: bool
    class Config:
        from_attributes = True

class ClassCreate(BaseModel):
    name: str
    teacher_id: int
    year_id: int

class ClassResponse(BaseModel):
    id: int
    name: str
    teacher_id: int
    year_id: int
    class Config:
        from_attributes = True


# ===========================
# 🎓 STUDENTS & ENROLLMENT
# ===========================

class StudentRegister(BaseModel):
    email: EmailStr
    full_name: str
    student_code: str
    date_of_birth: str
    parent_name: Optional[str] = None
    parent_phone: Optional[str] = None
    parent_email: Optional[str] = None
    blood_type: Optional[str] = None
    allergies: Optional[str] = None
    address: Optional[str] = None
    village: Optional[str] = None
    district: Optional[str] = None
    province: Optional[str] = None
    talents: Optional[str] = None
    health_info: Optional[str] = None

class StudentUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    student_code: Optional[str] = None
    date_of_birth: Optional[str] = None
    parent_name: Optional[str] = None
    parent_phone: Optional[str] = None
    parent_email: Optional[str] = None 
    blood_type: Optional[str] = None
    allergies: Optional[str] = None
    province: Optional[str] = None
    district: Optional[str] = None
    village: Optional[str] = None
    talents: Optional[str] = None
    health_info: Optional[str] = None

class StudentResponse(BaseModel):
    id: int
    student_code: str
    full_name: str
    class Config:
        from_attributes = True

class EnrollmentCreate(BaseModel):
    student_id: int
    class_id: int

class EnrollmentResponse(BaseModel):
    student_id: int
    class_id: int
    student_name: str
    class Config:
        from_attributes = True


# ===========================
# 📝 GRADES & BEHAVIOR
# ===========================

class GradeUpdate(BaseModel):
    student_id: int
    class_id: int
    month_id: int
    score_type: str  # "ATTENDANCE", "HOMEWORK", "MIDTERM", "FINAL"
    score_value: float
    reason: Optional[str] = None

class GradeLogResponse(BaseModel):
    id: int
    old_score: float
    new_score: float
    updated_by: int
    updated_by_name: str = "Unknown"
    reason: Optional[str]
    updated_at: datetime
    class Config:
        from_attributes = True

class BehaviorLogCreate(BaseModel):
    student_id: int
    type: str  # "POSITIVE" ຫຼື "NEGATIVE"
    title: str
    description: Optional[str] = None
    points: int

class BehaviorLogResponse(BaseModel):
    id: int
    student_id: int
    teacher_id: int
    type: str
    title: str
    description: Optional[str]
    points: int
    created_at: datetime
    class Config:
        from_attributes = True

class TalentUpdate(BaseModel):
    talents: str 


# ===========================
# 🏫 SCHEDULES & ATTENDANCE
# ===========================

class ScheduleCreate(BaseModel):
    class_id: int
    subject_name: str
    teacher_name: Optional[str] = None
    day_of_week: str
    start_time: str # ຮັບເປັນ String "HH:MM"
    end_time: str   # ຮັບເປັນ String "HH:MM"
    room: Optional[str] = None
    note: Optional[str] = None

class ScheduleResponse(BaseModel):
    id: int
    subject_name: str
    teacher_name: Optional[str] = None
    day_of_week: str
    start_time: str 
    end_time: str   
    room: Optional[str] = None
    note: Optional[str] = None
    class Config:
        from_attributes = True

# 🔥🔥 UPDATED ATTENDANCE SCHEMAS 🔥🔥
class AttendanceItem(BaseModel):
    student_id: int
    status: str  # PRESENT, ABSENT, LATE, PERMISSION
    remark: Optional[str] = None

class AttendanceBatchRequest(BaseModel):
    class_id: int
    date: date # ຮັບເປັນ YYYY-MM-DD
    students: List[AttendanceItem]

class AttendanceLogView(BaseModel):
    student_id: int
    student_code: str
    full_name: str
    status: str = "PRESENT" # Default ໃຫ້ເປັນ "ມາ"
    remark: Optional[str] = None
    

class AttendanceResponse(BaseModel):
    id: int
    student_id: int
    class_id: int
    date: date
    status: str
    remark: Optional[str] = None
    class Config:
        from_attributes = True

class TeacherWorkStatus(BaseModel):
    teacher_id: int
    full_name: str
    email: str
    class_name: str
    attendance_done: bool 
    grade_progress: float 
    class Config:
        from_attributes = True

# ===========================
# 📚 LMS & ASSIGNMENTS
# ===========================

class AssignmentCreate(BaseModel):
    title: str
    description: Optional[str] = None
    file_url: Optional[str] = None
    due_date: datetime
    class_id: int

class AssignmentResponse(AssignmentCreate):
    id: int
    created_at: datetime
    class_name: Optional[str] = None 

    class Config:
        from_attributes = True

class SubmissionGrade(BaseModel):
    submission_id: Optional[int] = None
    score: float
    feedback: Optional[str] = None
        
class SubmissionResponse(BaseModel):
    id: int
    score: Optional[float] = None
    feedback: Optional[str] = None
    file_url: str
    submitted_at: datetime
    class Config:
        from_attributes = True

class StudentAssignmentResponse(AssignmentResponse):
    submission: Optional[SubmissionResponse] = None

# ===========================
# 👨‍👩‍👧‍👦 PARENTS & CHILDREN
# ===========================

class ChildSummary(BaseModel):
    id: int
    name: str
    student_code: str
    class_name: str = "N/A"
    photo_url: Optional[str] = None 

# ===========================
# 📊 REPORTS
# ===========================

class StudentFullReport(BaseModel):
    id: int
    student_code: str
    full_name: str
    email: Optional[str] = None
    parent_email: Optional[str] = None
    parent_name: Optional[str] = None
    parent_phone: Optional[str] = None
    blood_type: Optional[str] = None
    talents: Optional[str] = None
    address_summary: Optional[str] = None
    total_merit_points: int
    behavior_logs: List[BehaviorLogResponse] = []
    class_name: Optional[str] = "N/A"
    academic_year: Optional[str] = "N/A"
    class Config:
        from_attributes = True