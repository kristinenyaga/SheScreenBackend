from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from messages import models as messages_models
from users.db import get_db
from users.auth import get_current_user
from messages.schemas import MessageCreate, MessageOut
from users import models as users_models
import httpx

router = APIRouter()

SMS_API_URL = "https://sms.textsms.co.ke/api/services/sendsms/"
SMS_API_KEY = "5075367cbe1a8d1284c158b4975615fb"
SMS_PARTNER_ID = "13831"
SMS_SENDER_ID = "TextSMS"

@router.post("/send", response_model=MessageOut)
def send_message(
    message: MessageCreate,
    db: Session = Depends(get_db),
    current_user: users_models.User = Depends(get_current_user),
):
    db_message = messages_models.Message(
        sender_id=current_user.id,
        receiver_id=message.receiver_id,
        content=message.content,
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    receiver = db.query(users_models.User).filter(
        users_models.User.id == message.receiver_id).first()
    print(receiver)
    if not receiver or not receiver.phone_number:
        raise HTTPException(
            status_code=404, detail="Receiver or phone number not found")

    sms_payload = {
        "apikey": SMS_API_KEY,
        "partnerID": SMS_PARTNER_ID,
        "message": message.content,
        "shortcode": SMS_SENDER_ID,
        "mobile": receiver.phone_number  
    }

    try:
        response = httpx.post(SMS_API_URL, json=sms_payload)
        response.raise_for_status()
    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to send SMS: {str(e)}")

    return db_message


