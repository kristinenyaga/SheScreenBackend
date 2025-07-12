from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class RecommendationBase(BaseModel):
    patient_id: int
    risk_prediction_id: int
    urgency: str = "Medium"
    notes: Optional[str] = None
    final_recommendation: str
    is_override: bool = False


class RecommendationCreate(RecommendationBase):
    pass


class RecommendationOut(RecommendationBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True
