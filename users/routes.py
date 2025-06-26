from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from langchain_community.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

from openai import OpenAI

from langchain_groq import ChatGroq

from users import auth, models, schemas, security
from users.db import get_db
from chat.prompts import generate_context, qa_template
from groq import Groq

from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv())

client = Groq()

router = APIRouter()


@router.post("/register", response_model=schemas.UserInDBBase)
async def register(user_in: schemas.UserIn, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(
        models.User.email == user_in.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = security.get_password_hash(user_in.password)

    db_user = models.User(
        email=user_in.email,
        first_name="", 
        last_name="",  
        phone_number="", 
        date_of_birth=None, 
        is_parent=False,
        role=models.UserRole.PATIENT,
        hashed_password=hashed_password
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.post("/token", response_model=schemas.Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(
        models.User.email == form_data.username).first()
    if not user or not security.pwd_context.verify(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.patch("/profile",response_model=schemas.UserInDBBase)
async def profile(user_update: schemas.UserUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
        db_user = db.query(models.User).filter(
            models.User.id == current_user.id).first()
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        update_data = user_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_user, key, value)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user


@router.get("/profile", response_model=schemas.UserInDBBase)
async def get_loggedin_user(current_user: models.User = Depends(auth.get_current_user)):
    return current_user


@router.get("/conversation")
async def read_conversation(
    query: str,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    db_user = auth.get_user(db, email=current_user.email)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    context = generate_context(db_user)
    prompt = qa_template.format(
        email=db_user.email,
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

    return structure_response(query, raw_response, db_user.email)