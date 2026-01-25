import sqlite3

# ຊື່ໄຟລ໌ Database ຂອງທ່ານ
DB_NAME = 'student_tracking.db'

def fix_database():
    print(f"🔄 Connecting to {DB_NAME}...")
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    try:
        # ==========================================
        # 1. ແກ້ໄຂຕາຕະລາງ ATTENDANCE (ເພີ່ມ period, remark)
        # ==========================================
        print("Checking 'attendance' table...")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='attendance'")
        if cursor.fetchone():
            cursor.execute("PRAGMA table_info(attendance)")
            columns_att = [info[1] for info in cursor.fetchall()]

            # ເພີ່ມ column 'period'
            if 'period' not in columns_att:
                print("  ➕ Adding 'period' column to attendance...")
                cursor.execute("ALTER TABLE attendance ADD COLUMN period TEXT DEFAULT 'DAILY'")
            else:
                print("  ✅ 'period' column already exists.")

            # ເພີ່ມ column 'remark'
            if 'remark' not in columns_att:
                print("  ➕ Adding 'remark' column to attendance...")
                cursor.execute("ALTER TABLE attendance ADD COLUMN remark TEXT")
            else:
                print("  ✅ 'remark' column already exists.")
        else:
             print("  ⚠️ Table 'attendance' not found!")


        # ==========================================
        # 2. ແກ້ໄຂຕາຕະລາງ GRADES (ເພີ່ມ subject_name)
        # ==========================================
        print("\nChecking 'grades' table...")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='grades'")
        if cursor.fetchone():
            cursor.execute("PRAGMA table_info(grades)")
            columns_grades = [info[1] for info in cursor.fetchall()]

            # ເພີ່ມ column 'subject_name'
            if 'subject_name' not in columns_grades:
                print("  ➕ Adding 'subject_name' column to grades...")
                cursor.execute("ALTER TABLE grades ADD COLUMN subject_name TEXT DEFAULT 'GENERAL'")
            else:
                print("  ✅ 'subject_name' column already exists.")
        else:
            print("  ⚠️ Table 'grades' not found! (Please run the server to create tables first)")


        # ==========================================
        # 3. ແກ້ໄຂຕາຕະລາງ CLASSES (ເພີ່ມ is_grade_locked) ✅ NEW
        # ==========================================
        print("\nChecking 'classes' table...")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='classes'")
        if cursor.fetchone():
            cursor.execute("PRAGMA table_info(classes)")
            columns_classes = [info[1] for info in cursor.fetchall()]

            # ເພີ່ມ column 'is_grade_locked'
            if 'is_grade_locked' not in columns_classes:
                print("  ➕ Adding 'is_grade_locked' column to classes...")
                # SQLite ໃຊ້ 0/1 ແທນ Boolean (0=False, 1=True)
                cursor.execute("ALTER TABLE classes ADD COLUMN is_grade_locked BOOLEAN DEFAULT 0") 
            else:
                print("  ✅ 'is_grade_locked' column already exists.")
        else:
            print("  ⚠️ Table 'classes' not found!")


        # ==========================================
        # 4. Commit Changes
        # ==========================================
        conn.commit()
        print("\n🎉 Database updated successfully!")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        conn.rollback()

    finally:
        conn.close()

if __name__ == "__main__":
    fix_database()