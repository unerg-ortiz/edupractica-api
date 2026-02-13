import sqlite3
from datetime import datetime

def migrate():
    conn = sqlite3.connect('sql_app.db')
    cursor = conn.cursor()
    
    # Get current columns
    cursor.execute("PRAGMA table_info(stages);")
    existing_cols = [col[1] for col in cursor.fetchall()]
    
    if "submitted_at" not in existing_cols:
        try:
            # Add without default first
            cursor.execute("ALTER TABLE stages ADD COLUMN submitted_at TIMESTAMP")
            print("✅ Added column: submitted_at")
            
            # Set a default value for existing records
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute(f"UPDATE stages SET submitted_at = '{now}'")
            print(f"✅ Updated existing records with submitted_at = {now}")
        except Exception as e:
            print(f"❌ Error adding submitted_at: {e}")
    else:
        print("ℹ️ Column submitted_at already exists.")
            
    conn.commit()
    conn.close()
    print("🚀 Fix migration finished.")

if __name__ == "__main__":
    migrate()
