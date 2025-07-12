from sqlalchemy import Column, Integer, String, Boolean, Date, Enum as SqlEnum
from sqlalchemy.orm import relationship
from users.db import Base
import enum


class UserRole(enum.Enum):
    ADMIN = "ADMIN"
    DOCTOR = "DOCTOR"
    NURSE = "NURSE"
    LAB_TECHNICIAN = "LAB_TECHNICIAN"
    RECEPTIONIST = "RECEPTIONIST"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    phone_number = Column(String(20), unique=True, nullable=True)
    email = Column(String(100), unique=True, index=True, nullable=False)
    date_of_birth = Column(Date, nullable=True)
    role = Column(SqlEnum(UserRole), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    

    patients = relationship("Patient", back_populates="created_by")
    created_care_plans = relationship("CarePlan", back_populates="creator")
    sent_messages = relationship("Message", back_populates="sender_user")


