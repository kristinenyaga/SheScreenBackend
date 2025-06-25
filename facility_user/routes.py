from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from users.db import get_db
from users import security
from facility_user import models,schemas
from typing import List

router = APIRouter(prefix="/facility-users")


@router.post("/", response_model=schemas.FacilityUserResponse)
def create_facility_user(user: schemas.FacilityUserCreate, db: Session = Depends(get_db)):
    hashed_pw = security.get_password_hash(user.hashed_password)
    db_user = models.FacilityUser(
        first_name=user.first_name,
        last_name=user.last_name,
        phone_number=user.phone_number,
        email=user.email,
        hashed_password=hashed_pw,
        role=user.role,
        facility_id=user.facility_id,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.get("/", response_model=List[schemas.FacilityUserResponse])
def get_all_users(db: Session = Depends(get_db)):
    return db.query(models.FacilityUser).all()
