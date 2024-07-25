from datetime import datetime
from typing import Optional

from dotenv import load_dotenv
from sqlalchemy.orm import Session
import models
import schemas
from passlib.context import CryptContext
from jose import JWTError, jwt
import logging
import os

# Load environment variables from the .env file
load_dotenv()

# Retrieve the database URL from the environment variables
SECRET_KEY = os.getenv("SECRET_KEY")

ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
logger = logging.getLogger(__name__)


def get_user_by_username(db: Session, username: str):
    """
    Retrieves a user from the database by their username.

    Parameters:
    - db (Session): The SQLAlchemy session object.
    - username (str): The username of the user to retrieve.

    Returns:
    - models.User: The user object if found, else None.
    """
    return db.query(models.User).filter(models.User.username == username).first()


def get_user_by_email(db: Session, email: str):
    """
    Retrieves a user from the database by their email.

    Parameters:
    - db (Session): The SQLAlchemy session object.
    - email (str): The email of the user to retrieve.

    Returns:
    - models.User: The user object if found, else None.
    """
    return db.query(models.User).filter(models.User.email == email).first()


def create_user(db: Session, user: schemas.UserCreate):
    """
    Creates a new user in the database.

    Parameters:
    - db (Session): The SQLAlchemy session object.
    - user (schemas.UserCreate): The user creation schema containing user details.

    Returns:
    - models.User: The newly created user object.
    """
    hashed_password = pwd_context.hash(user.password)
    db_user = models.User(
        username=user.username, email=user.email, hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_dispatches(db: Session, skip: int = 0, limit: int = 10):
    """
    Retrieves a list of dispatches from the database with pagination.

    Parameters:
    - db (Session): The SQLAlchemy session object.
    - skip (int): Number of records to skip (for pagination).
    - limit (int): Number of records to retrieve.

    Returns:
    - list[models.Dispatch]: A list of dispatch objects.
    """
    return db.query(models.Dispatch).offset(skip).limit(limit).all()


def create_dispatch(
        db: Session, area: str, created_at: datetime, user_id: int
) -> models.Dispatch:
    """
    Creates a new dispatch in the database.

    Parameters:
    - db (Session): The SQLAlchemy session object.
    - area (str): The area where the dispatch is to be created.
    - created_at (datetime): The timestamp when the dispatch is created.
    - user_id (int): The ID of the user creating the dispatch.

    Returns:
    - models.Dispatch: The newly created dispatch object.
    """
    db_dispatch = models.Dispatch(area=area, created_at=created_at, owner_id=user_id)
    db.add(db_dispatch)
    db.commit()
    db.refresh(db_dispatch)
    return db_dispatch


def get_dispatch_by_id(db: Session, dispatch_id: int):
    """
    Retrieves a dispatch from the database by its ID.

    Parameters:
    - db (Session): The SQLAlchemy session object.
    - dispatch_id (int): The ID of the dispatch to retrieve.

    Returns:
    - models.Dispatch: The dispatch object if found, else None.
    """
    return db.query(models.Dispatch).filter(models.Dispatch.id == dispatch_id).first()


def authenticate_user(db: Session, email: str, password: str):
    """
    Authenticates a user based on email and password.

    Parameters:
    - db (Session): The SQLAlchemy session object.
    - email (str): The email of the user to authenticate.
    - password (str): The password of the user to authenticate.

    Returns:
    - models.User: The authenticated user object if credentials are valid, else None.
    """
    user = get_user_by_email(db, email)
    if user and pwd_context.verify(password, user.hashed_password):
        return user
    return None


def get_current_user(db: Session, token: str):
    """
    Retrieves the current user based on the JWT token.

    Parameters:
    - db (Session): The SQLAlchemy session object.
    - token (str): The JWT token containing user information.

    Returns:
    - models.User: The user object if the token is valid, else None.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("email")
        if email:
            return get_user_by_email(db, email=email)
    except JWTError:
        return None
    return None


def get_filtered_dispatches(
        db: Session,
        status: Optional[str],
        date: Optional[datetime],
        area: Optional[str],
        skip: int,
        limit: int,
):
    """
    Retrieves a list of dispatches from the database with optional filters and pagination.

    Parameters:
    - db (Session): The SQLAlchemy session object.
    - status (Optional[str]): Optional filter for dispatch status.
    - date (Optional[datetime]): Optional filter for dispatch date.
    - area (Optional[str]): Optional filter for dispatch area.
    - skip (int): Number of records to skip (for pagination).
    - limit (int): Number of records to retrieve.

    Returns:
    - list[models.Dispatch]: A list of filtered dispatch objects.
    """
    logger.debug("Starting get_filtered_dispatches with parameters:")
    logger.debug(f"Status: {status}")
    logger.debug(f"Date: {date}")
    logger.debug(f"Area: {area}")
    logger.debug(f"Skip: {skip}")
    logger.debug(f"Limit: {limit}")

    query = db.query(models.Dispatch)

    if status:
        logger.debug(f"Applying status filter: {status}")
        query = query.filter(models.Dispatch.status == status)
    if date:
        logger.debug(f"Applying date filter: {date}")
        query = query.filter(models.Dispatch.date == date)
    if area:
        logger.debug(f"Applying area filter: {area}")
        query = query.filter(models.Dispatch.area == area)

    # Log the query to be executed
    logger.debug(f"Constructed query: {str(query)}")

    # Execute the query
    dispatches = query.offset(skip).limit(limit).all()

    logger.debug(f"Retrieved dispatches: {dispatches}")

    return dispatches


def accept_dispatch(db: Session, dispatch_id: int, user_id: int):
    """
    Marks a dispatch as accepted by a user.

    Parameters:
    - db (Session): The SQLAlchemy session object.
    - dispatch_id (int): The ID of the dispatch to be accepted.
    - user_id (int): The ID of the user accepting the dispatch.

    Returns:
    - models.Dispatch: The updated dispatch object if successful, else None.
    """
    dispatch = (
        db.query(models.Dispatch).filter(models.Dispatch.id == dispatch_id).first()
    )
    if not dispatch:
        return None
    dispatch.status = models.DispatchStatusEnum.IN_PROGRESS
    # dispatch.start_time = datetime.utcnow()
    dispatch.owner_id = user_id
    db.commit()
    db.refresh(dispatch)
    return dispatch


def get_accepted_dispatches(db: Session, user_id: int, skip: int, limit: int):
    """
    Retrieves a list of accepted dispatches for a specific user with pagination.

    Parameters:
    - db (Session): The SQLAlchemy session object.
    - user_id (int): The ID of the user for whom to retrieve accepted dispatches.
    - skip (int): Number of records to skip (for pagination).
    - limit (int): Number of records to retrieve.

    Returns:
    - list[models.Dispatch]: A list of accepted dispatch objects.
    """
    logger.debug(
        f"Querying accepted dispatches for user_id={user_id}, skip={skip}, limit={limit}"
    )
    dispatches = (
        db.query(models.Dispatch)
        .filter(models.Dispatch.owner_id == user_id)
        .offset(skip)
        .limit(limit)
        .all()
    )
    logger.debug(f"Dispatches found: {dispatches}")
    return dispatches


def start_dispatch(db: Session, dispatch_id: int, user_id: int):
    """
    Marks a dispatch as started by a user.

    Parameters:
    - db (Session): The SQLAlchemy session object.
    - dispatch_id (int): The ID of the dispatch to be started.
    - user_id (int): The ID of the user starting the dispatch.

    Returns:
    - models.Dispatch: The updated dispatch object if successful, else None.
    """
    dispatch = (
        db.query(models.Dispatch).filter(models.Dispatch.id == dispatch_id).first()
    )
    if not dispatch:
        return None
    if dispatch.owner_id != user_id:
        return None
    dispatch.status = models.DispatchStatusEnum.STARTED
    dispatch.start_time = datetime.utcnow()
    db.commit()
    db.refresh(dispatch)
    return dispatch


def complete_dispatch(
        db: Session,
        dispatch_id: int,
        user_id: int,
        pod_image: str,
        notes: str,
        recipient_name: str,
) -> schemas.DispatchBase:
    """
    Marks a dispatch as completed by a user and updates its details.

    Parameters:
    - db (Session): The SQLAlchemy session object.
    - dispatch_id (int): The ID of the dispatch to be completed.
    - user_id (int): The ID of the user completing the dispatch.
    - pod_image (str): Proof of delivery image URL or data.
    - notes (str): Additional notes for the dispatch.
    - recipient_name (str): The name of the recipient.

    Returns:
    - schemas.DispatchBase: The updated dispatch schema if successful, else None.
    """
    dispatch = (
        db.query(models.Dispatch).filter(models.Dispatch.id == dispatch_id).first()
    )
    if not dispatch or dispatch.owner_id != user_id:
        return None

    dispatch.status = models.DispatchStatusEnum.COMPLETED
    dispatch.complete_time = datetime.utcnow()
    dispatch.pod_image = pod_image
    dispatch.notes = notes
    dispatch.recipient_name = recipient_name
    db.commit()
    db.refresh(dispatch)
    return dispatch
