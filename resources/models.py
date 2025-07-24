from sqlalchemy import Column, String, Integer, Enum, ForeignKey
from sqlalchemy.orm import relationship
from users.db import Base
import enum


class ResourceType(str, enum.Enum):
    CONSUMABLE = "CONSUMABLE"
    REUSABLE = "REUSABLE"


class ResourceClassification(str, enum.Enum):
    PHARMACOLOGICAL = "PHARMACOLOGICAL"
    NON_PHARMACOLOGICAL = "NON_PHARMACOLOGICAL"

class Resource(Base):
    __tablename__ = "resources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    code = Column(String(50), unique=True)
    unit_of_measure = Column(String(50), nullable=False)
    quantity_available = Column(Integer, nullable=False, default=0)
    low_stock_threshold = Column(Integer, nullable=False, default=0)
    classification = Column(Enum(ResourceClassification), nullable=False)
    resource_type = Column(Enum(ResourceType), nullable=False)

    service_requirements = relationship("ServiceResourceRequirement", back_populates="resource")
    usage_logs = relationship("UsageLog", back_populates="resource")
