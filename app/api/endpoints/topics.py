from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api import deps
from app.crud import crud_topic, crud_stage
from app.schemas import topic as topic_schemas
from app.schemas import stage as stage_schemas
from app.models.user import User

router = APIRouter()

# =================== Professor Endpoints ===================

@router.get("/topics/me", response_model=List[topic_schemas.TopicWithStages])
async def get_my_topics(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_professor)
):
    """Get all topics created by the current professor with their stages."""
    topics = crud_topic.get_topics_by_professor(db, professor_id=current_user.id, skip=skip, limit=limit)
    
    # Load stages for each topic
    result = []
    for topic in topics:
        topic.stages  # This triggers lazy loading of the relationship
        result.append(topic)
    
    return result

@router.post("/topics", response_model=topic_schemas.Topic)
async def create_topic(
    topic: topic_schemas.TopicCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_professor)
):
    """Create a new topic (will be pending approval)."""
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
    
    # Access Control:
    # 1. Admins see everything
    # 2. Owners see their own topics
    # 3. Students see approved topics
    if not (current_user.is_superuser or 
            db_topic.professor_id == current_user.id or 
            (current_user.role == "student" and db_topic.approval_status == "approved")):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="No tienes permiso para acceder a este tema."
        )
    
    # Add professor name to response
    topic_dict = topic_schemas.TopicWithStages.model_validate(db_topic).model_dump()
    topic_dict['professor_name'] = db_topic.professor.full_name if db_topic.professor else None
    return topic_schemas.TopicWithStages(**topic_dict)

@router.put("/topics/{topic_id}", response_model=topic_schemas.Topic)
async def update_topic(
    topic_id: int,
    topic_update: topic_schemas.TopicUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_professor)
):
    """Update a topic (professor can only update their own topics)."""
    db_topic = crud_topic.get_topic(db, topic_id)
    if not db_topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    if db_topic.professor_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    return crud_topic.update_topic(db, topic_id, topic_update)
    
@router.delete("/topics/{topic_id}")
async def delete_topic(
    topic_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_professor)
):
    """Delete a topic (soft delete)."""
    db_topic = crud_topic.get_topic(db, topic_id)
    if not db_topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    if db_topic.professor_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    success = crud_topic.delete_topic(db, topic_id)
    if not success:
        raise HTTPException(status_code=404, detail="Topic not found")
        
    return {"message": "Topic deleted successfully"}

@router.post("/topics/{topic_id}/stages", response_model=stage_schemas.Stage)
async def add_stage_to_topic(
    topic_id: int,
    stage: stage_schemas.StageCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_professor)
):
    """Add a learning stage to a topic."""
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info(f"[ADD_STAGE] Request received - Topic ID: {topic_id}, User: {current_user.id}")
    logger.debug(f"[ADD_STAGE] Stage data: {stage.model_dump()}")
    
    db_topic = crud_topic.get_topic(db, topic_id)
    if not db_topic:
        logger.warning(f"[ADD_STAGE] Topic {topic_id} not found")
        raise HTTPException(status_code=404, detail="Topic not found")
    
    logger.info(f"[ADD_STAGE] Topic found - Professor ID: {db_topic.professor_id}, Category: {db_topic.category_id}")
    
    if db_topic.professor_id != current_user.id and not current_user.is_superuser:
        logger.warning(f"[ADD_STAGE] Unauthorized - User {current_user.id} tried to add stage to topic owned by {db_topic.professor_id}")
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Create stage with topic_id
    from app.models.stage import Stage
    try:
        stage_data = stage.model_dump()
        logger.debug(f"[ADD_STAGE] Original stage data keys: {stage_data.keys()}")
        
        stage_data['topic_id'] = topic_id
        stage_data['professor_id'] = current_user.id
        stage_data['category_id'] = db_topic.category_id  # Inherit from topic
        
        logger.debug(f"[ADD_STAGE] Final stage data: {stage_data}")
        
        db_stage = Stage(**stage_data)
        db.add(db_stage)
        db.commit()
        db.refresh(db_stage)
        
        logger.info(f"[ADD_STAGE] Stage {db_stage.id} created successfully for topic {topic_id}")
        return db_stage
    except Exception as e:
        db.rollback()
        logger.error(f"[ADD_STAGE] Error creating stage for topic {topic_id}: {type(e).__name__}: {str(e)}")
        logger.exception("Full traceback:")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating stage: {type(e).__name__}: {str(e)}"
        )

# =================== Student Endpoints ===================

@router.get("/categories/{category_id}/topics", response_model=List[topic_schemas.Topic])
async def get_category_topics(
    category_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """
    Get all approved topics for a specific category.
    Students only see approved topics.
    Admins see all topics in the category.
    """
    status_filter = "approved" if not current_user.is_superuser else None
    topics = crud_topic.get_topics_by_category(db, category_id, skip, limit, status=status_filter)
    return topics


@router.get("/categories/{category_id}/stages", response_model=List[stage_schemas.Stage])
async def get_category_stages(
    category_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """
    Get all stages for a specific category.
    Admins see everything, students see stages of approved topics.
    """
    from app.crud import crud_category
    # The CRUD function already filters by is_active=True
    # However, for students we should only show stages of approved topics
    if not current_user.is_superuser:
        topics = crud_topic.get_topics_by_category(db, category_id, status="approved")
        topic_ids = [t.id for t in topics]
        return db.query(Stage).filter(
            and_(Stage.topic_id.in_(topic_ids), Stage.is_active == True)
        ).order_by(Stage.topic_id, Stage.order).all()
        
    return crud_category.get_category_stages(db, category_id)

@router.get("/topics/{topic_id}/stages/progress", response_model=List[stage_schemas.StageWithProgress])
async def get_topic_stages_with_progress(
    topic_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """
    Get all stages for a topic with user progress information.
    Shows which stages are locked/unlocked and completed for the current user.
    
    The first stage (order=1) is always unlocked.
    Subsequent stages are locked until the previous stage is completed.
    """
    # Check if topic exists and is approved
    db_topic = crud_topic.get_topic(db, topic_id)
    if not db_topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    # Students can only access approved topics
    if not current_user.is_superuser and db_topic.professor_id != current_user.id:
        if db_topic.approval_status != "approved":
            raise HTTPException(status_code=404, detail="Topic not found")
    
    # Get all stages for the topic
    stages = crud_stage.get_stages_by_topic(db, topic_id)
    
    if not stages:
        return []
    
    # Initialize progress if user hasn't started this topic yet
    existing_progress = crud_stage.get_user_progress_by_topic(db, current_user.id, topic_id)
    if not existing_progress:
        crud_stage.initialize_user_progress_for_topic(db, current_user.id, topic_id)
    
    # Get user progress for all stages
    progress_map = {}
    user_progress = crud_stage.get_user_progress_by_topic(db, current_user.id, topic_id)
    for progress in user_progress:
        progress_map[progress.stage_id] = progress
    
    # Combine stage data with progress
    stages_with_progress = []
    for stage in stages:
        progress = progress_map.get(stage.id)
        stage_data = stage_schemas.StageWithProgress(
            id=stage.id,
            topic_id=stage.topic_id,
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


@router.get("/categories/{category_id}/stages/progress", response_model=List[stage_schemas.StageWithProgress])
async def get_category_stages_with_progress(
    category_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """
    Get all stages for all topics in a category with user progress information.
    Shows which stages are locked/unlocked and completed for the current user.
    """
    # Get all approved topics in the category
    topics = crud_topic.get_topics_by_category(db, category_id, status="approved")
    
    all_stages_with_progress = []
    
    for topic in topics:
        # Reusing the logic from get_topic_stages_with_progress
        stages = crud_stage.get_stages_by_topic(db, topic.id)
        if not stages:
            continue
            
        # Initialize progress if user hasn't started this topic yet
        existing_progress = crud_stage.get_user_progress_by_topic(db, current_user.id, topic.id)
        if not existing_progress:
            crud_stage.initialize_user_progress_for_topic(db, current_user.id, topic.id)
        
        # Get user progress for all stages in this topic
        progress_map = {}
        user_progress = crud_stage.get_user_progress_by_topic(db, current_user.id, topic.id)
        for progress in user_progress:
            progress_map[progress.stage_id] = progress
        
        # Combine stage data with progress for this topic
        for stage in stages:
            progress = progress_map.get(stage.id)
            stage_data = stage_schemas.StageWithProgress(
                id=stage.id,
                topic_id=stage.topic_id,
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
            all_stages_with_progress.append(stage_data)
    
    return all_stages_with_progress

# =================== Admin Endpoints ===================

@router.get("/topics/pending/review", response_model=List[topic_schemas.TopicWithStages])
async def get_pending_topics(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_superuser)
):
    """
    List all topics pending approval (Admin only).
    """
    topics = crud_topic.get_pending_topics(db, skip=skip, limit=limit)
    
    # Add professor names to the response
    result = []
    for topic in topics:
        topic_dict = topic_schemas.TopicWithStages.model_validate(topic).model_dump()
        topic_dict['professor_name'] = topic.professor.full_name if topic.professor else None
        result.append(topic_schemas.TopicWithStages(**topic_dict))
    
    return result

@router.post("/topics/{topic_id}/review", response_model=topic_schemas.Topic)
async def review_topic(
    topic_id: int,
    review: topic_schemas.TopicReview,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_superuser)
):
    """
    Approve or reject a topic (Admin only).
    When approved, all stages of the topic become visible to students.
    If rejected, it remains invisible and includes feedback comments.
    """
    review_status = "approved" if review.approved else "rejected"
    updated_topic = crud_topic.set_approval_status(
        db, topic_id, status=review_status, comment=review.comment
    )
    
    if not updated_topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found"
        )
        
    # TODO: Trigger notification to professor
    
    return updated_topic
