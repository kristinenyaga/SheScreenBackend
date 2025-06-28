from sqlalchemy import Column, String, Integer, Enum, ForeignKey
from sqlalchemy.orm import relationship
from users.db import Base
import enum

class ResourceType(Base):
    __tablename__ = "resource_types"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    unit_of_measure = Column(String(50), nullable=False)

    service_requirements = relationship("ServiceResourceRequirement", back_populates="resource_type")

