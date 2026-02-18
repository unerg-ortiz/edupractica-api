import sqlite3

def migrate():
    conn = sqlite3.connect('sql_app.db')
    cursor = conn.cursor()
    
    # Get current columns
    cursor.execute("PRAGMA table_info(stages);")
    existing_cols = [col[1] for col in cursor.fetchall()]
    
    target_columns = [
        ("professor_id", "INTEGER"),
        ("approval_status", "VARCHAR(20) DEFAULT 'approved'"),
        ("approval_comment", "TEXT"),
        ("submitted_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
    ]
    
    for col_name, col_type in target_columns:
        if col_name not in existing_cols:
            try:
                cursor.execute(f"ALTER TABLE stages ADD COLUMN {col_name} {col_type}")
                print(f"✅ Added column: {col_name}")
            except Exception as e:
                print(f"❌ Error adding {col_name}: {e}")
        else:
            print(f"ℹ️ Column already exists: {col_name}")
            
    # Ensure existing stages are approved
    cursor.execute("UPDATE stages SET approval_status = 'approved' WHERE approval_status IS NULL")
    
    conn.commit()
    conn.close()
    print("🚀 Migration finished.")

if __name__ == "__main__":
    migrate()
