from pydantic import BaseModel
from typing import Optional
from enum import Enum

class UserBase(BaseModel):
    username: str
    email: str

class UserIn(UserBase):
    password: str

class UserInDBBase(UserBase):
    id: int
    # is_active: bool = True
    # is_superuser: bool = False
    # is_verified: bool = False

    class Config:
        from_attributes = True

class UserInDB(UserInDBBase):
    hashed_password: str

class TokenData(BaseModel):
    username: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str
