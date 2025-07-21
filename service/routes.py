from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from users.db import get_db
from users import security
from service import models, schemas
from typing import List
from sqlalchemy.exc import IntegrityError
from datetime import timedelta

router = APIRouter(prefix="/services")


@router.post("/",response_model=schemas.CervicalCancerServiceResponse)
def create_cervical_cancer_services(service_data: schemas.CervicalCancerServiceCreate, db: Session = Depends(get_db)):
  existing = db.query(models.CervicalCancerService).filter(models.CervicalCancerService.name == service_data.name)

  if existing:
    raise HTTPException("Service with the provided name already exists")
  
  service = models.CervicalCancerService(**service_data.model_dump())
  db.add(service)
  db.commit()
  db.refresh(service)
  return service


@router.get("/", response_model=list[schemas.CervicalCancerServiceResponse])
def get_all_cervical_cancer_services(db:Session=Depends(get_db)):
  return db.query(models.CervicalCancerService).all()


@router.get("/by-name/{service_name}", response_model=schemas.CervicalCancerServiceResponse)
def get_service_by_name(service_name: str, db: Session = Depends(get_db)):
    service = db.query(models.CervicalCancerService).filter(
        models.CervicalCancerService.name == service_name).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    return service
