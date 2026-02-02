from pydantic import BaseModel, Field
from typing import Optional

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
