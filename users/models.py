from sqlalchemy import Column, Integer, String, Boolean, Date, Enum as SqlEnum, ForeignKey, ForeignKey
from sqlalchemy.orm import relationship
from users.db import Base
import enum

class UserRole(enum.Enum):
    PATIENT = "PATIENT"
    STAFF = "STAFF"

from users.db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(50), nullable=True)  
    last_name = Column(String(50), nullable=True)   
    phone_number = Column(String(20), unique=True, nullable=True)  
    email = Column(String(100), unique=True, index=True, nullable=False)  
    date_of_birth = Column(Date, nullable=True)  
    is_parent = Column(Boolean, default=False)
    role = Column(SqlEnum(UserRole), nullable=False, default=UserRole.PATIENT)
    hashed_password = Column(String(255))
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    
    care_plans = relationship("CarePlan", back_populates="user")
    risk_predictions = relationship("RiskPrediction", back_populates="user")


class RiskPrediction(Base):
    __tablename__ = "risk_predictions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Risk assessment input data
    number_of_sexual_partners = Column(Integer, nullable=False)
    first_sexual_intercourse_age = Column(Integer, nullable=False)
    smoking_status = Column(String(10), nullable=False)
    stds_history = Column(String(10), nullable=False)
    age_at_assessment = Column(Integer, nullable=False)
    
    # Prediction results
    cluster = Column(Integer, nullable=False)
    interpretation = Column(String(255), nullable=False)
    risk_level = Column(String(50), nullable=False)  # High, Medium, Low
    
    # Screening recommendations
    recommended_screenings = Column(String(500), nullable=True) 
    reason = Column(String(1000), nullable=True)
    urgency = Column(String(50), nullable=True)
    frequency = Column(String(200), nullable=True)
    additional_services = Column(String(500), nullable=True)
    
    created_at = Column(Date, nullable=False)
    
    user = relationship("User", back_populates="risk_predictions")


