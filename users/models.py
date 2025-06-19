from sqlalchemy import Column, Integer, String, Boolean, Date, Enum as SqlEnum
from users.db import Base
import enum

class UserRole(enum.Enum):
    PATIENT = "patient"
    STAFF = "staff"

from users.db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(50), nullable=True)  
    last_name = Column(String(50), nullable=True)   
    phone_number = Column(String(20), unique=True,nullable=True)  
    email = Column(String(100), unique=True, index=True,nullable=False)  
    date_of_birth = Column(Date, nullable=True)  
    is_parent = Column(Boolean, default=False)
    role = Column(SqlEnum(UserRole), nullable=False, default=UserRole.PATIENT)
    hashed_password = Column(String(255))
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
