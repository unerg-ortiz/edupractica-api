from typing import Optional
from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    token_type: str
    user_email: str
    user_role: str
    user_name: Optional[str] = None

class TokenPayload(BaseModel):
    sub: Optional[str] = None
