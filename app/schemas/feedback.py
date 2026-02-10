from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class FeedbackType(str, Enum):
    """Types of feedback that can be provided"""
    hint = "hint"
    encouragement = "encouragement"
    error_correction = "error_correction"


class MediaType(str, Enum):
    """Supported media types for feedback"""
    image = "image"
    audio = "audio"


# ============= Stage Feedback Schemas =============

class StageFeedbackBase(BaseModel):
    """Base schema for Stage Feedback"""
    stage_id: int = Field(..., description="ID of the stage this feedback belongs to")
    feedback_type: FeedbackType = Field(default=FeedbackType.hint, description="Type of feedback")
    sequence_order: int = Field(default=1, ge=1, description="Order in which this feedback is shown")
    max_hints_per_attempt: Optional[int] = Field(default=3, ge=1, le=10, description="Maximum hints per attempt")
    title: str = Field(..., min_length=1, max_length=200, description="Title of the feedback")
    text_content: Optional[str] = Field(None, description="Text content of the feedback")
    media_type: Optional[MediaType] = Field(None, description="Type of media (image/audio)")
    media_url: Optional[str] = Field(None, max_length=500, description="URL to media file")
    preview_settings: Optional[Dict[str, Any]] = Field(None, description="Responsive preview settings")
    is_active: bool = Field(default=True, description="Whether this feedback is active")


class StageFeedbackCreate(StageFeedbackBase):
    """Schema for creating a new stage feedback"""
    pass


class StageFeedbackUpdate(BaseModel):
    """Schema for updating an existing stage feedback"""
    feedback_type: Optional[FeedbackType] = None
    sequence_order: Optional[int] = Field(None, ge=1)
    max_hints_per_attempt: Optional[int] = Field(None, ge=1, le=10)
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    text_content: Optional[str] = None
    media_type: Optional[MediaType] = None
    media_url: Optional[str] = Field(None, max_length=500)
    preview_settings: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class StageFeedback(StageFeedbackBase):
    """Schema for returning stage feedback data"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class StageFeedbackWithUsage(StageFeedback):
    """Stage feedback with usage statistics"""
    times_viewed: int = Field(default=0, description="Number of times this feedback was viewed")
    avg_time_to_view: Optional[float] = Field(None, description="Average attempt number when viewed")


# ============= Student Attempt Schemas =============

class StudentAttemptBase(BaseModel):
    """Base schema for Student Attempt"""
    stage_id: int = Field(..., description="ID of the stage being attempted")
    is_successful: bool = Field(default=False, description="Whether the attempt was successful")
    error_details: Optional[Dict[str, Any]] = Field(None, description="Details about the error")
    time_spent_seconds: Optional[int] = Field(None, ge=0, description="Time spent on this attempt")


class StudentAttemptCreate(BaseModel):
    """Schema for creating a student attempt"""
    stage_id: int
    is_successful: bool = False
    error_details: Optional[Dict[str, Any]] = None
    time_spent_seconds: Optional[int] = None


class StudentAttemptUpdate(BaseModel):
    """Schema for updating a student attempt"""
    is_successful: Optional[bool] = None
    error_details: Optional[Dict[str, Any]] = None
    time_spent_seconds: Optional[int] = None


class StudentAttempt(BaseModel):
    """Schema for returning student attempt data"""
    id: int
    user_id: int
    stage_id: int
    attempt_number: int
    is_successful: bool
    hints_viewed: int
    error_details: Optional[Dict[str, Any]]
    time_spent_seconds: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


# ============= Feedback View Schemas =============

class StudentFeedbackViewCreate(BaseModel):
    """Schema for recording a feedback view"""
    attempt_id: int
    feedback_id: int


class StudentFeedbackView(BaseModel):
    """Schema for returning feedback view data"""
    id: int
    attempt_id: int
    feedback_id: int
    viewed_at: datetime

    class Config:
        from_attributes = True


# ============= Analytics Schemas =============

class StageAnalytics(BaseModel):
    """Schema for stage analytics data"""
    id: int
    stage_id: int
    total_attempts: int
    failed_attempts: int
    successful_attempts: int
    success_rate: float
    avg_hints_used: float
    max_hints_used: int
    most_common_errors: Optional[List[Dict[str, Any]]]
    avg_time_seconds: Optional[float]
    last_updated: datetime

    class Config:
        from_attributes = True


class StageAnalyticsSummary(BaseModel):
    """Simplified analytics summary for dashboards"""
    stage_id: int
    stage_title: str
    category_id: int
    total_attempts: int
    success_rate: float
    difficulty_score: float = Field(..., description="Calculated difficulty (0-100, higher = harder)")
    avg_hints_used: float
    needs_attention: bool = Field(..., description="True if success rate < 50%")


class CategoryAnalytics(BaseModel):
    """Analytics for an entire category"""
    category_id: int
    category_name: str
    total_students: int
    stages_analytics: List[StageAnalyticsSummary]
    overall_success_rate: float
    most_difficult_stage_id: Optional[int]


class FeedbackPreview(BaseModel):
    """Preview data for responsive testing"""
    feedback_id: int
    title: str
    text_content: Optional[str]
    media_type: Optional[MediaType]
    media_url: Optional[str]
    preview_settings: Optional[Dict[str, Any]]
    device_type: str = Field(..., description="mobile, tablet, desktop")


class HintRequest(BaseModel):
    """Request schema for getting hints during an attempt"""
    attempt_id: int
    requested_hint_number: int = Field(..., ge=1, description="Which hint number is being requested")


class HintResponse(BaseModel):
    """Response schema for hint requests"""
    feedback: StageFeedback
    hints_remaining: int = Field(..., description="Number of hints remaining for this attempt")
    max_hints: int = Field(..., description="Maximum hints allowed")
    can_request_more: bool = Field(..., description="Whether more hints can be requested")


class ErrorReport(BaseModel):
    """Common error pattern identified in analytics"""
    error_type: str
    frequency: int
    percentage: float
    sample_details: Optional[Dict[str, Any]]


class DifficultStagesReport(BaseModel):
    """Report of the most difficult stages across all categories"""
    stages: List[StageAnalyticsSummary]
    generated_at: datetime
