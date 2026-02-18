from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.transfer import TopicTransferRequest, Notification
from app.models.user import User
from app.models.stage import Stage

def create_transfer_request(db: Session, sender_id: int, receiver_email: str) -> Optional[TopicTransferRequest]:
    receiver = db.query(User).filter(User.email == receiver_email).first()
    if not receiver:
        return None
    
    # Create request
    db_request = TopicTransferRequest(
        sender_id=sender_id,
        receiver_id=receiver.id,
        status="pending"
    )
    db.add(db_request)
    db.flush() # Get ID

    # Send notification
    sender = db.query(User).filter(User.id == sender_id).first()
    notification = Notification(
        user_id=receiver.id,
        title="Solicitud de transferencia de temas",
        message=f"El profesor {sender.full_name or sender.email} quiere transferirte sus temas.",
        notification_type="TRANSFER_REQUEST",
        link=f"/transfer/requests/{db_request.id}"
    )
    db.add(notification)
    db.commit()
    db.refresh(db_request)
    return db_request

def get_transfer_request(db: Session, request_id: int) -> Optional[TopicTransferRequest]:
    return db.query(TopicTransferRequest).filter(TopicTransferRequest.id == request_id).first()

def get_received_transfer_requests(db: Session, user_id: int) -> List[TopicTransferRequest]:
    return db.query(TopicTransferRequest).filter(
        TopicTransferRequest.receiver_id == user_id, 
        TopicTransferRequest.status == "pending"
    ).all()

def accept_transfer_request(db: Session, request_id: int, user_id: int) -> bool:
    request = get_transfer_request(db, request_id)
    if not request or request.receiver_id != user_id or request.status != "pending":
        return False
    
    # Perform transfer
    db.query(Stage).filter(Stage.professor_id == request.sender_id).update(
        {Stage.professor_id: request.receiver_id}
    )
    
    # Update request status
    request.status = "accepted"
    request.completed_at = datetime.utcnow()
    
    # Notify sender
    receiver = db.query(User).filter(User.id == user_id).first()
    notification = Notification(
        user_id=request.sender_id,
        title="Transferencia aceptada",
        message=f"El profesor {receiver.full_name or receiver.email} ha aceptado tus temas.",
        notification_type="TRANSFER_ACCEPTED"
    )
    db.add(notification)
    
    db.commit()
    return True

def reject_transfer_request(db: Session, request_id: int, user_id: int) -> bool:
    request = get_transfer_request(db, request_id)
    if not request or request.receiver_id != user_id or request.status != "pending":
        return False
    
    request.status = "rejected"
    request.completed_at = datetime.utcnow()
    
    # Notify sender
    receiver = db.query(User).filter(User.id == user_id).first()
    notification = Notification(
        user_id=request.sender_id,
        title="Transferencia rechazada",
        message=f"El profesor {receiver.full_name or receiver.email} ha rechazado tus temas.",
        notification_type="TRANSFER_REJECTED"
    )
    db.add(notification)
    
    db.commit()
    return True

def get_notifications(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Notification]:
    return db.query(Notification).filter(Notification.user_id == user_id).order_by(Notification.created_at.desc()).offset(skip).limit(limit).all()

def mark_notification_as_read(db: Session, notification_id: int, user_id: int):
    notification = db.query(Notification).filter(Notification.id == notification_id, Notification.user_id == user_id).first()
    if notification:
        notification.is_read = True
        db.commit()
