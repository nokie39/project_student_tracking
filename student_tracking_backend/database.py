from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import urllib.parse
import os

# =========================================================
# ຕັ້ງຄ່າ Database Connection (Hybrid: Local + Cloud Run)
# =========================================================

# 1. ດຶງຂໍ້ມູນຈາກ Environment Variables
DB_USER = os.environ.get("DB_USER", "postgres")
DB_PASS = os.environ.get("DB_PASS", "NnoK@133994") # <--- ໃສ່ລະຫັດຜ່ານແທ້ຂອງທ່ານບ່ອນນີ້ສຳລັບ Local
DB_NAME = os.environ.get("DB_NAME", "student_tracking")

# ສຳລັບ Local (IP Address)
DB_HOST = os.environ.get("DB_HOST", "136.112.171.66") # IP ຂອງ Cloud SQL ຂອງທ່ານ
DB_PORT = os.environ.get("DB_PORT", "5432")

# ສຳລັບ Cloud Run (Connection Name)
# ຖ້າມີຄ່ານີ້ ສະແດງວ່າ Run ຢູ່ເທິງ Cloud
INSTANCE_CONNECTION_NAME = os.environ.get("INSTANCE_CONNECTION_NAME")

encoded_password = urllib.parse.quote_plus(DB_PASS)

# 2. Logic ເລືອກ Connection String (ຫົວໃຈສຳຄັນ ❤️)
if INSTANCE_CONNECTION_NAME:
    # ✅ ກໍລະນີຢູ່ Cloud Run: ໃຊ້ Unix Socket (ບໍ່ໃຊ້ IP)
    socket_path = f"/cloudsql/{INSTANCE_CONNECTION_NAME}"
    SQLALCHEMY_DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{encoded_password}@/{DB_NAME}?host={socket_path}"
    print("Connecting via Unix Socket...") # Log ບອກວ່າໃຊ້ Socket
else:
    # ✅ ກໍລະນີຢູ່ Local: ໃຊ້ TCP/IP
    SQLALCHEMY_DATABASE_URL = f"postgresql://{DB_USER}:{encoded_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    print("Connecting via TCP/IP...") # Log ບອກວ່າໃຊ້ IP

# ສ້າງ Engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()