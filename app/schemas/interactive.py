from pydantic import BaseModel, Field
from typing import List, Optional, Union, Dict, Any
from enum import Enum

class InteractiveType(str, Enum):
    MATCHING = "matching"
    CLASSIFICATION = "classification"
    ORDERING = "ordering"
    MULTIPLE_CHOICE = "multiple_choice"

class ElementType(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"

class ChallengeElement(BaseModel):
    id: str
    type: ElementType
    content: str  # Text string or URL for image/audio
    media_url: Optional[str] = None
    label: Optional[str] = None

class MatchingPair(BaseModel):
    left_id: str
    right_id: str

class ClassificationCategory(BaseModel):
    id: str
    title: str
    correct_element_ids: List[str]

class InteractiveConfig(BaseModel):
    challenge_type: InteractiveType = Field(..., description="Type of interactive game")
    instructions: str = Field(..., description="Professor instructions for the student")
    
    # Common elements used in the challenge
    elements: List[ChallengeElement] = Field(..., description="Library of available items (cards, images, etc.)")
    
    # Config specific to challenge type
    matching_pairs: Optional[List[MatchingPair]] = None
    classification_categories: Optional[List[ClassificationCategory]] = None
    correct_order: Optional[List[str]] = None  # List of element IDs in order
    
    # UI/UX Settings
    show_confetti: bool = Field(True, description="Whether to show animations on success")
    time_limit_seconds: Optional[int] = None
    
    class Config:
        from_attributes = True
