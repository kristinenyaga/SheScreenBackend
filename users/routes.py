from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.security import OAuth2PasswordRequestForm

from firebase_admin import auth as firebase_auth
from sqlalchemy.orm import Session

from pydantic import BaseModel

from langchain.prompts import PromptTemplate

from users import auth, models, schemas, security
from users.db import get_db
from chat.prompts import generate_context, qa_template
from groq import Groq

from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv())

client = Groq()
router = APIRouter()
    
@router.post("/profile")
def save_profile(
    profile: schemas.UserProfile,
    user: models.User = Depends(auth.verify_firebase_token),
    db: Session = Depends(get_db)
):
    db_user = auth.get_user(db, username=user.username)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    db_user.first_name = profile.first_name
    db_user.last_name = profile.last_name
    db_user.phone_number = profile.phone_number
    db_user.date_of_birth = profile.date_of_birth
    db_user.is_parent = profile.is_parent
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return {"message": "Profile updated successfully", "user_id": user["uid"]}

@router.get("/me")
def get_my_profile(user=Depends(auth.verify_firebase_token)):
    try:
        user_info = firebase_auth.get_user(user["uid"])
        return {
            "uid": user_info.uid,
            "email": user_info.email,
            "display_name": user_info.display_name,
            "phone_number": user_info.phone_number,
            "disabled": user_info.disabled
        }
    except firebase_auth.AuthError as e:
        raise HTTPException(status_code=400, detail=f"Error fetching user profile: {str(e)}")
    


@router.get("/conversation")
async def read_conversation(
    query: str,
    user: models.User = Depends(auth.verify_firebase_token),
    db: Session = Depends(get_db)
):
    db_user = auth.get_user(db, username=user.username)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    context = generate_context(db_user)
    prompt = qa_template.format(
        username=db_user.username,
        context=context,
        question=query
    )

    def classify_intent(query: str) -> str:
        q = query.lower()
        if "what is" in q or "definition" in q:
            return "definition"
        elif "symptom" in q:
            return "symptoms"
        elif "treatment" in q or "treat" in q:
            return "treatment"
        elif "prevent" in q or "vaccine" in q:
            return "prevention"
        elif "help" in q or "support" in q or "feel" in q:
            return "support"
        else:
            return "generic"
        
    def structure_response(query: str, raw_response: str, user: str) -> dict:
        intent = classify_intent(query)

        return {
            "user": user,
            "intent": intent,
            "response": raw_response.strip(),
            "formatted": format_for_display(intent, raw_response.strip(), user)
        }

    def format_for_display(intent: str, response: str, user: str):
        if intent in ["definition", "symptoms", "treatment", "prevention"]:
            return {
                "title": f"{intent.capitalize()} Info",
                "message": response
            }
        elif intent == "support":
            return {
                "title": "Support",
                "message": f"{user}, here's some encouragement and guidance:\n\n{response}"
            }
        else:
            return {
                "title": "Answer",
                "message": response
            }
        
    try:
        completion = client.chat.completions.create(
            model="compound-beta",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": query}
            ]
        )
        raw_response = completion.choices[0].message.content
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM service error: {e}")

    return structure_response(query, raw_response, db_user.username)