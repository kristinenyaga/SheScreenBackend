from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from users.db import get_db
from users import security
from service_resource_requirement import models, schemas
from typing import List
from sqlalchemy.exc import IntegrityError
from datetime import timedelta

router = APIRouter(prefix="/service-resource-requirements")


@router.get("/service/{service_id}", response_model=List[schemas.ServiceResourceRequirementResponse])
def get_requirements_by_service(service_id: int, db: Session = Depends(get_db)):
    requirements = db.query(models.ServiceResourceRequirement).filter(
        models.ServiceResourceRequirement.service_id == service_id
    ).all()

    if not requirements:
        raise HTTPException(
            status_code=404, detail="No resource requirements found for this service.")

    return requirements

@router.get("/", response_model=list[schemas.ServiceResourceRequirementResponse])
def get_detailed_requirements(db: Session = Depends(get_db)):
    return db.query(models.ServiceResourceRequirement).all()
