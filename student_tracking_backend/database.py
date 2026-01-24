from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# ໃຊ້ SQLite ສຳລັບ Dev (ຖ້າຂຶ້ນ Production ຄ່ອຍປ່ຽນເປັນ PostgreSQL)
SQLALCHEMY_DATABASE_URL = "sqlite:///./student_tracking.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency ເພື່ອເອົາ DB Session ໄປໃຊ້ໃນ API
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()