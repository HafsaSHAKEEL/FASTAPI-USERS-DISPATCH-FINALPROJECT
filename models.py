from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum, Boolean
from sqlalchemy.orm import relationship
from database import Base
import enum


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)

    roles = relationship("UserRole", back_populates="user")
    dispatches = relationship("Dispatch", back_populates="owner")
    addresses = relationship("Address", back_populates="user")
    tokens = relationship("Token", back_populates="user")


class UserRole(Base):
    __tablename__ = "user_roles"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    role_id = Column(Integer, ForeignKey("roles.id"), primary_key=True)

    user = relationship("User", back_populates="roles")
    role = relationship("Role")


class Address(Base):
    __tablename__ = "addresses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    street = Column(String)
    city = Column(String)
    state = Column(String)
    zip_code = Column(String)
    country = Column(String)

    user = relationship("User", back_populates="addresses")


class DispatchStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    STARTED = "started"
    COMPLETED = "completed"


class Dispatch(Base):
    __tablename__ = "dispatches"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String, index=True)
    date = Column(DateTime)
    area = Column(String)
    status = Column(Enum(DispatchStatus), default=DispatchStatus.PENDING)
    start_time = Column(DateTime, nullable=True)
    complete_time = Column(DateTime, nullable=True)
    pod_image = Column(String, nullable=True)
    notes = Column(String, nullable=True)
    recipient_name = Column(String, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="dispatches")
    packages = relationship("Package", back_populates="dispatch")
    status_history = relationship("DispatchStatusHistory", back_populates="dispatch")


class Package(Base):
    __tablename__ = "packages"

    id = Column(Integer, primary_key=True, index=True)
    dispatch_id = Column(Integer, ForeignKey("dispatches.id"))
    description = Column(String)
    weight = Column(String)
    dimensions = Column(String)

    dispatch = relationship("Dispatch", back_populates="packages")


class DispatchStatusHistory(Base):
    __tablename__ = "dispatch_status_history"

    id = Column(Integer, primary_key=True, index=True)
    dispatch_id = Column(Integer, ForeignKey("dispatches.id"))
    status = Column(Enum(DispatchStatus))
    timestamp = Column(DateTime)

    dispatch = relationship("Dispatch", back_populates="status_history")


class Token(Base):
    __tablename__ = "tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    token = Column(String, unique=True)
    expiry_date = Column(DateTime)

    user = relationship("User", back_populates="tokens")
