from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.api import deps
from app.crud import crud_stage
from app.schemas import stage as stage_schemas
from app.schemas.interactive import InteractiveConfig
from app.models.user import User
from app.core import media

router = APIRouter()


# Note: Endpoints for listing stages by topic are in topics.py
# GET /topics/{topic_id}/stages/progress - get all stages with progress
# GET /categories/{category_id}/topics - get approved topics in category


@router.get("/stages/{stage_id}", response_model=stage_schemas.Stage)
async def get_stage(
    stage_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """Get a specific stage by ID"""
    stage = crud_stage.get_stage(db, stage_id)
    if not stage:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stage not found"
        )
    return stage


@router.post("/stages", response_model=stage_schemas.Stage)
async def create_stage(
    stage: stage_schemas.StageCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_professor)
):
    """
    Create a new stage.
    Stages should be created in sequential order.
    """
    return crud_stage.create_stage(db, stage, professor_id=current_user.id)


@router.put("/stages/{stage_id}", response_model=stage_schemas.Stage)
async def update_stage(
    stage_id: int,
    stage_update: stage_schemas.StageUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_professor)
):
    """Update a stage"""
    db_stage = crud_stage.get_stage(db, stage_id)
    if not db_stage:
        raise HTTPException(status_code=404, detail="Stage not found")
    
    if not current_user.is_superuser and db_stage.professor_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only update your own stages")
        
    updated_stage = crud_stage.update_stage(db, stage_id, stage_update)
    return updated_stage


@router.delete("/stages/{stage_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_stage(
    stage_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_professor)
):
    """Soft delete a stage"""
    db_stage = crud_stage.get_stage(db, stage_id)
    if not db_stage:
        raise HTTPException(status_code=404, detail="Stage not found")
        
    if not current_user.is_superuser and db_stage.professor_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only delete your own stages")
        
    success = crud_stage.delete_stage(db, stage_id)
    return None


@router.post("/stages/{stage_id}/complete", response_model=stage_schemas.UserStageProgress)
async def complete_stage(
    stage_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """
    Mark a stage as completed for the current user.
    This will automatically unlock the next stage in the sequence.
    
    Requirements:
    - The stage must be unlocked for the user
    - The user must have successfully completed the challenge
    """
    # Check if stage exists
    stage = crud_stage.get_stage(db, stage_id)
    if not stage:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stage not found"
        )
    
    # Check if stage is unlocked for the user
    user_progress = crud_stage.get_user_stage_progress(db, current_user.id, stage_id)
    if not user_progress or not user_progress.is_unlocked:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This stage is locked. Complete the previous stage first."
        )
    
    # Mark stage as completed and unlock next stage
    updated_progress = crud_stage.complete_stage(db, current_user.id, stage_id)
    return updated_progress




@router.post("/stages/{stage_id}/interactive", response_model=stage_schemas.Stage)
async def update_interactive_challenge(
    stage_id: int,
    config: InteractiveConfig,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_professor)
):
    """
    Configure the interactive challenge (Drag and Drop/Matching) for a stage.
    Professor can update their own stages.
    """
    db_stage = crud_stage.get_stage(db, stage_id)
    if not db_stage:
        raise HTTPException(status_code=404, detail="Stage not found")
    
    if not current_user.is_superuser and db_stage.professor_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only update your own stages")
    
    updated_stage = crud_stage.update_stage(
        db, stage_id, stage_schemas.StageUpdate(interactive_config=config)
    )
    if not updated_stage:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stage not found"
        )
    return updated_stage
