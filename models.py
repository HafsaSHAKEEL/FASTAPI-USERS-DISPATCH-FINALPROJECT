import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from database import Base


class DispatchStatusEnum(str, enum.Enum):
    """
    Enumeration for dispatch status.

    This enum defines the possible statuses a dispatch can have.
    """
    IN_PROGRESS = "in_progress"
    PENDING = "pending"
    ACCEPTED = "accepted"
    STARTED = "started"
    COMPLETED = "completed"


class User(Base):
    """
    SQLAlchemy model for the User entity.

    This model represents a user in the system and includes attributes for username,
    email, hashed password, and active status. It also establishes a relationship
    to the Dispatch model.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    dispatches = relationship("Dispatch", back_populates="owner")


class Dispatch(Base):
    """
    SQLAlchemy model for the Dispatch entity.

    This model represents a dispatch in the system and includes attributes for
    area, created at, description, date, status, start and complete times, proof of
    delivery image, notes, recipient name, and owner. It also establishes a relationship
    to the User model.
    """
    __tablename__ = "dispatches"

    id = Column(Integer, primary_key=True, index=True)
    area = Column(String, index=True)
    created_at = Column(DateTime, index=True, default=datetime.utcnow)
    description = Column(String, default="No description")
    date = Column(DateTime, default=datetime.utcnow)
    status = Column(Enum(DispatchStatusEnum), default=DispatchStatusEnum.PENDING)
    start_time = Column(DateTime, nullable=True)
    complete_time = Column(DateTime, nullable=True)
    pod_image = Column(String, nullable=True)
    notes = Column(String, nullable=True)
    recipient_name = Column(String, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="dispatches")
