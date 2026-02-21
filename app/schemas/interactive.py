from pydantic import BaseModel, Field
from typing import List, Optional, Union, Dict, Any
from enum import Enum

class InteractiveType(str, Enum):
    MATCHING = "matching"
    CLASSIFICATION = "classification"
    ORDERING = "ordering"
    MULTIPLE_CHOICE = "multiple_choice"
    QUIZ = "quiz"

class QuizOption(BaseModel):
    id: str
    text: str
    isCorrect: bool

class QuizQuestion(BaseModel):
    id: str
    question: str
    options: List[QuizOption]

class QuizConfig(BaseModel):
    questions: List[QuizQuestion]

class ClassificationBucket(BaseModel):
    id: str
    name: str

class ClassificationItem(BaseModel):
    id: str
    content: str
    bucketId: str

class ClassificationConfig(BaseModel):
    buckets: List[ClassificationBucket]
    items: List[ClassificationItem]

class MatchingPair(BaseModel):
    id: str
    left: str
    right: str

class MatchingConfig(BaseModel):
    pairs: List[MatchingPair]

class OrderingItem(BaseModel):
    id: str
    text: str

class OrderingConfig(BaseModel):
    items: List[OrderingItem]

class InteractiveConfig(BaseModel):
    challengeType: InteractiveType
    # Fields to accommodate different game structures
    quiz: Optional[QuizConfig] = None
    classification: Optional[ClassificationConfig] = None
    matching: Optional[MatchingConfig] = None
    ordering: Optional[OrderingConfig] = None
    
    # Legacy/Flexible fields
    instructions: Optional[str] = None
    show_confetti: bool = True
    time_limit_seconds: Optional[int] = None
    
    class Config:
        from_attributes = True
        extra = "allow" # Allow extra fields for flexibility
