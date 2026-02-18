import sqlite3

def check_schema():
    conn = sqlite3.connect('sql_app.db')
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(stages);")
    columns = cursor.fetchall()
    print("Columns in 'stages' table:")
    for col in columns:
        print(col)
    conn.close()

if __name__ == "__main__":
    check_schema()
