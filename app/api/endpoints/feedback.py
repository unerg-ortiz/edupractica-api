from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.api import deps
from app.crud import crud_feedback, crud_stage
from app.schemas import feedback as feedback_schemas
from app.models.user import User
from app.core import media

router = APIRouter()

# ================= Teacher Endpoints =================

@router.post("/stages/{stage_id}/feedback", response_model=feedback_schemas.StageFeedback)
async def create_feedback(
    stage_id: int,
    feedback: feedback_schemas.StageFeedbackCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_superuser)
):
    """Create new feedback for a stage (Teacher only)"""
    stage = crud_stage.get_stage(db, stage_id)
    if not stage:
        raise HTTPException(status_code=404, detail="Stage not found")
        
    return crud_feedback.create_feedback(db, feedback)


@router.get("/stages/{stage_id}/feedback", response_model=List[feedback_schemas.StageFeedback])
async def get_stage_feedback(
    stage_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_superuser)
):
    """Get all feedback configured for a stage (Teacher only)"""
    stage = crud_stage.get_stage(db, stage_id)
    if not stage:
        raise HTTPException(status_code=404, detail="Stage not found")
        
    return crud_feedback.get_feedback_by_stage(db, stage_id, skip, limit)


@router.put("/feedback/{feedback_id}", response_model=feedback_schemas.StageFeedback)
async def update_feedback(
    feedback_id: int,
    feedback_update: feedback_schemas.StageFeedbackUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_superuser)
):
    """Update feedback configuration"""
    feedback = crud_feedback.update_feedback(db, feedback_id, feedback_update)
    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")
    return feedback


@router.delete("/feedback/{feedback_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_feedback(
    feedback_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_superuser)
):
    """Delete feedback"""
    success = crud_feedback.delete_feedback(db, feedback_id)
    if not success:
        raise HTTPException(status_code=404, detail="Feedback not found")
    return None


@router.post("/feedback/{feedback_id}/media", response_model=feedback_schemas.StageFeedback)
async def upload_feedback_media(
    feedback_id: int,
    file: UploadFile = File(...),
    media_type: str = Form(...),  # "image" or "audio"
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_superuser)
):
    """Upload media file for feedback"""
    feedback = crud_feedback.get_feedback(db, feedback_id)
    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")
        
    # Validate and save file
    media.validate_file(file, media_type)
    file_path = media.save_upload_file(file, feedback.stage.id)
    
    # Update feedback record
    update_data = feedback_schemas.StageFeedbackUpdate(
        media_type=media_type,
        media_url=file_path
    )
    return crud_feedback.update_feedback(db, feedback_id, update_data)


@router.post("/feedback/preview", response_model=feedback_schemas.FeedbackPreview)
async def preview_feedback(
    data: feedback_schemas.FeedbackPreview,
    current_user: User = Depends(deps.get_current_active_superuser)
):
    """
    Generate a preview structure for frontend testing.
    Does not interact with DB, just validates structure.
    """
    return data


# ================= Student Endpoints =================

@router.post("/stages/{stage_id}/attempts", response_model=feedback_schemas.StudentAttempt)
async def record_attempt(
    stage_id: int,
    attempt: feedback_schemas.StudentAttemptCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """Record a student attempt on a stage"""
    # Verify stage exists
    stage = crud_stage.get_stage(db, stage_id)
    if not stage:
        raise HTTPException(status_code=404, detail="Stage not found")
        
    return crud_feedback.create_attempt(db, current_user.id, attempt)


@router.get("/stages/{stage_id}/hints", response_model=List[feedback_schemas.StageFeedback])
async def get_available_hints(
    stage_id: int,
    attempt_id: Optional[int] = None,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """
    Get available hints for a stage.
    If attempt_id is provided, logic could filter based on usage limits.
    For now, returns all configured hints for the stage.
    """
    # Simply return all active hints for the stage
    # The client/frontend will manage progressive disclosure based on attempt count
    return crud_feedback.get_feedback_by_stage(db, stage_id)


@router.post("/attempts/{attempt_id}/view-hint/{feedback_id}", response_model=feedback_schemas.StudentFeedbackView)
async def record_hint_view(
    attempt_id: int,
    feedback_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """
    Record that a student viewed a specific hint.
    Enforces the max hints per attempt limit.
    """
    result = crud_feedback.record_feedback_view(db, attempt_id, feedback_id)
    
    if not result:
        # Check if it was limit reached or just invalid IDs
        # For simplicity, assuming validation passed but limit reached
        # A more robust implementation would distinguish errors
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Cannot view hint: Limit reached for this attempt or invalid ID"
        )
        
    return result
