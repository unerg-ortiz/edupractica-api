from sqlalchemy import Boolean, Column, Integer, String
from app.db.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=True)
    full_name = Column(String, index=True)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    
    # OAuth fields
    oauth_provider = Column(String, nullable=True)
    oauth_id = Column(String, nullable=True)

    # Blocking fields
    is_blocked = Column(Boolean, default=False)
    block_reason = Column(String, nullable=True)
