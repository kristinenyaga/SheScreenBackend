from pydantic import BaseModel

class UserProfile(BaseModel):
    first_name: str
    last_name: str
    phone_number: str
    date_of_birth: str
    is_parent: bool

class UserBase(BaseModel):
    firebase_uid: str
    email: str
    username: str

class UserOut(UserBase):
    first_name: str
    last_name: str
    phone_number: str
    date_of_birth: str
    is_parent: bool