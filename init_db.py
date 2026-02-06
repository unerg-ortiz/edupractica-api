from sqlalchemy.orm import Session
from app.db.session import SessionLocal, engine
from app.db.base import Base
from app.core.security import get_password_hash
from app.models.user import User
# Ensure models are imported for metadata
from app.models import user, audit

Base.metadata.create_all(bind=engine)

def init_db(db: Session) -> None:
    user = db.query(User).filter(User.email == "admin@example.com").first()
    if not user:
        user = User(
            email="admin@example.com",
            hashed_password=get_password_hash("admin123"),
            full_name="Admin User",
            is_superuser=True,
            is_active=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        print("Admin user created")
    else:
        print("Admin user already exists")

if __name__ == "__main__":
    db = SessionLocal()
    init_db(db)
