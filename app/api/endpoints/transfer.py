from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import crud, models, schemas
from app.api import deps
from app.crud import crud_transfer
from app.schemas.transfer import TransferRequest, TransferRequestCreate, NotificationBase

router = APIRouter()

@router.get("/search-colleagues", response_model=List[schemas.User])
def search_colleagues(
    q: str,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Search for other professors by email or name.
    """
    if not current_user.is_professor and not current_user.is_superuser:
         raise HTTPException(status_code=403, detail="Only professors can search for colleagues")
         
    users = db.query(models.User).filter(
        (models.User.email.ilike(f"%{q}%")) | (models.User.full_name.ilike(f"%{q}%")),
        models.User.id != current_user.id,
        models.User.is_professor == True # Only search for professors
    ).limit(10).all()
    return users

@router.post("/request", response_model=TransferRequest)
def initiate_transfer(
    request_in: TransferRequestCreate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Initiate a topic transfer to another professor.
    """
    if not current_user.is_professor and not current_user.is_superuser:
         raise HTTPException(status_code=403, detail="Only professors can initiate transfers")
         
    request = crud_transfer.create_transfer_request(db, current_user.id, request_in.receiver_email)
    if not request:
        raise HTTPException(status_code=404, detail="Receiver not found")
    return request

@router.get("/requests", response_model=List[TransferRequest])
def list_transfer_requests(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    List pending transfer requests for the current user.
    """
    return crud_transfer.get_received_transfer_requests(db, current_user.id)

@router.post("/requests/{request_id}/accept")
def accept_transfer(
    request_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Accept a transfer request.
    """
    success = crud_transfer.accept_transfer_request(db, request_id, current_user.id)
    if not success:
        raise HTTPException(status_code=400, detail="Invalid request or already processed")
    return {"msg": "Transfer accepted successfully"}

@router.post("/requests/{request_id}/reject")
def reject_transfer(
    request_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Reject a transfer request.
    """
    success = crud_transfer.reject_transfer_request(db, request_id, current_user.id)
    if not success:
        raise HTTPException(status_code=400, detail="Invalid request or already processed")
    return {"msg": "Transfer rejected"}

@router.get("/notifications", response_model=List[NotificationBase])
def get_notifications(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get notifications for the current user.
    """
    return crud_transfer.get_notifications(db, current_user.id, skip, limit)
