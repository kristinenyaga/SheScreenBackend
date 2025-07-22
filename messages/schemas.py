from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class MessageCreate(BaseModel):
    receiver_patient_id: int
    sender_user_id: int
    content: str


class BotConversationCreate(BaseModel):
    content: str


class MessageOut(BaseModel):
    id: int
    sender_user_id: Optional[int] = None
    receiver_patient_id: Optional[int] = None
    content: str
    is_bot_message: bool
    conversation_type: str
    timestamp: datetime

    class Config:
        from_attributes = True


    class Config:
        from_attributes = True


class BotConversationOut(BaseModel):
    id: int
    user_id: int
    content: str
    is_bot_message: int
    timestamp: datetime

    class Config:
        from_attributes = True
