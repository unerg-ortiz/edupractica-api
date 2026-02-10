import sqlite3

def migrate():
    conn = sqlite3.connect('sql_app.db')
    cursor = conn.cursor()
    
    # Check current columns
    cursor.execute('PRAGMA table_info(users)')
    columns = [row[1] for row in cursor.fetchall()]
    
    try:
        if 'oauth_provider' not in columns:
            print("Adding oauth_provider column...")
            cursor.execute('ALTER TABLE users ADD COLUMN oauth_provider VARCHAR')
        
        if 'oauth_id' not in columns:
            print("Adding oauth_id column...")
            cursor.execute('ALTER TABLE users ADD COLUMN oauth_id VARCHAR')
            
        # Note: Changing NOT NULL to NULL in SQLite is complex (requires recreating table)
        # However, existing users already have a password, so they won't violate NOT NULL.
        # New users without it will fail until the table is recreated.
        # For now, let's just add the columns. 
        # If the user wants full support for NULL passwords, we should recreate.
        
        conn.commit()
        print("Migration successful!")
    except Exception as e:
        print(f"Error during migration: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
