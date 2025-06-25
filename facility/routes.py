from facility import models,schemas
from users.db import get_db
from fastapi  import Depends,APIRouter
from sqlalchemy.orm import Session


router = APIRouter(prefix="/facilities")

@router.post("/",response_model=schemas.FacilityResponse)
def create_facility(facility:schemas.FacilityCreate,db: Session =Depends(get_db)):
    db_facility = models.Facility(**facility.dict())
    db.add(db_facility)
    db.commit()
    db.refresh(db_facility)
    return db_facility

@router.get("/",response_model = list[schemas.FacilityResponse])
def get_facility(db: Session = Depends(get_db)):
  return db.query(models.Facility).all()
