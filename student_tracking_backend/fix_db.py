# fix_db.py
import sqlite3

# ເຊື່ອມຕໍ່ກັບຖານຂໍ້ມູນ
conn = sqlite3.connect('student_tracking.db')
cursor = conn.cursor()

try:
    print("Checking database schema...")
    
    # ດຶງລາຍຊື່ column ປະຈຸບັນ
    cursor.execute("PRAGMA table_info(attendance)")
    columns = [info[1] for info in cursor.fetchall()]
    
    # 1. ເພີ່ມ column 'period' ຖ້າຍັງບໍ່ມີ
    if 'period' not in columns:
        print("Adding 'period' column...")
        cursor.execute("ALTER TABLE attendance ADD COLUMN period TEXT DEFAULT 'DAILY'")
    else:
        print("'period' column already exists.")

    # 2. ເພີ່ມ column 'remark' ຖ້າຍັງບໍ່ມີ
    if 'remark' not in columns:
        print("Adding 'remark' column...")
        cursor.execute("ALTER TABLE attendance ADD COLUMN remark TEXT")
    else:
        print("'remark' column already exists.")

    conn.commit()
    print("✅ Database updated successfully!")

except Exception as e:
    print(f"❌ Error: {e}")

finally:
    conn.close()