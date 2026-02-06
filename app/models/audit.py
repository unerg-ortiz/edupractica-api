from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from app.db.base import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    action = Column(String, nullable=False, index=True)
    target_type = Column(String, nullable=False)  # e.g., "USER"
    target_id = Column(String, nullable=False)    # ID of the object being acted upon
    details = Column(String, nullable=True)       # e.g., "Reason: Spam"
    actor_id = Column(Integer, ForeignKey("users.id"), nullable=True) # Who performed the action
    timestamp = Column(DateTime, default=datetime.utcnow)
