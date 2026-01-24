from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware # <--- ຢ່າລືມ Import
import models
from database import engine
from routers import users, academic, students, grades, schedules, attendance, lms, reports, behavior, head, enrollments, parents


# ສ້າງ Database
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# ==========================================
# ⚠️ ສ່ວນສຳຄັນ: CORS ຕ້ອງຢູ່ບ່ອນນີ້ (ກ່ອນ Routers)
# ==========================================
app.add_middleware(
    CORSMiddleware,
    # ອະນຸຍາດໃຫ້ Frontend ເຂົ້າເຖິງໄດ້ (ໃສ່ * ຄືໃຫ້ທຸກເວັບ, ຫຼືໃສ່ http://localhost:5173)
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