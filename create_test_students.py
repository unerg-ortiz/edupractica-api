from app.db.session import SessionLocal
from app.crud import user
from app.schemas.user import UserCreate

def create_students():
    db = SessionLocal()
    students_data = [
        {"email": "student1@example.com", "password": "password123", "full_name": "Student One"},
        {"email": "student2@example.com", "password": "password123", "full_name": "Student Two"},
        {"email": "student3@example.com", "password": "password123", "full_name": "Student Three"},
        {"email": "student4@example.com", "password": "password123", "full_name": "Student Four"},
    ]
    
    for s_data in students_data:
        db_user = user.get_by_email(db, email=s_data["email"])
        if not db_user:
            user_in = UserCreate(**s_data)
            user.create(db, obj_in=user_in)
            print(f"Created student: {s_data['email']}")
    db.close()

if __name__ == "__main__":
    create_students()
