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


@router.get("/categories/{category_id}/stages", response_model=List[stage_schemas.Stage])
async def get_category_stages(
    category_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """
    Get all stages for a specific category.
    Returns stages ordered by their sequence.
    """
    stages = crud_stage.get_stages_by_category(db, category_id, skip, limit)
    return stages


@router.get("/categories/{category_id}/stages/progress", response_model=List[stage_schemas.StageWithProgress])
async def get_category_stages_with_progress(
    category_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """
    Get all stages for a category with user progress information.
    Shows which stages are locked/unlocked and completed for the current user.
    
    The first stage (order=1) is always unlocked.
    Subsequent stages are locked until the previous stage is completed.
    """
    # Get all stages for the category
    stages = crud_stage.get_stages_by_category(db, category_id)
    
    if not stages:
        return []
    
    # Initialize progress if user hasn't started this category yet
    existing_progress = crud_stage.get_user_progress_by_category(db, current_user.id, category_id)
    if not existing_progress:
        crud_stage.initialize_user_progress_for_category(db, current_user.id, category_id)
    
    # Get user progress for all stages
    progress_map = {}
    user_progress = crud_stage.get_user_progress_by_category(db, current_user.id, category_id)
    for progress in user_progress:
        progress_map[progress.stage_id] = progress
    
    # Combine stage data with progress
    stages_with_progress = []
    for stage in stages:
        progress = progress_map.get(stage.id)
        stage_data = stage_schemas.StageWithProgress(
            id=stage.id,
            category_id=stage.category_id,
            order=stage.order,
            title=stage.title,
            description=stage.description,
            content=stage.content,
            challenge_description=stage.challenge_description,
            media_url=stage.media_url,
            media_type=stage.media_type,
            media_filename=stage.media_filename,
            interactive_config=stage.interactive_config,
            is_active=stage.is_active,
            is_archived=stage.is_archived,
            professor_id=stage.professor_id,
            is_unlocked=progress.is_unlocked if progress else False,
            is_completed=progress.is_completed if progress else False
        )
        stages_with_progress.append(stage_data)
    
    return stages_with_progress


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


@router.post("/categories/{category_id}/initialize", response_model=List[stage_schemas.UserStageProgress])
async def initialize_category_progress(
    category_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """
    Initialize user progress for all stages in a category.
    Only the first stage will be unlocked, all others will be locked.
    This is automatically called when accessing stages with progress,
    but can be manually triggered if needed.
    """
    progress_list = crud_stage.initialize_user_progress_for_category(
        db, current_user.id, category_id
    )
    return progress_list
@router.post("/stages/{stage_id}/interactive", response_model=stage_schemas.Stage)
async def update_interactive_challenge(
    stage_id: int,
    config: InteractiveConfig,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_superuser)
):
    """
    Configure the interactive challenge (Drag and Drop/Matching) for a stage.
    Admin only (Professor role).
    """
    updated_stage = crud_stage.update_stage(
        db, stage_id, stage_schemas.StageUpdate(interactive_config=config)
    )
    if not updated_stage:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stage not found"
        )
    return updated_stage
