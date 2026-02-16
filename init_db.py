from sqlalchemy.orm import Session
from app.db.session import SessionLocal, engine
from app.db.base import Base
from app.core.security import get_password_hash
from app.models.user import User
# Ensure models are imported for metadata
from app.models import user, audit, category, stage, feedback, transfer

Base.metadata.create_all(bind=engine)

def init_db(db: Session) -> None:
    user = db.query(User).filter(User.email == "admin@example.com").first()
    if not user:
        user = User(
            email="admin@example.com",
            hashed_password=get_password_hash("admin123"),
            full_name="Admin User",
            is_superuser=True,
            is_professor=True,
            is_active=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        print("Admin user created")
    else:
        # Update existing admin to be professor too
        user.is_professor = True
        db.add(user)
        db.commit()
        print("Admin user updated to be professor")

    # Create a Test Professor
    prof = db.query(User).filter(User.email == "profe@example.com").first()
    if not prof:
        prof = User(
            email="profe@example.com",
            hashed_password=get_password_hash("profe123"),
            full_name="Profesor de Prueba",
            is_superuser=False,
            is_professor=True,
            is_active=True,
        )
        db.add(prof)
        db.commit()
        print("Test professor created")

if __name__ == "__main__":
    db = SessionLocal()
    init_db(db)
