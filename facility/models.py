from sqlalchemy import Column, String, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from users.db import Base


class Facility(Base):
    __tablename__ = "facilities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    region = Column(String(100), nullable=False)
    contact_number = Column(String(100), nullable=True)

    users = relationship("FacilityUser", back_populates="facility")
    resources = relationship("Resource", back_populates="facility")
