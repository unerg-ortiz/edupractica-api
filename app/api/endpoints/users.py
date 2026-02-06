from typing import Any, List

from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps

router = APIRouter()

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
