from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class CarePlanBase(BaseModel):
    user_id: int
    facility_id: int
    created_by: int
    hpv_result: Optional[str] = None
    pap_smear_result: Optional[str] = None
    recommended_action: Optional[str] = None
    screening_type: Optional[str] = None


class CarePlanCreate(CarePlanBase):
    pass


class CarePlanResponse(CarePlanBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
