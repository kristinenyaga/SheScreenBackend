from pydantic import BaseModel, EmailStr
from typing import Optional
from enum import Enum
from datetime import date


class UserRole(str, Enum):
    patient = "patient"
    staff = "staff"


class UserBase(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    email: EmailStr
    date_of_birth: date | None = None
    is_parent: bool = False  
    role: UserRole = UserRole.patient


class UserUpdate(BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]
    phone_number: Optional[str]
    date_of_birth: Optional[date]
    is_parent: Optional[bool]

class UserIn(BaseModel):
    email:EmailStr
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
    email: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str
