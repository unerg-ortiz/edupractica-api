from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, EmailStr

class TransferRequestCreate(BaseModel):
    receiver_email: EmailStr

class TransferRequest(BaseModel):
    id: int
    sender_id: int
    receiver_id: int
    status: str
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class NotificationBase(BaseModel):
    id: int
    title: str
    message: str
    is_read: bool
    notification_type: str
    link: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
