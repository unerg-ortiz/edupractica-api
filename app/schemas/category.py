from pydantic import BaseModel, Field
from typing import Optional, List

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
    stages: List[StageSummary] = Field(default_factory=list, description="List of stages in this category")
    metrics: CategoryMetrics = Field(..., description="Analytics metrics for this category")
    
    class Config:
        from_attributes = True
