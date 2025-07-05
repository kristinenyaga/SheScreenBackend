from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime,timezone
from users.db import Base 


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    receiver_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    content = Column(Text, nullable=False)
    is_bot_message = Column(Integer, default=0) 
    conversation_type = Column(String(50), default="user_to_user")
    timestamp = Column(DateTime(timezone=True),default=lambda: datetime.now(timezone.utc))

    sender = relationship("User", foreign_keys=[sender_id], backref="sent_messages")
    receiver = relationship("User", foreign_keys=[receiver_id], backref="received_messages")
    user = relationship("User", foreign_keys=[user_id], backref="bot_conversations")
