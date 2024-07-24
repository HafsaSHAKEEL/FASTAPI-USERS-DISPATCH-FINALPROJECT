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
        from_attributes = True


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
        from_attributes = True


class DispatchStatus(str, enum.Enum):
    IN_PROGRESS = "in_progress"
    PENDING = "pending"
    ACCEPTED = "accepted"
    STARTED = "started"
    COMPLETED = "completed"


class DispatchCreate(BaseModel):
    area: str


class DispatchBase(BaseModel):
    id: int
    description: str
    date: datetime
    area: str
    status: DispatchStatus
    start_time: Optional[datetime] = None
    complete_time: Optional[datetime] = None
    pod_image: Optional[str] = None
    notes: Optional[str] = None
    recipient_name: Optional[str] = None
    created_at: datetime

    class Config:
        orm_mode = True
        from_attributes = True


class UserLogin(BaseModel):
    email: str
    password: str


class DispatchList(BaseModel):
    total: int
    dispatches: List[DispatchBase]

    class Config:
        orm_mode = True
        from_attributes = True


class DispatchAcceptResponse(BaseModel):
    message: str


class DispatchStartResponse(BaseModel):
    id: int
    area: str
    status: DispatchStatus
    start_time: datetime
    created_at: datetime

    class Config:
        orm_mode = True
        from_attributes = True


class DispatchCompleteRequest(BaseModel):
    pod_image: str
    notes: str
    recipient_name: str
