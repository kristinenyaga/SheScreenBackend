from fastapi import APIRouter, Depends,HTTPException,status
from sqlalchemy.orm import Session
from users.db import get_db
from facility_resources import models,schemas

router = APIRouter(prefix="/facility-resources")

@router.post("/",response_model=schemas.ResourceResponse)
def create_resource(resource:schemas.ResourceCreate,db:Session=Depends(get_db)):
  db_resource = models.FacilityResource(**resource.model_dump())
  db.add(db_resource)
  db.commit()
  db.refresh(db_resource)
  return db_resource

@router.get("/facility/{facility_id}",response_model=list[schemas.ResourceResponse])
def get_resources_by_facility(facility_id:int,db:Session=Depends(get_db)):
  return db.query(models.FacilityResource).filter(models.FacilityResource.facility_id == facility_id).all()

@router.patch("/{resource_id}",response_model=schemas.ResourceResponse)
def update_resource(resource_id:int,updates:schemas.ResourceUpdate,db:Session=Depends(get_db)):
  resource = db.query(models.FacilityResource).filter(models.FacilityResource.id == resource_id).first()
  if not resource:
    raise HTTPException(status_code=404,detail='FacilityResource not found')
  
  for key,value in updates.model_dump(exclude_unset=True).items():
    setattr(resource,key,value,)

  db.commit()
  db.refresh(resource)
  return resource


@router.delete("/{resource_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_resource(resource_id: int, db: Session = Depends(get_db)):
    resource = db.query(models.FacilityResource).filter(
        models.FacilityResource.id == resource_id).first()
    if not resource:
        raise HTTPException(status_code=404, detail="FacilityResource not found")

    db.delete(resource)
    db.commit()
    return None
