from sqlalchemy import Column, Integer, String, Text, Enum
from sqlalchemy.orm import relationship
from users.db import Base
import enum


class ServiceCategory(str, enum.Enum):
    screening = "screening"
    vaccination = "vaccination"
    treatment = "treatment"

class CervicalCancerService(Base):
    __tablename__ = "cervical_cancer_services"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    slug = Column(String(100), unique=True)
    description = Column(Text, nullable=True)
    category = Column(Enum(ServiceCategory), nullable=False)

    service_cost = relationship("ServiceCost", back_populates="service", uselist=False)
    resource_requirements = relationship("ServiceResourceRequirement", back_populates="service")
