from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from messages import models as messages_models
from patients.models import Patient
from users.db import get_db
from users.auth import get_current_user
from messages.schemas import MessageCreate, MessageOut, BotConversationOut, FollowUpMessageCreate
from users import models as users_models
from typing import List
import httpx

router = APIRouter()

SMS_API_URL = "https://sms.textsms.co.ke/api/services/sendsms/"
SMS_API_KEY = "5075367cbe1a8d1284c158b4975615fb"
SMS_PARTNER_ID = "13831"
SMS_SENDER_ID = "TextSMS"


def format_lab_result_sms(patient_name: str, test_name: str, result: str) -> str:
    result = result.capitalize()

    if result == "Negative":
        return (
            f"Dear {patient_name},\n"
            f"Your recent {test_name} result is negative.\n"
            "This suggests no abnormal changes were found.\n"
            "Your doctor will review the result and send a follow-up plan.\n"
            "Call 0712 345 678 for any questions."
        )
    elif result == "Positive":
        return (
            f"Dear {patient_name},\n"
            f"Your recent {test_name} result is positive.\n"
            "This may indicate abnormal changes that need further review.\n"
            "Your doctor will provide a follow-up plan shortly.\n"
            "Call 0712 345 678 if you have any concerns."
        )
    else:
        return (
            f"Dear {patient_name},\n"
            f"Your {test_name} result is now available.\n"
            "Your doctor will contact you with next steps.\n"
            "Call 0712 345 678 if you need support."
        )


@router.post("/send", response_model=MessageOut)
def send_message(
    message: MessageCreate,
    db: Session = Depends(get_db),
    current_user: users_models.User = Depends(get_current_user),
):
    receiver = db.query(Patient).filter(
        Patient.id == message.receiver_patient_id).first()

    if not receiver or not receiver.phone_number:
        raise HTTPException(
            status_code=404, detail="Receiver or phone number not found"
        )

    formatted_sms = format_lab_result_sms(
        patient_name=receiver.first_name,
        test_name=message.test_name,
        result=message.result
    )

    db_message = messages_models.Message(
        sender_user_id=current_user.id,
        receiver_patient_id=message.receiver_patient_id,
        content=formatted_sms,
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)

    sms_payload = {
        "apikey": SMS_API_KEY,
        "partnerID": SMS_PARTNER_ID,
        "message": formatted_sms,
        "shortcode": SMS_SENDER_ID,
        "mobile": receiver.phone_number,
    }

    try:
        response = httpx.post(SMS_API_URL, json=sms_payload)
        response.raise_for_status()
    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to send SMS: {str(e)}")

    return db_message


@router.post("/send-followup", response_model=MessageOut)
def send_followup_message(
    message: FollowUpMessageCreate,
    db: Session = Depends(get_db),
    current_user: users_models.User = Depends(get_current_user),
):
    receiver = db.query(Patient).filter(
        Patient.id == message.patient_id).first()

    if not receiver or not receiver.phone_number:
        raise HTTPException(
            status_code=404, detail="Receiver or phone number not found"
        )

    sms_message = (
        f"Dear {receiver.first_name},\n"
        f"Your doctor has reviewed your test results and recommended the following follow-up plan:\n"
        f"{message.plan_summary}\n"
        "Please visit the clinic to discuss next steps in person.\n"
        "Call us at 0712 345 678 for any questions."
    )

    db_message = messages_models.Message(
        sender_user_id=current_user.id,
        receiver_patient_id=message.patient_id,
        content=sms_message,
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)

    sms_payload = {
        "apikey": SMS_API_KEY,
        "partnerID": SMS_PARTNER_ID,
        "message": sms_message,
        "shortcode": SMS_SENDER_ID,
        "mobile": receiver.phone_number,
    }

    try:
        response = httpx.post(SMS_API_URL, json=sms_payload)
        response.raise_for_status()
    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to send SMS: {str(e)}"
        )

    return db_message


@router.post("/save-bot-conversation")
def save_bot_conversation(
    user_message: str,
    bot_response: str,
    current_user: users_models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    user_db_message = messages_models.Message(
        user_id=current_user.id,
        content=user_message,
        is_bot_message=0,
        conversation_type="user_to_bot"
    )
    db.add(user_db_message)
    
    bot_db_message = messages_models.Message(
        user_id=current_user.id,
        content=bot_response,
        is_bot_message=1,
        conversation_type="user_to_bot"
    )
    db.add(bot_db_message)
    
    db.commit()
    db.refresh(user_db_message)
    db.refresh(bot_db_message)
    
    return {
        "user_message": user_db_message,
        "bot_response": bot_db_message
    }


@router.get("/bot-conversation-history", response_model=List[BotConversationOut])
def get_bot_conversation_history(
    current_user: users_models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    
    conversations = db.query(messages_models.Message).filter(
        messages_models.Message.user_id == current_user.id,
        messages_models.Message.conversation_type == "user_to_bot"
    ).order_by(messages_models.Message.timestamp.asc()).all()
    
    return conversations


