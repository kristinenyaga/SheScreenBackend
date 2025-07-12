from typing import Optional
from pydantic import BaseModel
from datetime import date

class PatientOut(BaseModel):
    id: int
    first_name: str
    last_name: str
    date_of_birth: Optional[date]
    area_of_residence: Optional[str]

    class Config:
        orm_mode = True

class PatientProfileBase(BaseModel):
    is_sexually_active: Optional[str]
    number_of_sexual_partners: Optional[int]
    first_sexual_intercourse_age: Optional[int]
    smoking_status: Optional[str]
    stds_history: Optional[str]
    hpv_result: Optional[str]
    immune_compromised: Optional[str]
    immune_condition_detail: Optional[str]
    contraceptive_using: Optional[str]
    contraceptive_use_years: Optional[int]
    hpv_vaccinated: Optional[str]
    has_children: Optional[str]
    children_count: Optional[int]
    first_pregnancy_age: Optional[str]
    family_history: Optional[str]
    patient: PatientOut

    class Config:
        orm_mode = True


class PatientProfileCreate(PatientProfileBase):
    patient_id: int


class PatientProfileUpdate(PatientProfileBase):
    pass


class PatientProfileResponse(PatientProfileBase):
    id: int
    patient_id: int
