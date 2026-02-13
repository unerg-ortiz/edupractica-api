from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, JSON, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class Stage(Base):
    """
    Represents a learning stage in the educational content.
    Stages are sequential and can be locked/unlocked based on completion.
    """
    __tablename__ = "stages"

    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    professor_id = Column(Integer, ForeignKey("users.id"), nullable=True) # Who created/submitted the stage
    order = Column(Integer, nullable=False, index=True)  # Sequential order (1, 2, 3...)
    title = Column(String(100), nullable=False)
    description = Column(String, nullable=True)
    content = Column(String, nullable=True)  # Educational content
    challenge_description = Column(String, nullable=True)  # Challenge to complete this stage
    media_url = Column(String, nullable=True)  # Path to uploaded video/audio/image
    media_type = Column(String(20), nullable=True)  # 'video', 'audio', or 'image'
    media_filename = Column(String(255), nullable=True) # Original filename
    interactive_config = Column(JSON, nullable=True) # Configuration for drag-and-drop/matching games
    
    # Approval Workflow
    approval_status = Column(String(20), default="pending", nullable=False) # pending, approved, rejected
    approval_comment = Column(String, nullable=True) # Feedback from admin
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())
    
    is_active = Column(Boolean, default=True)
    
    # Relationships
    category = relationship("Category", backref="stages")
    user_progress = relationship("UserStageProgress", back_populates="stage")


class UserStageProgress(Base):
    """
    Tracks user progress through stages.
    A user can only unlock stage n+1 after completing stage n.
    """
    __tablename__ = "user_stage_progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    stage_id = Column(Integer, ForeignKey("stages.id"), nullable=False)
    is_completed = Column(Boolean, default=False)
    is_unlocked = Column(Boolean, default=False)
    
    # Relationships
    user = relationship("User", backref="stage_progress")
    stage = relationship("Stage", back_populates="user_progress")
