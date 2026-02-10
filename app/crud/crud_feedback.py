from sqlalchemy.orm import Session
from sqlalchemy import desc, func, case
from typing import List, Optional, Any
from fastapi.encoders import jsonable_encoder

from app.models.feedback import StageFeedback, StudentAttempt, StudentFeedbackView
from app.schemas import feedback as schemas
from app.models.stage import Stage, UserStageProgress

def get_feedback(db: Session, feedback_id: int) -> Optional[StageFeedback]:
    return db.query(StageFeedback).filter(StageFeedback.id == feedback_id).first()

def get_feedback_by_stage(
    db: Session, stage_id: int, skip: int = 0, limit: int = 100
) -> List[StageFeedback]:
    return db.query(StageFeedback)\
        .filter(StageFeedback.stage_id == stage_id)\
        .order_by(StageFeedback.sequence_order)\
        .offset(skip)\
        .limit(limit)\
        .all()

def create_feedback(db: Session, feedback: schemas.StageFeedbackCreate) -> StageFeedback:
    db_feedback = StageFeedback(**feedback.dict())
    db.add(db_feedback)
    db.commit()
    db.refresh(db_feedback)
    return db_feedback

def update_feedback(
    db: Session, feedback_id: int, feedback_update: schemas.StageFeedbackUpdate
) -> Optional[StageFeedback]:
    db_feedback = get_feedback(db, feedback_id)
    if not db_feedback:
        return None
        
    update_data = feedback_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_feedback, field, value)
        
    db.add(db_feedback)
    db.commit()
    db.refresh(db_feedback)
    return db_feedback

def delete_feedback(db: Session, feedback_id: int) -> bool:
    db_feedback = get_feedback(db, feedback_id)
    if not db_feedback:
        return False
        
    db.delete(db_feedback)
    db.commit()
    return True

# --- Student Attempt Logic ---

def create_attempt(
    db: Session, user_id: int, attempt: schemas.StudentAttemptCreate
) -> StudentAttempt:
    # Check current attempt number
    count = db.query(StudentAttempt).filter(
        StudentAttempt.user_id == user_id,
        StudentAttempt.stage_id == attempt.stage_id
    ).count()
    
    db_attempt = StudentAttempt(
        user_id=user_id,
        stage_id=attempt.stage_id,
        attempt_number=count + 1,
        is_successful=attempt.is_successful,
        time_spent_seconds=attempt.time_spent_seconds,
        error_details=str(attempt.error_details) if attempt.error_details else None
        # hints_viewed default 0
    )
    db.add(db_attempt)
    db.commit()
    db.refresh(db_attempt)
    
    # If successful, update user progress if not already completed
    if attempt.is_successful:
        from app.crud import crud_stage
        crud_stage.complete_stage(db, user_id, attempt.stage_id)
        
    return db_attempt

def record_feedback_view(
    db: Session, attempt_id: int, feedback_id: int
) -> Optional[StudentFeedbackView]:
    attempt = db.query(StudentAttempt).filter(StudentAttempt.id == attempt_id).first()
    if not attempt:
        return None
        
    feedback = get_feedback(db, feedback_id)
    if not feedback:
        return None
        
    # Check if max hints reached
    if feedback.feedback_type == 'top_failed_hint': # Example check
       pass # Implement specific logic
       
    # Check if already viewed
    existing = db.query(StudentFeedbackView).filter(
        StudentFeedbackView.attempt_id == attempt_id,
        StudentFeedbackView.feedback_id == feedback_id
    ).first()
    
    if existing:
        return existing
        
    # Create view
    view = StudentFeedbackView(attempt_id=attempt_id, feedback_id=feedback_id)
    db.add(view)
    
    # Increment view count on attempt
    attempt.hints_viewed += 1
    db.add(attempt)
    
    db.commit()
    db.refresh(view)
    return view

# --- Analytics Logic ---

def get_stage_analytics(db: Session, stage_id: int) -> schemas.StageAnalytics:
    total_attempts = db.query(StudentAttempt).filter(StudentAttempt.stage_id == stage_id).count()
    failed = db.query(StudentAttempt).filter(StudentAttempt.stage_id == stage_id, StudentAttempt.is_successful == False).count()
    successful = db.query(StudentAttempt).filter(StudentAttempt.stage_id == stage_id, StudentAttempt.is_successful == True).count()
    
    success_rate = 0.0
    if total_attempts > 0:
        success_rate = (successful / total_attempts) * 100
        
    avg_hints = db.query(func.avg(StudentAttempt.hints_viewed)).filter(StudentAttempt.stage_id == stage_id).scalar() or 0
    max_hints = db.query(func.max(StudentAttempt.hints_viewed)).filter(StudentAttempt.stage_id == stage_id).scalar() or 0
    avg_time = db.query(func.avg(StudentAttempt.time_spent_seconds)).filter(StudentAttempt.stage_id == stage_id).scalar()
    
    import datetime
    return schemas.StageAnalytics(
        id=stage_id, # using stage_id as ID for analytics object
        stage_id=stage_id,
        total_attempts=total_attempts,
        failed_attempts=failed,
        successful_attempts=successful,
        success_rate=success_rate,
        avg_hints_used=float(avg_hints),
        max_hints_used=int(max_hints),
        most_common_errors=[], # Placeholder
        avg_time_seconds=float(avg_time) if avg_time else None,
        last_updated=datetime.datetime.utcnow()
    )

def get_most_difficult_stages(db: Session, limit: int = 5) -> List[schemas.StageAnalytics]:
    # Group by stage_id, order by failure count desc
    # This is a bit complex in pure ORM, might need raw SQL or subqueries
    # For now, simplistic approach: iterate all stages (inefficient but works for MVP)
    # A better approach:
    
    stage_stats = db.query(
        StudentAttempt.stage_id,
        func.count(StudentAttempt.id).label('total'),
        func.sum(case((StudentAttempt.is_successful == False, 1), else_=0)).label('failures')
    ).group_by(StudentAttempt.stage_id).all()
    
    results = []
    for stage_id, total, failures in stage_stats:
        if total > 0:
            rate = failures / total
            results.append((stage_id, rate))
            
    results.sort(key=lambda x: x[1], reverse=True)
    top_stages = results[:limit]
    
    analytics_list = []
    for stage_id, rate in top_stages:
        analytics_list.append(get_stage_analytics(db, stage_id))
        
    return analytics_list
