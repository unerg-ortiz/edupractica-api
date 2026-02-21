from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class Topic(Base):
    """
    Represents an educational theme or topic created by a professor.
    A topic contains multiple learning stages.
    """
    __tablename__ = "topics"

    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    professor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(String, nullable=True)
    
    # Approval Workflow
    approval_status = Column(String(20), default="pending", nullable=False) # pending, approved, rejected
    approval_comment = Column(String, nullable=True) # Feedback from admin
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())
    
    is_active = Column(Boolean, default=True)
    is_archived = Column(Boolean, default=False)

    # Relationships
    category = relationship("Category", backref="topics")
    professor = relationship("User", backref="topics")
    stages = relationship("Stage", back_populates="topic", cascade="all, delete-orphan")
