import sqlite3

DB_NAME = 'secure_delivery.db'

def run_migration():
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        # إضافة عمود status مع قيمة افتراضية للطلبات السابقة
        cursor.execute("ALTER TABLE orders ADD COLUMN status TEXT DEFAULT 'pending';")
        conn.commit()
        print(f"✅ Success: 'status' column added to {DB_NAME}")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print("⚠️ The column 'status' already exists.")
        else:
            print(f"❌ Error: {e}")
    finally:
        if 'conn' in locals() and conn:
            conn.close()

if __name__ == '__main__':
    run_migration()
