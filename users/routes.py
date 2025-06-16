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
    db_user = auth.get_user(db, username=user_in.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    db_user = db.query(models.User).filter(models.User.email == user_in.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = security.get_password_hash(user_in.password)
    db_user = models.User(
        **user_in.model_dump(exclude={"password"}), hashed_password=hashed_password
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
    user = auth.get_user(db, username=form_data.username)
    if not user or not security.pwd_context.verify(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/conversation")
async def read_conversation(
    query: str,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    db_user = auth.get_user(db, username=current_user.username)
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