import sqlite3
import os

db_path = "sql_app.db"

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("Updating database schema...")
    
    # Add columns to users
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN is_professor BOOLEAN DEFAULT 0")
        print("Added is_professor to users")
    except sqlite3.OperationalError as e:
        print(f"users table: {e}")

    # Add columns to stages
    try:
        cursor.execute("ALTER TABLE stages ADD COLUMN is_archived BOOLEAN DEFAULT 0")
        print("Added is_archived to stages")
    except sqlite3.OperationalError as e:
        print(f"stages table: {e}")

    try:
        cursor.execute("ALTER TABLE stages ADD COLUMN professor_id INTEGER REFERENCES users(id)")
        print("Added professor_id to stages")
    except sqlite3.OperationalError as e:
        print(f"stages table: {e}")
        
    conn.commit()
    conn.close()
    print("Database columns updated.")
else:
    print("Database file not found. Running the app will create it from scratch.")

# Also run create_all to create new tables
from app.db.base import Base
from app.db.session import engine
# Import all models to ensure they are registered
from app.models import user, category, stage, feedback, audit, transfer

print("Creating new tables if they don't exist...")
Base.metadata.create_all(bind=engine)
print("Finished.")
