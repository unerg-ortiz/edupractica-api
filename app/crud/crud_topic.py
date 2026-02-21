from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_

from app.models.topic import Topic
from app.models.stage import Stage
from app.schemas.topic import TopicCreate, TopicUpdate


def get_topic(db: Session, topic_id: int) -> Optional[Topic]:
    return (
        db.query(Topic)
        .options(joinedload(Topic.professor))
        .filter(Topic.id == topic_id, Topic.is_active == True)
        .first()
    )


def get_topics_by_professor(
    db: Session, 
    professor_id: int, 
    skip: int = 0, 
    limit: int = 100
) -> List[Topic]:
    return (
        db.query(Topic)
        .filter(Topic.professor_id == professor_id, Topic.is_active == True)
        .order_by(Topic.submitted_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_topics_by_category(
    db: Session, 
    category_id: int, 
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = "approved"
) -> List[Topic]:
    """Get topics for a category, optionally filtered by approval status"""
    query = db.query(Topic).filter(Topic.category_id == category_id, Topic.is_active == True)
    if status:
        query = query.filter(Topic.approval_status == status)
    return (
        query.order_by(Topic.submitted_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_pending_topics(db: Session, skip: int = 0, limit: int = 100) -> List[Topic]:
    """Get all topics pending approval (Admin only)"""
    return (
        db.query(Topic)
        .options(joinedload(Topic.professor))
        .filter(Topic.approval_status == "pending", Topic.is_active == True)
        .order_by(Topic.submitted_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def set_approval_status(
    db: Session, 
    topic_id: int, 
    status: str, 
    comment: Optional[str] = None
) -> Optional[Topic]:
    """Approve or reject a topic (Admin only)"""
    db_topic = get_topic(db, topic_id)
    if not db_topic:
        return None
    
    db_topic.approval_status = status
    if comment:
        db_topic.approval_comment = comment
    
    db.commit()
    db.refresh(db_topic)
    return db_topic


def create_topic(db: Session, topic: TopicCreate, professor_id: int) -> Topic:
    db_topic = Topic(
        title=topic.title,
        description=topic.description,
        category_id=topic.category_id,
        professor_id=professor_id,
        approval_status="pending"
    )
    db.add(db_topic)
    db.commit()
    db.refresh(db_topic)
    return db_topic


def update_topic(db: Session, topic_id: int, topic_update: TopicUpdate) -> Optional[Topic]:
    db_topic = get_topic(db, topic_id)
    if not db_topic:
        return None
    
    update_data = topic_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_topic, field, value)
    
    db.commit()
    db.refresh(db_topic)
    return db_topic


def delete_topic(db: Session, topic_id: int) -> bool:
    db_topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if not db_topic:
        return False
    
    db_topic.is_active = False
    db.commit()
    return True
