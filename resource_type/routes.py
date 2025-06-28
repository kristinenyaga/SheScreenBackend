from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from users.db import get_db
from users import security
from resource_type import models, schemas
from typing import List
from sqlalchemy.exc import IntegrityError
from datetime import timedelta

router = APIRouter(prefix="/resource-type")


@router.post("/", response_model=schemas.ResourceTypeResponse)
def create_resource_type(resource: schemas.ResourceTypeCreate, db: Session = Depends(get_db)):
    existing = db.query(models.ResourceType).filter_by(name=resource.name).first()
    if existing:
        raise HTTPException(
            status_code=400, detail="Resource type already exists")

    new_resource = models.ResourceType(**resource.model_dump())
    db.add(new_resource)
    db.commit()
    db.refresh(new_resource)
    return new_resource


@router.get("/", response_model=list[schemas.ResourceTypeResponse])
def get_all_resource_types(db: Session = Depends(get_db)):
    return db.query(models.ResourceType).all()

@router.patch("/{resource_type_id}",response_model=schemas.ResourceTypeResponse)
def update_resource_type(resource_type_id: int, update_data: schemas.ResourceTypeUpdate, db: Session = Depends(get_db)):
    resource = db.query(models.ResourceType).get(resource_type_id)

    if not resource:
        raise HTTPException("Resource not found")
    
    for field,value in update_data().dict(exclude_unset=True).items():
        setattr(resource, field, value)
    
    db.commit()
    db.refresh(resource)
    return resource


@router.delete("/{resource_type_id}")
def delete_resource_type(resource_type_id:int,db:Session=Depends(get_db)):
    resource = db.query(models.ResourceType).get(resource_type_id)
    if not resource:
        raise HTTPException(status_code=404, detail="Resource type not found")

    db.delete(resource)
    db.commit()
    return {"message": "Resource type deleted successfully"}
