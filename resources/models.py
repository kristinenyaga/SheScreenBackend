from sqlalchemy import Column, String, Integer, Enum, ForeignKey
from sqlalchemy.orm import relationship
from users.db import Base
import enum


class ResourceCategory(str, enum.Enum):
    equipment = "equipment"
    medication = "medication"
    consumables = "consumables"



class Resource(Base):
    __tablename__ = "resources"

    id = Column(Integer, primary_key=True, index=True)
    facility_id = Column(Integer, ForeignKey("facilities.id"), nullable=False)
    name = Column(String(100), nullable=False)
    category = Column(Enum(ResourceCategory), nullable=False)
    quantity_available = Column(Integer, default=0)
    unit_of_measure = Column(String(50), nullable=False)
    low_stock_threshold = Column(Integer, default=5)

    facility = relationship("Facility", back_populates="resources")
