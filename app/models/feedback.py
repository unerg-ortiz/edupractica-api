from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Float, JSON, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class StageFeedback(Base):
    """
    Feedback and hints configured by teachers for each stage.
    Can include text, images, or audio to help students when they fail.
    """
    __tablename__ = "stage_feedback"

    id = Column(Integer, primary_key=True, index=True)
    stage_id = Column(Integer, ForeignKey("stages.id"), nullable=False, index=True)
    
    # Type of feedback: hint, encouragement, error_correction
    feedback_type = Column(String(50), nullable=False, default="hint")
    
    # Sequential order for displaying hints (1, 2, 3...)
    sequence_order = Column(Integer, nullable=False, default=1)
    
    # Maximum hints allowed per attempt (scaffolding control)
    max_hints_per_attempt = Column(Integer, nullable=True, default=3)
    
    # Content
    title = Column(String(200), nullable=False)
    text_content = Column(Text, nullable=True)
    
    # Media support (image, audio)
    media_type = Column(String(20), nullable=True)  # 'image', 'audio', null
    media_url = Column(String(500), nullable=True)  # Path to media file
    
    # Responsive preview settings (stored as JSON)
    preview_settings = Column(JSON, nullable=True)  # {mobile: {...}, tablet: {...}}
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    stage = relationship("Stage", backref="feedbacks")
    views = relationship("StudentFeedbackView", back_populates="feedback", cascade="all, delete-orphan")


class StudentAttempt(Base):
    """
    Tracks every attempt a student makes on a stage.
    Used for analytics and understanding student difficulties.
    """
    __tablename__ = "student_attempts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    stage_id = Column(Integer, ForeignKey("stages.id"), nullable=False, index=True)
    
    # Attempt tracking
    attempt_number = Column(Integer, nullable=False, default=1)
    is_successful = Column(Boolean, default=False)
    
    # Hint usage tracking
    hints_viewed = Column(Integer, default=0)
    
    # Additional context
    error_details = Column(JSON, nullable=True)  # Store error information
    time_spent_seconds = Column(Integer, nullable=True)  # Time spent on attempt
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relationships
    user = relationship("User", back_populates="attempts")
    stage = relationship("Stage", backref="attempts")
    feedback_views = relationship("StudentFeedbackView", back_populates="attempt", cascade="all, delete-orphan")


class StudentFeedbackView(Base):
    """
    Tracks which feedback/hints a student has viewed during an attempt.
    Ensures students don't exceed the maximum hints per attempt.
    """
    __tablename__ = "student_feedback_views"

    id = Column(Integer, primary_key=True, index=True)
    attempt_id = Column(Integer, ForeignKey("student_attempts.id"), nullable=False, index=True)
    feedback_id = Column(Integer, ForeignKey("stage_feedback.id"), nullable=False, index=True)
    
    viewed_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    attempt = relationship("StudentAttempt", back_populates="feedback_views")
    feedback = relationship("StageFeedback", back_populates="views")


class StageAnalytics(Base):
    """
    Aggregated analytics for stages to identify difficult challenges.
    This table can be updated periodically or on-demand.
    """
    __tablename__ = "stage_analytics"

    id = Column(Integer, primary_key=True, index=True)
    stage_id = Column(Integer, ForeignKey("stages.id"), nullable=False, unique=True, index=True)
    
    # Aggregate metrics
    total_attempts = Column(Integer, default=0)
    failed_attempts = Column(Integer, default=0)
    successful_attempts = Column(Integer, default=0)
    success_rate = Column(Float, default=0.0)  # Percentage
    
    # Hint usage
    avg_hints_used = Column(Float, default=0.0)
    max_hints_used = Column(Integer, default=0)
    
    # Common errors (JSON array)
    most_common_errors = Column(JSON, nullable=True)
    
    # Average time to complete
    avg_time_seconds = Column(Float, nullable=True)
    
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    stage = relationship("Stage", backref="analytics", uselist=False)
