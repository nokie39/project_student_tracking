from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
import models
from database import engine, get_db
from routers import users, academic, students, grades, schedules, attendance, lms, reports, behavior, head, enrollments, parents


# ສ້າງ Database (ຖ້າຍັງບໍ່ມີ Table)
models.Base.metadata.create_all(bind=engine)


app = FastAPI()

# ==========================================
# ⚠️ ສ່ວນສຳຄັນ: CORS ຕ້ອງຢູ່ບ່ອນນີ້ (ກ່ອນ Routers)
# ==========================================
app.add_middleware(
    CORSMiddleware,
    # ອະນຸຍາດໃຫ້ Frontend ເຂົ້າເຖິງໄດ້ (ໃສ່ * ຄືໃຫ້ທຸກເວັບ)
    allow_origins=["*"], 
    allow_credentials=True,
    # ອະນຸຍາດທຸກ Method (GET, POST, PUT, DELETE, OPTIONS)
    allow_methods=["*"], 
    allow_headers=["*"],
)
# ==========================================

# ໂຫຼດ API Routers
app.include_router(users.router)
app.include_router(academic.router)
app.include_router(students.router)
app.include_router(grades.router)
app.include_router(schedules.router)
app.include_router(attendance.router)
app.include_router(lms.router)
app.include_router(reports.router)
app.include_router(head.router)
app.include_router(behavior.router)
app.include_router(enrollments.router)
app.include_router(parents.router)

# Mount Static Files (ສຳລັບຮູບພາບ/ໄຟລ໌)
from fastapi.staticfiles import StaticFiles
import os

# ສ້າງ folder ຖ້າຍັງບໍ່ມີ
if not os.path.exists("static/uploads"):
    os.makedirs("static/uploads")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def root():
    return {"message": "Student Tracking API is Running!"}

# ==========================================
# ✅ ROUTE ພິເສດ: ແກ້ໄຂ Database (ເພີ່ມຖັນ period)
# ==========================================
@app.get("/fix-database-schema")
def fix_database_schema(db: Session = Depends(get_db)):
    try:
        # ສັ່ງ SQL ເພື່ອເພີ່ມຖັນ period ເຂົ້າໄປໃນຕາຕະລາງ attendance
        sql = text("ALTER TABLE attendance ADD COLUMN period VARCHAR DEFAULT 'DAILY';")
        db.execute(sql)
        db.commit()
        return {"message": "✅ ອັບເດດ Database ສຳເລັດແລ້ວ! (Added 'period' column successfully)"}
    except Exception as e:
        # ຖ້າມີຖັນນີ້ຢູ່ແລ້ວ ຫຼື ມີບັນຫາອື່ນໆ ມັນຈະແຈ້ງເຕືອນ
        return {"message": f"⚠️ ແຈ້ງເຕືອນ (ອາດຈະມີຖັນນີ້ຢູ່ແລ້ວ): {str(e)}"}