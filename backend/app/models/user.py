from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from enum import Enum

from .base import Base


class UserRoleEnum(str, Enum):
    admin = "admin"
    quality_manager = "quality_manager"
    inspector = "inspector"
    engineer = "engineer"
    viewer = "viewer"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(SQLEnum(UserRoleEnum), default=UserRoleEnum.viewer, nullable=False)
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    drawings = relationship("Drawing", back_populates="owner")
    audit_logs = relationship("AuditLog", back_populates="user")
