from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date


class UserBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: Optional[str]
    date_of_birth: Optional[date]


class UserCreate(UserBase):
    password: str
    role: str  # Must match UserRole enum values (e.g., DOCTOR)


class UserUpdate(BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]
    phone_number: Optional[str]
    date_of_birth: Optional[date]


class UserOut(UserBase):
    id: int
    role: str
    is_active: bool
    is_verified: bool

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None
