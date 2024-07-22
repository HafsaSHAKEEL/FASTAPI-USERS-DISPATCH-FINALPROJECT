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


class User(UserBase):
    id: int
    is_active: bool
    roles: List[Role] = []

    class Config:
        orm_mode = True


class AddressBase(BaseModel):
    street: str
    city: str
    state: str
    zip_code: str
    country: str


class AddressCreate(AddressBase):
    pass


class Address(AddressBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True


class DispatchStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    STARTED = "started"
    COMPLETED = "completed"


class DispatchBase(BaseModel):
    description: str
    date: datetime
    area: str
    status: DispatchStatus
    start_time: Optional[datetime] = None
    complete_time: Optional[datetime] = None
    pod_image: Optional[str] = None
    notes: Optional[str] = None
    recipient_name: Optional[str] = None


class DispatchCreate(DispatchBase):
    pass


class Dispatch(DispatchBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True


class DispatchComplete(BaseModel):
    pod_image: str
    notes: str
    recipient_name: str


class PackageBase(BaseModel):
    description: str
    weight: str
    dimensions: str


class PackageCreate(PackageBase):
    pass


class Package(PackageBase):
    id: int
    dispatch_id: int

    class Config:
        orm_mode = True


class DispatchStatusHistoryBase(BaseModel):
    status: DispatchStatus
    timestamp: datetime


class DispatchStatusHistoryCreate(DispatchStatusHistoryBase):
    pass


class DispatchStatusHistory(DispatchStatusHistoryBase):
    id: int
    dispatch_id: int

    class Config:
        orm_mode = True


class TokenBase(BaseModel):
    token: str
    expiry_date: datetime


class TokenCreate(TokenBase):
    pass


class Token(TokenBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True
