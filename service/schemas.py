from pydantic import BaseModel
from typing import Optional
from enum import Enum


class ServiceCategory(str, Enum):
    screening = "screening"
    vaccination = "vaccination"
    treatment = "treatment"
    consultation = "consultation"


class CervicalCancerServiceCreate(BaseModel):
    name: str
    description: Optional[str] = None
    category: ServiceCategory


class CervicalCancerServiceResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    category: ServiceCategory

    class Config:
        from_attributes = True
