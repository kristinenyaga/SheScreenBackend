from pydantic import BaseModel, Field
from typing import Optional
from datetime import date


class SymptomLogCreate(BaseModel):
    symptom: str
    severity: Optional[int] = Field(None, ge=1, le=10)
    notes: Optional[str]


class SymptomLogOut(BaseModel):
    id: int
    date: date
    symptom: str
    severity: Optional[int]
    notes: Optional[str]

    class Config:
        orm_mode = True
