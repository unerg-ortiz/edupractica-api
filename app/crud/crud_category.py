from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from app.models.category import Category
from app.models.stage import Stage, UserStageProgress
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryMetrics

def get_category(db: Session, category_id: int):
    return db.query(Category).filter(Category.id == category_id).first()

def get_category_by_name(db: Session, name: str):
    return db.query(Category).filter(Category.name == name).first()

def get_categories(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Category).offset(skip).limit(limit).all()

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
    total_stages = db.query(func.count(Stage.id)).filter(
        and_(Stage.category_id == category_id, Stage.is_active == True)
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
    ).join(Stage).filter(
        Stage.category_id == category_id
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
        student_progress = db.query(UserStageProgress).join(Stage).filter(
            and_(
                UserStageProgress.user_id == student_id,
                Stage.category_id == category_id,
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
    return db.query(Stage).filter(
        and_(Stage.category_id == category_id, Stage.is_active == True)
    ).order_by(Stage.order).all()
