from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from users.db import get_db
from users import security
from facility_user import models,schemas
from typing import List
from sqlalchemy.exc import IntegrityError
from datetime import timedelta

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
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="Phone number or email already in use")
    

@router.post("/login",response_model=schemas.TokenResponse)
async def facility_user_login(login_data:schemas.LoginRequest,db:Session=Depends(get_db)):
    user = db.query(models.FacilityUser).filter(models.FacilityUser.email==login_data.email).first()
    if not user or not security.pwd_context.verify(login_data.hashed_password, user.hashed_password):
        raise HTTPException(
            status_code=401, detail="Invalid email or password")
    access_token_expires = timedelta(
            minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/", response_model=List[schemas.FacilityUserResponse])
def get_all_users(db: Session = Depends(get_db)):
    return db.query(models.FacilityUser).all()

