from pydantic import BaseModel, EmailStr
from datetime import date, datetime
from typing import Optional


class RecommendationBase(BaseModel):
    patient_id: int
    risk_prediction_id: int
    urgency: str = "Medium"
    notes: Optional[str] = None
    is_override: bool = False
    status: str = "awaiting_test_results"

    test_recommendations: Optional[str] = None
    non_test_recommendations: Optional[str] = None
    additional_services: Optional[str] = None
    ai_recommendation: Optional[str] = None
    referral: Optional[str] = None


class RecommendationCreate(RecommendationBase):
    pass


class Patient(BaseModel):
    first_name: str
    last_name: str
    patient_code:str

class RecommendationOut(RecommendationBase):
    id: int
    created_at: datetime
    patient:Patient

    class Config:
        orm_mode = True
