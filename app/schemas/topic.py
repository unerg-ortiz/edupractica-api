from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.schemas.stage import Stage

class TopicBase(BaseModel):
    title: str = Field(..., max_length=200)
    description: Optional[str] = None
    category_id: int

class TopicCreate(TopicBase):
    pass

class TopicUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[int] = None
    approval_status: Optional[str] = None
    approval_comment: Optional[str] = None
    is_active: Optional[bool] = None

class Topic(TopicBase):
    id: int
    professor_id: int
    professor_name: Optional[str] = None
    approval_status: str
    approval_comment: Optional[str]
    submitted_at: datetime
    is_active: bool
    is_archived: bool

    class Config:
        from_attributes = True

class TopicWithStages(Topic):
    stages: List[Stage]

class TopicReview(BaseModel):
    """Schema for approving or rejecting a topic"""
    approved: bool = Field(..., description="True to approve, False to reject")
    comment: Optional[str] = Field(None, description="Reason for rejection or feedback")
