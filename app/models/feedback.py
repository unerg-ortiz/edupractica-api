from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Float
from sqlalchemy.orm import relationship, backref
import datetime

from app.db.base import Base

class StageFeedback(Base):
    __tablename__ = "stage_feedback"

    id = Column(Integer, primary_key=True, index=True)
    stage_id = Column(Integer, ForeignKey("stages.id"), nullable=False)
    feedback_type = Column(String, nullable=False) # 'hint', 'error_correction', 'encouragement'
    sequence_order = Column(Integer, default=1)
    title = Column(String(200), nullable=False)
    text_content = Column(String, nullable=True)
    media_url = Column(String(500), nullable=True)
    media_type = Column(String, nullable=True) # 'image', 'audio'
    max_hints_per_attempt = Column(Integer, default=3)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.datetime.utcnow)

    # Relationships
    stage = relationship("Stage", backref="feedback_items")


class StudentAttempt(Base):
    __tablename__ = "student_attempts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    stage_id = Column(Integer, ForeignKey("stages.id"), nullable=False)
    attempt_number = Column(Integer, nullable=False)
    is_successful = Column(Boolean, default=False)
    hints_viewed = Column(Integer, default=0)
    time_spent_seconds = Column(Integer, nullable=True)
    error_details = Column(String, nullable=True) # JSON stored as string or just text
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    user = relationship("User", backref="attempts")
    stage = relationship("Stage", backref="student_attempts")


class StudentFeedbackView(Base):
    __tablename__ = "student_feedback_views"

    id = Column(Integer, primary_key=True, index=True)
    attempt_id = Column(Integer, ForeignKey("student_attempts.id"), nullable=False)
    feedback_id = Column(Integer, ForeignKey("stage_feedback.id"), nullable=False)
    viewed_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    attempt = relationship("StudentAttempt", backref="feedback_views")
    feedback = relationship("StageFeedback")
