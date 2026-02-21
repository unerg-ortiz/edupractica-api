from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api import deps
from app.crud import crud_topic, crud_stage
from app.schemas import topic as topic_schemas
from app.schemas import stage as stage_schemas
from app.models.user import User

router = APIRouter()

@router.get("/topics/me", response_model=List[topic_schemas.Topic])
async def get_my_topics(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_professor)
):
    """Get all topics created by the current professor."""
    return crud_topic.get_topics_by_professor(db, professor_id=current_user.id, skip=skip, limit=limit)

@router.post("/topics", response_model=topic_schemas.Topic)
async def create_topic(
    topic: topic_schemas.TopicCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_professor)
):
    """Create a new topic."""
    return crud_topic.create_topic(db, topic, professor_id=current_user.id)

@router.get("/topics/{topic_id}", response_model=topic_schemas.TopicWithStages)
async def get_topic(
    topic_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """Get a specific topic with its stages."""
    db_topic = crud_topic.get_topic(db, topic_id)
    if not db_topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    return db_topic

@router.post("/topics/{topic_id}/stages", response_model=stage_schemas.Stage)
async def add_stage_to_topic(
    topic_id: int,
    stage: stage_schemas.StageCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_professor)
):
    """Add a learning stage to a topic."""
    db_topic = crud_topic.get_topic(db, topic_id)
    if not db_topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    if db_topic.professor_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    # In CRUD create_stage, we need to adapt it to use topic_id
    # For now, let's assume we update crud_stage later or handle it here
    from app.models.stage import Stage
    db_stage = Stage(**stage.model_dump())
    db_stage.topic_id = topic_id
    db.add(db_stage)
    db.commit()
    db.refresh(db_stage)
    return db_stage
