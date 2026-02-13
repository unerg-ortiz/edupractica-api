from pydantic import BaseModel, Field
from typing import Optional

class StageBase(BaseModel):
    """Base schema for Stage"""
    category_id: int = Field(..., description="ID of the category this stage belongs to")
    order: int = Field(..., ge=1, description="Sequential order of the stage (1, 2, 3...)")
    title: str = Field(..., max_length=100, description="Title of the stage")
    description: Optional[str] = Field(None, description="Description of the stage")
    content: Optional[str] = Field(None, description="Educational content for this stage")
    challenge_description: Optional[str] = Field(None, description="Challenge to complete this stage")
    media_url: Optional[str] = Field(None, description="URL or path to the media file")
    media_type: Optional[str] = Field(None, description="Type of media ('video', 'audio', 'image')")
    media_filename: Optional[str] = Field(None, description="Original filename of the media")
    is_active: bool = Field(True, description="Whether this stage is active")

class StageCreate(StageBase):
    """Schema for creating a new stage"""
    pass

class StageUpdate(BaseModel):
    """Schema for updating an existing stage"""
    category_id: Optional[int] = None
    order: Optional[int] = Field(None, ge=1)
    title: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    content: Optional[str] = None
    challenge_description: Optional[str] = None
    is_active: Optional[bool] = None

class Stage(StageBase):
    """Schema for returning stage data"""
    id: int

    class Config:
        from_attributes = True


class UserStageProgressBase(BaseModel):
    """Base schema for UserStageProgress"""
    user_id: int
    stage_id: int
    is_completed: bool = False
    is_unlocked: bool = False

class UserStageProgressCreate(BaseModel):
    """Schema for creating user stage progress"""
    stage_id: int

class UserStageProgressUpdate(BaseModel):
    """Schema for updating user stage progress"""
    is_completed: Optional[bool] = None
    is_unlocked: Optional[bool] = None

class UserStageProgress(UserStageProgressBase):
    """Schema for returning user stage progress"""
    id: int

    class Config:
        from_attributes = True


class StageWithProgress(BaseModel):
    """
    Schema for returning a stage with user progress information.
    Shows whether the stage is locked/unlocked and completed.
    """
    id: int
    category_id: int
    order: int
    title: str
    description: Optional[str]
    content: Optional[str]
    challenge_description: Optional[str]
    media_url: Optional[str]
    media_type: Optional[str]
    media_filename: Optional[str]
    is_active: bool
    is_unlocked: bool = Field(..., description="Whether this stage is unlocked for the user")
    is_completed: bool = Field(..., description="Whether the user has completed this stage")

    class Config:
        from_attributes = True
