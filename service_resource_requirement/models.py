from sqlalchemy import Column, Integer, String, Boolean, Date, Enum as SqlEnum, ForeignKey, ForeignKey
from sqlalchemy.orm import relationship
from users.db import Base
import enum


class ServiceResourceRequirement(Base):
    __tablename__ = "service_resource_requirements"

    id = Column(Integer, primary_key=True)
    service_id = Column(Integer, ForeignKey("cervical_cancer_services.id"))
    resource_id = Column(Integer, ForeignKey("resources.id"))
    required_quantity = Column(Integer)

    service = relationship("CervicalCancerService",back_populates="resource_requirements")
    resource = relationship("Resource", back_populates="service_requirements")
