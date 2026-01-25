from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
import database, models, auth

router = APIRouter(
    prefix="/reports",
    tags=["Reports"]
)

# ==========================================
# 1. ບົດສະຫຼຸບປະຈຳພາກ (Semester Summary)
# ==========================================

def get_semester_months(semester_id: int):
    if semester_id == 1:
        return [9, 10, 11, 12, 1] 
    elif semester_id == 2:
        return [2, 3, 4, 5, 6]    
    return []

@router.get("/semester-summary/{class_id}/{semester_id}")
def get_semester_summary(
    class_id: int,
    semester_id: int,
    db: Session = Depends(database.get_db),
    current_user: dict = Depends(auth.get_current_user)
):
    target_months = get_semester_months(semester_id)
    
    students = db.query(models.Student).join(models.Enrollment).filter(
        models.Enrollment.class_id == class_id
    ).all()
    
    report_data = []
    
    for stu in students:
        grades = db.query(models.Grade).filter(
            models.Grade.student_id == stu.id,
            models.Grade.class_id == class_id,
            models.Grade.month_id.in_(target_months)
        ).all()
        
        subjects_data = {}
        
        for g in grades:
            subj = g.subject_name
            if subj not in subjects_data:
                subjects_data[subj] = {
                    "monthly_scores": [], 
                    "midterm_max": 0,     
                    "final_max": 0
                }
            
            monthly_total = (g.attendance_score or 0) + (g.homework_score or 0)
            if monthly_total > 0:
                subjects_data[subj]["monthly_scores"].append(monthly_total)
            
            if (g.midterm_score or 0) > subjects_data[subj]["midterm_max"]:
                subjects_data[subj]["midterm_max"] = g.midterm_score
                
            if (g.final_score or 0) > subjects_data[subj]["final_max"]:
                subjects_data[subj]["final_max"] = g.final_score
            
        final_subjects = []
        for subj, data in subjects_data.items():
            avg_regular = 0
            count = len(data["monthly_scores"])
            if count > 0:
                avg_regular = sum(data["monthly_scores"]) / count
            
            semester_total = avg_regular + data["midterm_max"] + data["final_max"]
            
            grade_char = "F"
            if semester_total >= 80: grade_char = "A"
            elif semester_total >= 75: grade_char = "B+"
            elif semester_total >= 70: grade_char = "B"
            elif semester_total >= 65: grade_char = "C+"
            elif semester_total >= 60: grade_char = "C"
            elif semester_total >= 55: grade_char = "D+"
            elif semester_total >= 50: grade_char = "D"

            final_subjects.append({
                "subject": subj,
                "avg_regular": round(avg_regular, 2),
                "midterm": data["midterm_max"],
                "final": data["final_max"],
                "total": round(semester_total, 2),
                "grade": grade_char
            })
            
        report_data.append({
            "student_id": stu.id,
            "full_name": stu.full_name,
            "student_code": stu.student_code,
            "subjects": final_subjects
        })
        
    return report_data


# ==========================================
# 2. ປະຫວັດການຮຽນລະອຽດ (Detailed History)
# ==========================================

def get_month_name(month_id: int):
    months = {
        9: "ກັນຍາ (Sep)", 10: "ຕຸລາ (Oct)", 11: "ພະຈິກ (Nov)", 12: "ທັນວາ (Dec)",
        1: "ມັງກອນ (Jan)", 2: "ກຸມພາ (Feb)", 3: "ມີນາ (Mar)", 4: "ເມສາ (Apr)",
        5: "ພຶດສະພາ (May)", 6: "ມິຖຸນາ (Jun)", 7: "ກໍລະກົດ (Jul)", 8: "ສິງຫາ (Aug)"
    }
    return months.get(month_id, str(month_id))

@router.get("/student-detail-history/{student_id}")
def get_student_detail_history(
    student_id: int,
    db: Session = Depends(database.get_db),
    current_user: dict = Depends(auth.get_current_user)
):
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not student:
        return {"error": "Student not found"}

    grades = db.query(models.Grade)\
        .join(models.Class).join(models.AcademicYear)\
        .filter(models.Grade.student_id == student_id)\
        .order_by(models.AcademicYear.name.desc(), models.Grade.month_id.asc())\
        .all()

    history = {}

    for g in grades:
        year_name = g.classroom.academic_year.name
        class_name = g.classroom.name
        year_key = f"{year_name} ({class_name})" 
        
        if year_key not in history:
            history[year_key] = {}
            
        m_id = g.month_id
        if m_id not in history[year_key]:
            history[year_key][m_id] = []
            
        history[year_key][m_id].append({
            "subject": g.subject_name,
            "attendance": g.attendance_score,
            "homework": g.homework_score,
            "midterm": g.midterm_score,
            "final": g.final_score,
            "total": g.total_score
        })

    final_report = []
    
    for year_info, months_data in history.items():
        months_list = []
        # Sort ເດືອນ: 9, 10, 11, 12, 1, 2...
        sorted_month_ids = sorted(months_data.keys(), key=lambda x: x if x >= 9 else x + 12)
        
        for m_id in sorted_month_ids:
            months_list.append({
                "month_id": m_id,
                "month_name": get_month_name(m_id),
                "subjects": months_data[m_id]
            })
            
        final_report.append({
            "year_info": year_info,
            "months": months_list
        })

    return {
        "student": {
            "full_name": student.full_name,
            "code": student.student_code
        },
        "history": final_report
    }


# ==========================================
# 3. ໃບຢັ້ງຢືນຜົນການຮຽນ (Transcript) - ⚠️ ຕ້ອງມີສ່ວນນີ້!
# ==========================================

@router.get("/student-transcript/{student_id}")
def get_student_transcript(
    student_id: int,
    db: Session = Depends(database.get_db),
    current_user: dict = Depends(auth.get_current_user)
):
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not student:
        return {"error": "Student not found"}

    enrollments = db.query(models.Enrollment).join(models.Class).join(models.AcademicYear)\
        .filter(models.Enrollment.student_id == student_id)\
        .order_by(models.AcademicYear.name.asc())\
        .all()

    transcript_data = []

    for enroll in enrollments:
        cls = enroll.classroom
        year = cls.academic_year
        
        grades = db.query(models.Grade).filter(
            models.Grade.student_id == student_id,
            models.Grade.class_id == cls.id
        ).all()

        subjects_data = {}
        for g in grades:
            subj = g.subject_name
            if subj not in subjects_data:
                subjects_data[subj] = {"total_sum": 0, "count": 0}
            
            score = (g.attendance_score or 0) + (g.homework_score or 0) + (g.midterm_score or 0) + (g.final_score or 0)
            
            if score > 0:
                subjects_data[subj]["total_sum"] += score
                subjects_data[subj]["count"] += 1

        final_subjects = []
        year_total_score = 0
        subject_count = 0

        for subj, data in subjects_data.items():
            avg_score = 0
            if data["count"] > 0:
                avg_score = data["total_sum"] / data["count"]

            grade_char = "F"
            if avg_score >= 80: grade_char = "A"
            elif avg_score >= 70: grade_char = "B"
            elif avg_score >= 60: grade_char = "C"
            elif avg_score >= 50: grade_char = "D"

            final_subjects.append({
                "subject": subj,
                "score": round(avg_score, 2),
                "grade": grade_char
            })
            
            year_total_score += avg_score
            subject_count += 1

        gpa = 0
        if subject_count > 0:
            gpa = year_total_score / subject_count

        transcript_data.append({
            "year_name": year.name,
            "class_name": cls.name,
            "subjects": final_subjects,
            "gpa": round(gpa, 2)
        })

    return {
        "student_info": {
            "full_name": student.full_name,
            "student_code": student.student_code,
            "dob": student.date_of_birth
        },
        "academic_history": transcript_data
    }