from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from app.models.category import Category
from app.models.topic import Topic
from app.models.stage import Stage, UserStageProgress
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryMetrics
from typing import List, Optional, Tuple
from difflib import SequenceMatcher

def get_category(db: Session, category_id: int):
    return db.query(Category).filter(Category.id == category_id).first()

def get_category_by_name(db: Session, name: str):
    return db.query(Category).filter(Category.name == name).first()


def calculate_similarity(str1: str, str2: str) -> float:
    """Calculate similarity between two strings (0-100)"""
    if not str1 or not str2:
        return 0.0
    return SequenceMatcher(None, str1.lower(), str2.lower()).ratio() * 100


def get_categories_enhanced(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    order_by: str = "name",
    order_direction: str = "asc",
    detect_duplicates: bool = False
) -> Tuple[List[dict], int]:
    """
    Get categories with advanced filtering and duplicate detection.
    
    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        search: Search term for name or description
        order_by: Field to order by (name, created_at, total_stages)
        order_direction: Order direction (asc, desc)
        detect_duplicates: Whether to calculate similarity scores
    
    Returns:
        Tuple of (list of category dicts with metadata, total count)
    """
    # Base query
    query = db.query(Category)
    
    # Apply search filter
    if search:
        search_filter = or_(
            Category.name.ilike(f"%{search}%"),
            Category.description.ilike(f"%{search}%")
        )
        query = query.filter(search_filter)
    
    # Get total count before pagination
    total_count = query.count()
    
    # Apply ordering
    order_column = Category.name  # default
    if order_by == "created_at":
        order_column = Category.created_at
    elif order_by == "name":
        order_column = Category.name
    
    if order_direction.lower() == "desc":
        query = query.order_by(order_column.desc())
    else:
        query = query.order_by(order_column.asc())
    
    # Apply pagination
    categories = query.offset(skip).limit(limit).all()
    
    # Build result with stage counts
    result = []
    all_category_names = [c.name for c in db.query(Category).all()] if detect_duplicates else []
    
    for category in categories:
        # Count stages
        stage_count = db.query(func.count(Stage.id)).join(Topic).filter(
            and_(Topic.category_id == category.id, Stage.is_active == True)
        ).scalar() or 0
        
        # Calculate similarity if duplicate detection is enabled
        similarity_score = None
        if detect_duplicates:
            # Find most similar category (excluding itself)
            max_similarity = 0.0
            for other_name in all_category_names:
                if other_name != category.name:
                    similarity = calculate_similarity(category.name, other_name)
                    if similarity > max_similarity:
                        max_similarity = similarity
            
            # Only report if similarity is significant (> 70%)
            similarity_score = max_similarity if max_similarity > 70 else None
        
        result.append({
            "id": category.id,
            "name": category.name,
            "description": category.description,
            "icon": category.icon,
            "created_at": category.created_at,
            "total_stages": stage_count,
            "similarity_score": similarity_score
        })
    
    return result, total_count


def get_categories(db: Session, skip: int = 0, limit: int = 100, name: str = None):
    query = db.query(Category)
    if name:
        query = query.filter(Category.name.ilike(f"%{name}%"))
    return query.offset(skip).limit(limit).all()

def create_category(db: Session, category: CategoryCreate):
    db_category = Category(
        name=category.name,
        description=category.description,
        icon=category.icon
    )
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

def update_category(db: Session, db_category: Category, category: CategoryUpdate):
    update_data = category.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_category, key, value)
    
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

def delete_category(db: Session, db_category: Category):
    db.delete(db_category)
    db.commit()
    return db_category


def get_category_metrics(db: Session, category_id: int) -> CategoryMetrics:
    """
    Calculate metrics for a specific category:
    - Total stages
    - Total unique students who accessed the category
    - Completion rate (% of students who completed all stages)
    - Average progress across all students
    """
    # Get total stages in category
    total_stages = db.query(func.count(Stage.id)).join(Topic).filter(
        and_(Topic.category_id == category_id, Stage.is_active == True)
    ).scalar() or 0
    
    if total_stages == 0:
        return CategoryMetrics(
            total_stages=0,
            total_students=0,
            completion_rate=0.0,
            average_progress=0.0
        )
    
    # Get all unique students who have progress in this category
    students_with_progress = db.query(
        UserStageProgress.user_id
    ).join(Stage).join(Topic).filter(
        Topic.category_id == category_id
    ).distinct().all()
    
    total_students = len(students_with_progress)
    
    if total_students == 0:
        return CategoryMetrics(
            total_stages=total_stages,
            total_students=0,
            completion_rate=0.0,
            average_progress=0.0
        )
    
    # Calculate completion rate and average progress
    students_completed = 0
    total_progress_sum = 0.0
    
    for (student_id,) in students_with_progress:
        # Get student's progress for all stages in this category
        student_progress = db.query(UserStageProgress).join(Stage).join(Topic).filter(
            and_(
                UserStageProgress.user_id == student_id,
                Topic.category_id == category_id,
                Stage.is_active == True
            )
        ).all()
        
        completed_stages = sum(1 for p in student_progress if p.is_completed)
        student_percentage = (completed_stages / total_stages) * 100 if total_stages > 0 else 0
        total_progress_sum += student_percentage
        
        # Check if student completed all stages
        if completed_stages == total_stages:
            students_completed += 1
    
    completion_rate = (students_completed / total_students) * 100 if total_students > 0 else 0.0
    average_progress = total_progress_sum / total_students if total_students > 0 else 0.0
    
    return CategoryMetrics(
        total_stages=total_stages,
        total_students=total_students,
        completion_rate=round(completion_rate, 2),
        average_progress=round(average_progress, 2)
    )


def get_category_stages(db: Session, category_id: int):
    """Get all stages for a category ordered by sequence"""
    return db.query(Stage).join(Topic).filter(
        and_(Topic.category_id == category_id, Stage.is_active == True)
    ).order_by(Topic.id, Stage.order).all()
