from sqlalchemy.orm import Session
from pydantic import EmailStr
from typing import Any, List, Optional

from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps

router = APIRouter()

@router.get("/me", response_model=schemas.User)
def read_user_me(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get current user.
    """
    return current_user

@router.put("/me", response_model=schemas.User)
def update_user_me(
    *,
    db: Session = Depends(deps.get_db),
    password: Optional[str] = Body(None),
    full_name: Optional[str] = Body(None),
    email: Optional[EmailStr] = Body(None),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update own user.
    """
    current_user_data = jsonable_encoder(current_user)
    user_in = schemas.UserUpdate(**current_user_data)
    if password is not None:
        user_in.password = password
    if full_name is not None:
        user_in.full_name = full_name
    if email is not None:
        user_in.email = email
    user = crud.user.update(db, db_obj=current_user, obj_in=user_in)
    return user

@router.delete("/me", response_model=schemas.User)
def delete_me(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete own user profile and all associated data.
    """
    crud.user.remove_completely(db, user_id=current_user.id)
    return current_user

@router.get("/students", response_model=List[schemas.User])
def read_students(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve students. Accessible by active users (professors).
    """
    # For now, all active users can see students. 
    # Logic could be hardened to only allow professors/admins.
    students = crud.user.get_students(db, skip=skip, limit=limit)
    return students

@router.get("/", response_model=List[schemas.User])
def read_users(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_superuser),
) -> Any:
    """
    Retrieve users.
    """
    users = crud.user.get_multi(db, skip=skip, limit=limit)
    return users

@router.post("/signup", response_model=schemas.User)
def signup(
    *,
    db: Session = Depends(deps.get_db),
    user_in: schemas.UserCreate,
) -> Any:
    """
    Public signup endpoint for new users.
    """
    user = crud.user.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system",
        )
    # Ensure superuser flag cannot be set via public signup
    user_in.is_superuser = False
    
    # Prevent admin role creation via public signup
    if user_in.role == "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin role cannot be assigned through public signup",
        )
    
    # Restrict to allowed roles only
    allowed_roles = ["student", "professor"]
    if user_in.role not in allowed_roles:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid role. Allowed roles: {', '.join(allowed_roles)}",
        )
    
    user = crud.user.create(db, obj_in=user_in)
    return user

@router.post("/", response_model=schemas.User)
def create_user(
    *,
    db: Session = Depends(deps.get_db),
    user_in: schemas.UserCreate,
    current_user: models.User = Depends(deps.get_current_superuser),
) -> Any:
    """
    Create new user.
    """
    user = crud.user.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system",
        )
    user = crud.user.create(db, obj_in=user_in)
    return user

@router.post("/{user_id}/block", response_model=schemas.User)
def block_user(
    *,
    db: Session = Depends(deps.get_db),
    user_id: int,
    block_request: schemas.BlockUserRequest,
    current_user: models.User = Depends(deps.get_current_superuser),
) -> Any:
    """
    Block a user.
    """
    user = crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )
    if user.is_superuser:
        raise HTTPException(
             status_code=400,
             detail="Cannot block a superuser"
        )
        
    user = crud.user.block_user(db, db_obj=user, reason=block_request.reason, admin_id=current_user.id)
    return user

@router.post("/me/deactivate", response_model=schemas.User)
def deactivate_me(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Deactivate own account and archive topics if professor.
    """
    if current_user.is_superuser:
        raise HTTPException(
            status_code=400,
            detail="Superusers cannot deactivate themselves via this endpoint"
        )
    
    # Archive topics if professor
    if current_user.is_professor:
        db.query(models.Stage).filter(models.Stage.professor_id == current_user.id).update(
            {models.Stage.is_archived: True}
        )
    
    current_user.is_active = False
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    
    # Audit log
    crud.user.block_user(db, db_obj=current_user, reason="Self-deactivation", admin_id=current_user.id)
    
    return current_user

@router.delete("/{user_id}", response_model=schemas.User)
def delete_user(
    *,
    db: Session = Depends(deps.get_db),
    user_id: int,
    current_user: models.User = Depends(deps.get_current_superuser),
) -> Any:
    """
    Delete a user.
    """
    user = crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )
    if user.is_superuser:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete a superuser",
        )
    if user.id == current_user.id:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete yourself",
        )
    
    deleted_user = crud.user.delete(db, id=user_id, admin_id=current_user.id)
    return deleted_user

