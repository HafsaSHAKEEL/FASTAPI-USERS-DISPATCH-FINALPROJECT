from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
import enum


class RoleBase(BaseModel):
    """
    Base model for role attributes.

    This model includes the basic attributes for a role, such as its name.
    """
    name: str


class RoleCreate(RoleBase):
    """
    Model for creating a new role.

    This model extends RoleBase and is used for creating new roles.
    """
    pass


class Role(RoleBase):
    """
    Model for a role with an ID.

    This model includes all attributes of RoleBase along with an ID field,
    which represents the unique identifier for the role.
    """
    id: int

    class Config:
        orm_mode = True
        from_attributes = True


class UserBase(BaseModel):
    """
    Base model for user attributes.

    This model includes basic attributes for a user, such as username and email.
    """
    username: str
    email: Optional[str] = None


class UserCreate(UserBase):
    """
    Model for creating a new user.

    This model extends UserBase and adds a password field for creating a new user.
    """
    password: str


class UserResponse(BaseModel):
    """
    Model for user response.

    This model includes the username of the user and is used in responses where
    only the username is needed.
    """
    username: str


class User(UserBase):
    """
    Model for a user with additional fields.

    This model extends UserBase to include an ID, active status, and associated roles.
    """
    id: int
    is_active: bool
    roles: List[Role] = []

    class Config:
        orm_mode = True
        from_attributes = True


class DispatchStatus(str, enum.Enum):
    """
    Enumeration for dispatch status.

    This enum defines the possible statuses a dispatch can have.
    """
    IN_PROGRESS = "in_progress"
    PENDING = "pending"
    ACCEPTED = "accepted"
    STARTED = "started"
    COMPLETED = "completed"


class DispatchCreate(BaseModel):
    """
    Model for creating a new dispatch.

    This model includes the area attribute required to create a new dispatch.
    """
    area: str


class DispatchBase(BaseModel):
    """
    Base model for a dispatch.

    This model includes attributes that describe a dispatch, such as ID, description,
    date, area, status, and timestamps. It represents the core details of a dispatch.
    """
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
    """
    Model for user login credentials.

    This model includes the email and password required for user authentication.
    """
    email: str
    password: str


class DispatchList(BaseModel):
    """
    Model for a list of dispatches.

    This model includes a total count of dispatches and a list of DispatchBase objects
    representing individual dispatches.
    """
    total: int
    dispatches: List[DispatchBase]

    class Config:
        orm_mode = True
        from_attributes = True


class DispatchAcceptResponse(BaseModel):
    """
    Model for the response after accepting a dispatch.

    This model includes a message confirming that the dispatch has been accepted.
    """
    message: str


class DispatchStartResponse(BaseModel):
    """
    Model for the response after starting a dispatch.

    This model includes details of the dispatch that was started, including its ID,
    area, status, start time, and creation time.
    """
    id: int
    area: str
    status: DispatchStatus
    start_time: datetime
    created_at: datetime

    class Config:
        orm_mode = True
        from_attributes = True


class DispatchCompleteRequest(BaseModel):
    """
    Model for the request body when completing a dispatch.

    This model includes fields for the proof of delivery image, notes, and recipient name
    required to complete a dispatch.
    """
    pod_image: str
    notes: str
    recipient_name: str
