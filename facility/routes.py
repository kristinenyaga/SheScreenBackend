from facility import models,schemas
from users.db import get_db
from fastapi  import Depends,APIRouter,HTTPException
from sqlalchemy.orm import Session


router = APIRouter(prefix="/facilities")

@router.post("/",response_model=schemas.FacilityResponse)
def create_facility(facility:schemas.FacilityCreate,db: Session =Depends(get_db)):
    db_facility = db.query(models.Facility).filter(
        models.Facility.name == facility.name).first()
    if db_facility:
        raise HTTPException(status_code=400, detail="Facility already registered")
    
    db_facility = models.Facility(**facility.dict())
    db.add(db_facility)
    db.commit()
    db.refresh(db_facility)
    return db_facility

@router.get("/",response_model = list[schemas.FacilityResponse])
def get_facilities(db: Session = Depends(get_db)):
  return db.query(models.Facility).all()
