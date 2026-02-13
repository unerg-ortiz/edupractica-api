from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.stage import Stage, UserStageProgress
from app.schemas.stage import StageCreate, StageUpdate


def get_stage(db: Session, stage_id: int) -> Optional[Stage]:
    """Get a stage by ID"""
    return db.query(Stage).filter(Stage.id == stage_id).first()


def get_stages_by_category(
    db: Session, 
    category_id: int, 
    skip: int = 0, 
    limit: int = 100
) -> List[Stage]:
    """Get all stages for a category, ordered by sequence"""
    return (
        db.query(Stage)
        .filter(Stage.category_id == category_id, Stage.is_active == True)
        .order_by(Stage.order)
        .offset(skip)
        .limit(limit)
        .all()
    )


def create_stage(db: Session, stage: StageCreate, professor_id: Optional[int] = None) -> Stage:
    """Create a new stage"""
    db_stage = Stage(**stage.model_dump(), professor_id=professor_id)
    db.add(db_stage)
    db.commit()
    db.refresh(db_stage)
    return db_stage


def update_stage(db: Session, stage_id: int, stage_update: StageUpdate) -> Optional[Stage]:
    """Update an existing stage"""
    db_stage = get_stage(db, stage_id)
    if not db_stage:
        return None
    
    update_data = stage_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_stage, field, value)
    
    db.commit()
    db.refresh(db_stage)
    return db_stage


def delete_stage(db: Session, stage_id: int) -> bool:
    """Soft delete a stage by setting is_active to False"""
    db_stage = get_stage(db, stage_id)
    if not db_stage:
        return False
    
    db_stage.is_active = False
    db.commit()
    return True


# User Stage Progress CRUD operations

def get_user_stage_progress(
    db: Session, 
    user_id: int, 
    stage_id: int
) -> Optional[UserStageProgress]:
    """Get user progress for a specific stage"""
    return (
        db.query(UserStageProgress)
        .filter(
            and_(
                UserStageProgress.user_id == user_id,
                UserStageProgress.stage_id == stage_id
            )
        )
        .first()
    )


def get_user_progress_by_category(
    db: Session, 
    user_id: int, 
    category_id: int
) -> List[UserStageProgress]:
    """Get all user progress for stages in a category"""
    return (
        db.query(UserStageProgress)
        .join(Stage)
        .filter(
            and_(
                UserStageProgress.user_id == user_id,
                Stage.category_id == category_id
            )
        )
        .order_by(Stage.order)
        .all()
    )


def create_or_update_user_progress(
    db: Session,
    user_id: int,
    stage_id: int,
    is_completed: bool = False,
    is_unlocked: bool = False
) -> UserStageProgress:
    """Create or update user progress for a stage"""
    db_progress = get_user_stage_progress(db, user_id, stage_id)
    
    if db_progress:
        # Update existing progress
        db_progress.is_completed = is_completed
        db_progress.is_unlocked = is_unlocked
    else:
        # Create new progress
        db_progress = UserStageProgress(
            user_id=user_id,
            stage_id=stage_id,
            is_completed=is_completed,
            is_unlocked=is_unlocked
        )
        db.add(db_progress)
    
    db.commit()
    db.refresh(db_progress)
    return db_progress


def complete_stage(db: Session, user_id: int, stage_id: int) -> Optional[UserStageProgress]:
    """
    Mark a stage as completed and unlock the next stage.
    Returns the updated progress or None if stage doesn't exist.
    """
    # Get the current stage
    current_stage = get_stage(db, stage_id)
    if not current_stage:
        return None
    
    # Mark current stage as completed
    current_progress = create_or_update_user_progress(
        db, user_id, stage_id, is_completed=True, is_unlocked=True
    )
    
    # Find and unlock the next stage
    next_stage = (
        db.query(Stage)
        .filter(
            and_(
                Stage.category_id == current_stage.category_id,
                Stage.order == current_stage.order + 1,
                Stage.is_active == True
            )
        )
        .first()
    )
    
    if next_stage:
        # Unlock the next stage
        create_or_update_user_progress(
            db, user_id, next_stage.id, is_completed=False, is_unlocked=True
        )
    
    return current_progress


def initialize_user_progress_for_category(
    db: Session, 
    user_id: int, 
    category_id: int
) -> List[UserStageProgress]:
    """
    Initialize user progress for all stages in a category.
    Only the first stage (order=1) is unlocked, all others are locked.
    """
    stages = get_stages_by_category(db, category_id)
    progress_list = []
    
    for stage in stages:
        # Check if progress already exists
        existing_progress = get_user_stage_progress(db, user_id, stage.id)
        if not existing_progress:
            # First stage is unlocked, others are locked
            is_unlocked = (stage.order == 1)
            progress = create_or_update_user_progress(
                db, user_id, stage.id, is_completed=False, is_unlocked=is_unlocked
            )
            progress_list.append(progress)
        else:
            progress_list.append(existing_progress)
    
    return progress_list
