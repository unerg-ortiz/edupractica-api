from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class CategoryBase(BaseModel):
    name: str = Field(..., max_length=50, description="Name of the category")
    description: Optional[str] = None
    icon: Optional[str] = None

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(CategoryBase):
    name: Optional[str] = Field(None, max_length=50)

class Category(CategoryBase):
    id: int
    created_at: datetime = Field(..., description="Timestamp when category was created")

    class Config:
        from_attributes = True


# Schema for category list with additional info
class CategoryList(CategoryBase):
    id: int
    created_at: datetime
    total_stages: int = Field(0, description="Number of stages in this category")
    similarity_score: Optional[float] = Field(None, description="Similarity score for duplicate detection (0-100)")
    
    class Config:
        from_attributes = True


# Schema for stage summary in category detail
class StageSummary(BaseModel):
    id: int
    order: int
    title: str
    description: Optional[str]
    is_active: bool
    media_type: Optional[str] = None
    
    class Config:
        from_attributes = True


# Schema for category metrics
class CategoryMetrics(BaseModel):
    total_stages: int = Field(..., description="Total number of stages in this category")
    total_students: int = Field(..., description="Number of unique students who have accessed this category")
    completion_rate: float = Field(..., description="Percentage of students who completed all stages (0-100)")
    average_progress: float = Field(..., description="Average completion percentage across all students (0-100)")


# Detailed category view with stages and metrics
class CategoryDetail(CategoryBase):
    id: int
    created_at: datetime
    stages: List[StageSummary] = Field(default_factory=list, description="List of stages in this category")
    metrics: CategoryMetrics = Field(..., description="Analytics metrics for this category")
    
    class Config:
        from_attributes = True
