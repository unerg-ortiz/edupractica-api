from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_
from datetime import datetime

from app.models.feedback import StageFeedback, StudentAttempt, StudentFeedbackView, StageAnalytics
from app.models.stage import Stage
from app.schemas.feedback import (
    StageFeedbackCreate, 
    StageFeedbackUpdate, 
    StudentAttemptCreate,
    StageAnalytics as StageAnalyticsSchema
)


# ============= Stage Feedback CRUD =============

def create_feedback(db: Session, feedback: StageFeedbackCreate) -> StageFeedback:
    """Create new feedback for a stage"""
    db_feedback = StageFeedback(
        stage_id=feedback.stage_id,
        feedback_type=feedback.feedback_type,
        sequence_order=feedback.sequence_order,
        max_hints_per_attempt=feedback.max_hints_per_attempt,
        title=feedback.title,
        text_content=feedback.text_content,
        media_type=feedback.media_type,
        media_url=feedback.media_url,
        preview_settings=feedback.preview_settings,
        is_active=feedback.is_active
    )
    db.add(db_feedback)
    db.commit()
    db.refresh(db_feedback)
    return db_feedback


def get_feedback_by_stage(
    db: Session, 
    stage_id: int, 
    skip: int = 0, 
    limit: int = 100
) -> List[StageFeedback]:
    """Get all feedback for a stage, ordered by sequence"""
    return (
        db.query(StageFeedback)
        .filter(StageFeedback.stage_id == stage_id, StageFeedback.is_active == True)
        .order_by(StageFeedback.sequence_order)
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_feedback(db: Session, feedback_id: int) -> Optional[StageFeedback]:
    """Get a specific feedback by ID"""
    return db.query(StageFeedback).filter(StageFeedback.id == feedback_id).first()


def update_feedback(
    db: Session, 
    feedback_id: int, 
    feedback_update: StageFeedbackUpdate
) -> Optional[StageFeedback]:
    """Update feedback"""
    db_feedback = get_feedback(db, feedback_id)
    if not db_feedback:
        return None
    
    update_data = feedback_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_feedback, field, value)
    
    db.commit()
    db.refresh(db_feedback)
    return db_feedback


def delete_feedback(db: Session, feedback_id: int) -> bool:
    """Soft delete feedback"""
    db_feedback = get_feedback(db, feedback_id)
    if not db_feedback:
        return False
    
    db_feedback.is_active = False
    db.commit()
    return True


# ============= Student Attempt CRUD =============

def create_attempt(
    db: Session, 
    user_id: int, 
    attempt: StudentAttemptCreate
) -> StudentAttempt:
    """
    Record a new student attempt.
    Also calculates the attempt number automatically.
    """
    # Calculate attempt number
    last_attempt = (
        db.query(StudentAttempt)
        .filter(
            StudentAttempt.user_id == user_id,
            StudentAttempt.stage_id == attempt.stage_id
        )
        .order_by(desc(StudentAttempt.attempt_number))
        .first()
    )
    
    next_attempt_number = (last_attempt.attempt_number + 1) if last_attempt else 1
    
    db_attempt = StudentAttempt(
        user_id=user_id,
        stage_id=attempt.stage_id,
        attempt_number=next_attempt_number,
        is_successful=attempt.is_successful,
        error_details=attempt.error_details,
        time_spent_seconds=attempt.time_spent_seconds
    )
    
    db.add(db_attempt)
    db.commit()
    db.refresh(db_attempt)
    
    # Update analytics asynchronously (or synchronously for simplicity here)
    update_stage_analytics(db, attempt.stage_id)
    
    return db_attempt


def get_student_attempts(
    db: Session, 
    user_id: int, 
    stage_id: int
) -> List[StudentAttempt]:
    """Get all attempts for a student on a stage"""
    return (
        db.query(StudentAttempt)
        .filter(
            StudentAttempt.user_id == user_id,
            StudentAttempt.stage_id == stage_id
        )
        .order_by(StudentAttempt.attempt_number)
        .all()
    )


# ============= Feedback View CRUD =============

def record_feedback_view(
    db: Session, 
    attempt_id: int, 
    feedback_id: int
) -> Optional[StudentFeedbackView]:
    """
    Record that a student viewed a specific feedback/hint.
    Checks if the limit has been reached first.
    """
    attempt = db.query(StudentAttempt).get(attempt_id)
    feedback = get_feedback(db, feedback_id)
    
    if not attempt or not feedback:
        return None
    
    # Check if already viewed
    existing_view = (
        db.query(StudentFeedbackView)
        .filter(
            StudentFeedbackView.attempt_id == attempt_id,
            StudentFeedbackView.feedback_id == feedback_id
        )
        .first()
    )
    
    if existing_view:
        return existing_view
    
    # Check limit
    if feedback.max_hints_per_attempt:
        if attempt.hints_viewed >= feedback.max_hints_per_attempt:
            # Limit reached
            return None
    
    # Record view
    view = StudentFeedbackView(attempt_id=attempt_id, feedback_id=feedback_id)
    db.add(view)
    
    # Update attempt counter
    attempt.hints_viewed += 1
    
    db.commit()
    db.refresh(view)
    return view


# ============= Analytics CRUD =============

def update_stage_analytics(db: Session, stage_id: int) -> StageAnalytics:
    """
    Recalculate analytics for a stage based on all attempts.
    This is an expensive operation, ideally should be a background task.
    """
    # Get all attempts
    attempts_query = db.query(StudentAttempt).filter(StudentAttempt.stage_id == stage_id)
    total = attempts_query.count()
    
    if total == 0:
        return _get_or_create_analytics(db, stage_id)
    
    failed = attempts_query.filter(StudentAttempt.is_successful == False).count()
    successful = attempts_query.filter(StudentAttempt.is_successful == True).count()
    
    # Calculate averages
    avg_hints = db.query(func.avg(StudentAttempt.hints_viewed)).filter(StudentAttempt.stage_id == stage_id).scalar() or 0.0
    max_hints = db.query(func.max(StudentAttempt.hints_viewed)).filter(StudentAttempt.stage_id == stage_id).scalar() or 0
    avg_time = db.query(func.avg(StudentAttempt.time_spent_seconds)).filter(StudentAttempt.stage_id == stage_id).scalar() or 0.0
    
    # Get or create analytics record
    analytics = _get_or_create_analytics(db, stage_id)
    
    analytics.total_attempts = total
    analytics.failed_attempts = failed
    analytics.successful_attempts = successful
    analytics.success_rate = (successful / total) * 100 if total > 0 else 0.0
    analytics.avg_hints_used = float(avg_hints)
    analytics.max_hints_used = int(max_hints)
    analytics.avg_time_seconds = float(avg_time)
    
    # Simple error analysis (aggregating error types from JSON)
    # This is a simplified version; in production, you'd want more robust JSON aggregation
    
    db.commit()
    db.refresh(analytics)
    return analytics


def _get_or_create_analytics(db: Session, stage_id: int) -> StageAnalytics:
    analytics = db.query(StageAnalytics).filter(StageAnalytics.stage_id == stage_id).first()
    if not analytics:
        analytics = StageAnalytics(stage_id=stage_id)
        db.add(analytics)
        db.commit()
        db.refresh(analytics)
    return analytics


def get_stage_analytics(db: Session, stage_id: int) -> StageAnalytics:
    analytics = db.query(StageAnalytics).filter(StageAnalytics.stage_id == stage_id).first()
    if not analytics:
        # Generate on demand if missing
        return update_stage_analytics(db, stage_id)
    return analytics


def get_most_difficult_stages(db: Session, limit: int = 5) -> List[StageAnalytics]:
    """Get stages with the lowest success rate (that have at least 5 attempts)"""
    return (
        db.query(StageAnalytics)
        .filter(StageAnalytics.total_attempts >= 5)
        .order_by(StageAnalytics.success_rate.asc())
        .limit(limit)
        .all()
    )
