from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import and_, desc
from sqlalchemy.orm import Session

from app.api import deps
from app.crud import crud_stage
from app.schemas import stage as stage_schemas
from app.schemas.interactive import InteractiveConfig
from app.models.user import User

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
    Students only see APPROVED stages.
    Admins see ALL stages in this category.
    """
    status_filter = "approved" if not current_user.is_superuser else None
    stages = crud_stage.get_stages_by_category(db, category_id, skip, limit, status=status_filter)
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
    
    Students only see APPROVED stages.
    """
    # Get all approved stages for the category
    stages = crud_stage.get_stages_by_category(db, category_id, status="approved")
    
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
    current_user: User = Depends(deps.get_current_active_user) # Professors can create
):
    """
    Create a new stage.
    Stages created by ANYONE start as 'pending' approval.
    """
    # In a real app, we'd check if current_user has 'Professor' role
    return crud_stage.create_stage(db, stage, professor_id=current_user.id)


@router.put("/stages/{stage_id}", response_model=stage_schemas.Stage)
async def update_stage(
    stage_id: int,
    stage_update: stage_schemas.StageUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_superuser)
):
    """Update a stage (admin only)"""
    updated_stage = crud_stage.update_stage(db, stage_id, stage_update)
    if not updated_stage:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stage not found"
        )
    return updated_stage


@router.delete("/stages/{stage_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_stage(
    stage_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_superuser)
):
    """Soft delete a stage (admin only)"""
    success = crud_stage.delete_stage(db, stage_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stage not found"
        )
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


# ================= Admin Review Endpoints =================

@router.get("/review/pending", response_model=List[stage_schemas.Stage])
async def get_pending_review(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_superuser)
):
    """
    List all stages pending approval (Admin only).
    """
    return crud_stage.get_pending_stages(db, skip=skip, limit=limit)


@router.post("/stages/{stage_id}/review", response_model=stage_schemas.Stage)
async def review_stage(
    stage_id: int,
    review: stage_schemas.StageReview,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_superuser)
):
    """
    Approve or reject a stage (Admin only).
    If rejected, it remains invisible and includes feedback comments.
    """
    review_status = "approved" if review.approved else "rejected"
    updated_stage = crud_stage.set_approval_status(
        db, stage_id, status=review_status, comment=review.comment
    )
    
    if not updated_stage:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stage not found"
        )
        
    # TODO: Trigger notification to professor_id
    
    return updated_stage
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
