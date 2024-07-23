from datetime import datetime

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from database import Base
import enum


class DispatchStatusEnum(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    STARTED = "started"
    COMPLETED = "completed"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    dispatches = relationship("Dispatch", back_populates="owner")


class Dispatch(Base):
    __tablename__ = "dispatches"

    id = Column(Integer, primary_key=True, index=True)
    area = Column(String, index=True)
    created_at = Column(DateTime, index=True, default=datetime.utcnow)  # Default to current time
    description = Column(String, default="No description")  # Default description
    date = Column(DateTime, default=datetime.utcnow)  # Default to current datetime
    status = Column(Enum(DispatchStatusEnum), default=DispatchStatusEnum.PENDING)
    start_time = Column(DateTime, nullable=True)
    complete_time = Column(DateTime, nullable=True)
    pod_image = Column(String, nullable=True)
    notes = Column(String, nullable=True)
    recipient_name = Column(String, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="dispatches")