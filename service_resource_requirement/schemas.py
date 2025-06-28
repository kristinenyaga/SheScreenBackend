from pydantic import BaseModel
from typing import Optional


class ServiceResourceRequirementResponse(BaseModel):
    id: int
    service_id: int
    resource_type_id: int
    required_quantity: int

    class Config:
        orm_mode = True
