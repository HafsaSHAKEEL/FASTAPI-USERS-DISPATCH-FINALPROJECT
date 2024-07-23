from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
import enum


class RoleBase(BaseModel):
    name: str


class RoleCreate(RoleBase):
    pass


class Role(RoleBase):
    id: int

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    username: str
    email: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserResponse(BaseModel):
    username: str


class User(UserBase):
    id: int
    is_active: bool
    roles: List[Role] = []

    class Config:
        orm_mode = True

        class Config:
            orm_mode = True
            from_attributes = True  # Allow from_orm method


class DispatchCreate(BaseModel):
    area: str


class DispatchStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    STARTED = "started"
    COMPLETED = "completed"


class DispatchBase(BaseModel):
    description: str
    date: datetime
    area: str
    status: DispatchStatus  # Change to enum
    start_time: Optional[datetime] = None
    complete_time: Optional[datetime] = None
    pod_image: Optional[str] = None
    notes: Optional[str] = None
    recipient_name: Optional[str] = None
    created_at: datetime

    class Config:
        orm_mode = True
        from_attributes = True  # Allow from_orm method


class DispatchList(BaseModel):
    total: int
    dispatches: list[DispatchBase]

    class Config:
        orm_mode = True
        from_attributes = True  # Allow from_orm method


class UserLogin(BaseModel):
    email: str
    password: str
