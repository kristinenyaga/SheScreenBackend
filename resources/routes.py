from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from users.db import get_db
from resources import models, schemas
from users import auth
from users.models import User
import httpx

router = APIRouter(prefix="/resources", tags=["Resources"])

SMS_API_URL = "https://sms.textsms.co.ke/api/services/sendsms/"
SMS_API_KEY = "5075367cbe1a8d1284c158b4975615fb"
SMS_PARTNER_ID = "13831"
SMS_SENDER_ID = "TextSMS"


def send_low_stock_sms(resource_name: str, quantity: int, phone: str):
    message = (
        f"ALERT: Resource '{resource_name}' is low in stock.\n"
        f"Remaining quantity: {quantity}.\n"
        "Please restock as soon as possible."
    )
    sms_payload = {
        "apikey": SMS_API_KEY,
        "partnerID": SMS_PARTNER_ID,
        "message": message,
        "shortcode": SMS_SENDER_ID,
        "mobile": phone,
    }
    try:
        response = httpx.post(SMS_API_URL, json=sms_payload)
        response.raise_for_status()
    except httpx.HTTPError as e:
        print(f"Failed to send SMS: {str(e)}")


@router.post("/", response_model=schemas.ResourceOut)
def create_resource(resource: schemas.ResourceCreate, db: Session = Depends(get_db)):
    existing = db.query(models.Resource).filter(
        models.Resource.name == resource.name).first()
    if existing:
        raise HTTPException(
            status_code=400, detail="Resource with that name already exists")
    db_resource = models.Resource(**resource.dict())
    db.add(db_resource)
    db.commit()
    db.refresh(db_resource)
    return db_resource


@router.get("/", response_model=List[schemas.ResourceOut])
def get_all_resources(db: Session = Depends(get_db)):
    return db.query(models.Resource).all()


@router.get("/{resource_id}", response_model=schemas.ResourceOut)
def get_resource(resource_id: int, db: Session = Depends(get_db)):
    resource = db.query(models.Resource).filter(
        models.Resource.id == resource_id).first()
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    return resource


@router.put("/{resource_id}", response_model=schemas.ResourceOut)
def update_resource(
    resource_id: int,
    updated: schemas.ResourceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_user),
):
    resource = db.query(models.Resource).filter(
        models.Resource.id == resource_id).first()
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")

    for field, value in updated.dict(exclude_unset=True).items():
        setattr(resource, field, value)

    db.commit()
    db.refresh(resource)

    if resource.quantity_available <= resource.low_stock_threshold:
        if current_user.phone_number:
            send_low_stock_sms(
                resource.name, resource.quantity_available, current_user.phone_number)

    return resource


@router.delete("/{resource_id}")
def delete_resource(resource_id: int, db: Session = Depends(get_db)):
    resource = db.query(models.Resource).filter(
        models.Resource.id == resource_id).first()
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    db.delete(resource)
    db.commit()
    return {"detail": "Resource deleted successfully"}
