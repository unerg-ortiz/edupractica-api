"""
Migration script to add 'role' column to users table.
Run this once: python migrate_add_role.py
"""
import sqlite3

DB_PATH = "sql_app.db"

def migrate():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check existing columns
    cursor.execute("PRAGMA table_info(users)")
    columns = [col[1] for col in cursor.fetchall()]
    print(f"Current columns: {columns}")
    
    if "role" not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'student'")
        # Set admin role for superusers
        cursor.execute("UPDATE users SET role = 'admin' WHERE is_superuser = 1")
        conn.commit()
        print("✅ Column 'role' added and superusers set as admin.")
    else:
        print("✅ Column 'role' already exists.")
    
    # Show updated users
    cursor.execute("SELECT id, email, role, is_superuser FROM users")
    for row in cursor.fetchall():
        print(f"  User: id={row[0]}, email={row[1]}, role={row[2]}, is_superuser={row[3]}")
    
    conn.close()

if __name__ == "__main__":
    migrate()
