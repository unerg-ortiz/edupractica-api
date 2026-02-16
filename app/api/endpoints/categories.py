from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.session import get_db
from app.schemas.category import Category, CategoryCreate, CategoryUpdate, CategoryDetail, StageSummary
from app.crud import crud_category
from app.api import deps
from app.models.user import User

router = APIRouter()

@router.post("/", response_model=Category)
def create_category(
    category: CategoryCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_superuser)
):
    db_category = crud_category.get_category_by_name(db, name=category.name)
    if db_category:
        raise HTTPException(status_code=400, detail="Category already exists")
    return crud_category.create_category(db=db, category=category)

@router.get("/", response_model=List[Category])
def read_categories(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """
    Get all categories (simple list).
    For advanced filtering, use /categories/list endpoint.
    """
    categories = crud_category.get_categories(db, skip=skip, limit=limit)
    return categories


@router.get("/list")
def list_categories_enhanced(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of records to return"),
    search: Optional[str] = Query(None, description="Search by name or description"),
    order_by: str = Query("name", pattern="^(name|created_at)$", description="Field to order by"),
    order_direction: str = Query("asc", pattern="^(asc|desc)$", description="Order direction"),
    detect_duplicates: bool = Query(False, description="Enable duplicate detection"),
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_superuser)
):
    """
    Get enhanced category list with advanced features (Admin only).
    
    Features:
    - **Pagination**: Use skip and limit parameters
    - **Search**: Filter by name or description
    - **Ordering**: Sort by name or created_at (asc/desc)
    - **Duplicate Detection**: Highlights similar category names (>70% similarity)
    
    Response includes:
    - Total count of matching categories
    - List of categories with stage counts
    - Similarity scores when duplicate detection is enabled
    
    Example:
    ```
    GET /categories/list?search=python&order_by=created_at&order_direction=desc&detect_duplicates=true
    ```
    """
    from app.schemas.category import CategoryList
    
    categories, total_count = crud_category.get_categories_enhanced(
        db=db,
        skip=skip,
        limit=limit,
        search=search,
        order_by=order_by,
        order_direction=order_direction,
        detect_duplicates=detect_duplicates
    )
    
    return {
        "total": total_count,
        "skip": skip,
        "limit": limit,
        "items": categories
    }

@router.get("/{category_id}", response_model=Category)
def read_category(
    category_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    db_category = crud_category.get_category(db, category_id=category_id)
    if db_category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return db_category


@router.get("/{category_id}/detail", response_model=CategoryDetail)
def read_category_detail(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_superuser)
):
    """
    Get detailed information about a category including:
    - Basic category info (name, description, icon)
    - List of all stages (topics) in the category
    - Metrics: total stages, total students, completion rate, average progress
    
    This endpoint is designed for administrators to review category information
    before making changes.
    """
    db_category = crud_category.get_category(db, category_id=category_id)
    if db_category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # Get stages for this category
    stages = crud_category.get_category_stages(db, category_id)
    stages_summary = [
        StageSummary(
            id=stage.id,
            order=stage.order,
            title=stage.title,
            description=stage.description,
            is_active=stage.is_active,
            media_type=stage.media_type
        )
        for stage in stages
    ]
    
    # Get metrics
    metrics = crud_category.get_category_metrics(db, category_id)
    
    # Build detailed response
    return CategoryDetail(
        id=db_category.id,
        name=db_category.name,
        description=db_category.description,
        icon=db_category.icon,
        created_at=db_category.created_at,
        stages=stages_summary,
        metrics=metrics
    )


@router.put("/{category_id}", response_model=Category)
def update_category(
    category_id: int, 
    category: CategoryUpdate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_superuser)
):
    db_category = crud_category.get_category(db, category_id=category_id)
    if db_category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    
    if category.name:
        existing_category = crud_category.get_category_by_name(db, name=category.name)
        if existing_category and existing_category.id != category_id:
             raise HTTPException(status_code=400, detail="Category name already exists")
             
    return crud_category.update_category(db=db, db_category=db_category, category=category)

@router.delete("/{category_id}", response_model=Category)
def delete_category(
    category_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_superuser)
):
    db_category = crud_category.get_category(db, category_id=category_id)
    if db_category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return crud_category.delete_category(db=db, db_category=db_category)


@router.get("/{category_id}/students", response_model=List[dict])
def get_category_students(
    category_id: int,
    search: Optional[str] = Query(None, description="Search students by name or email"),
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_superuser)
):
    """
    Get list of students who have accessed this category.
    Supports search by name or email.
    
    Returns student info with their progress in this category.
    """
    from app.models.user import User
    from app.models.stage import Stage, UserStageProgress
    from sqlalchemy import and_, or_
    
    # Verify category exists
    db_category = crud_category.get_category(db, category_id=category_id)
    if db_category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # Get unique students who have progress in this category
    query = db.query(User).join(
        UserStageProgress, UserStageProgress.user_id == User.id
    ).join(
        Stage, Stage.id == UserStageProgress.stage_id
    ).filter(
        Stage.category_id == category_id
    ).distinct()
    
    # Apply search filter if provided
    if search:
        query = query.filter(
            or_(
                User.email.ilike(f"%{search}%"),
                User.full_name.ilike(f"%{search}%")
            )
        )
    
    students = query.all()
    
    # Calculate progress for each student
    result = []
    total_stages = crud_category.get_category_metrics(db, category_id).total_stages
    
    for student in students:
        # Get student's completed stages in this category
        completed = db.query(UserStageProgress).join(Stage).filter(
            and_(
                UserStageProgress.user_id == student.id,
                Stage.category_id == category_id,
                UserStageProgress.is_completed == True
            )
        ).count()
        
        progress_percentage = (completed / total_stages * 100) if total_stages > 0 else 0
        
        result.append({
            "id": student.id,
            "email": student.email,
            "full_name": student.full_name,
            "completed_stages": completed,
            "total_stages": total_stages,
            "progress_percentage": round(progress_percentage, 2)
        })
    
    return result
