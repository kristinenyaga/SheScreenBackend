from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime,Boolean
from sqlalchemy.orm import relationship
from datetime import datetime,timezone
from users.db import Base 


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)

    sender_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    receiver_patient_id = Column(Integer, ForeignKey("patients.id"), nullable=True)

    content = Column(Text, nullable=False)
    is_bot_message = Column(Boolean, default=False)
    conversation_type = Column(String(50), default="user_to_patient")
    timestamp = Column(DateTime(timezone=True),default=lambda: datetime.now(timezone.utc))
    sender_user = relationship("User", back_populates="sent_messages")
    receiver_patient = relationship("Patient", back_populates="received_messages")
