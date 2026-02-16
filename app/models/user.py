from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import relationship
from app.db.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, index=True)
    role = Column(String, index=True, default="student") # roles: student, professor, admin
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    is_professor = Column(Boolean, default=False)
    
    # Blocking fields
    is_blocked = Column(Boolean, default=False)
    block_reason = Column(String, nullable=True)

    # Relationships
    attempts = relationship("StudentAttempt", back_populates="user", cascade="all, delete-orphan")
    stage_progress = relationship("UserStageProgress", back_populates="user", cascade="all, delete-orphan")
