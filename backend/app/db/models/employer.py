from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.db.base import Base

class EmployerStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class Employer(Base):
    __tablename__ = "employers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    company_name = Column(String(255), nullable=False)
    registration_number = Column(String(100), nullable=False)
    industry = Column(String(100), nullable=False)
    company_size = Column(String(50), nullable=False)
    website = Column(String(255), nullable=True)
    country = Column(String(100), nullable=False)
    city = Column(String(100), nullable=False)

    contact_name = Column(String(255), nullable=False)
    contact_title = Column(String(100), nullable=False)
    contact_email = Column(String(255), nullable=False)
    contact_phone = Column(String(50), nullable=False)

    hiring_description = Column(Text, nullable=True)
    certificate_url = Column(String(500), nullable=True)
    logo_url = Column(String(500), nullable=True)

    status = Column(Enum(EmployerStatus), default=EmployerStatus.PENDING)
    rejection_reason = Column(Text, nullable=True)

    applied_at = Column(DateTime, default=datetime.utcnow)
    reviewed_at = Column(DateTime, nullable=True)
    reviewed_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    reviewer = relationship("User", foreign_keys=[reviewed_by])
