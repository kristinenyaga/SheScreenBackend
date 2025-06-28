from sqlalchemy import Column, String, Integer, Enum, ForeignKey
from sqlalchemy.orm import relationship
from users.db import Base
import enum


class FacilityResource(Base):
    __tablename__ = "facility_resources"

    id = Column(Integer, primary_key=True)
    facility_id = Column(Integer, ForeignKey("facilities.id"))
    resource_type_id = Column(Integer, ForeignKey("resource_types.id"))
    quantity_available = Column(Integer)
    low_stock_threshold = Column(Integer)

    facility = relationship("Facility", back_populates="facility_resources")
    resource_type = relationship("ResourceType")
