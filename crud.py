from datetime import datetime
from typing import List
from venv import logger

from black import Optional
from sqlalchemy.orm import Session
import models
import schemas
from passlib.context import CryptContext
from jose import JWTError, jwt

SECRET_KEY = "abc-def-ghi"
ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = pwd_context.hash(user.password)
    db_user = models.User(
        username=user.username, email=user.email, hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_dispatches(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Dispatch).offset(skip).limit(limit).all()


def create_dispatch(
    db: Session, area: str, created_at: datetime, user_id: int
) -> models.Dispatch:
    db_dispatch = models.Dispatch(area=area, created_at=created_at, owner_id=user_id)
    db.add(db_dispatch)
    db.commit()
    db.refresh(db_dispatch)
    return db_dispatch


def get_dispatch_by_id(db: Session, dispatch_id: int):
    return db.query(models.Dispatch).filter(models.Dispatch.id == dispatch_id).first()


def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)
    if user and pwd_context.verify(password, user.hashed_password):
        return user
    return None


def get_current_user(db: Session, token: str):
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
    logger.debug(f"Querying accepted dispatches for user_id={user_id}, skip={skip}, limit={limit}")
    dispatches = db.query(models.Dispatch).filter(models.Dispatch.owner_id == user_id).offset(skip).limit(limit).all()
    logger.debug(f"Dispatches found: {dispatches}")
    return dispatches


def start_dispatch(db: Session, dispatch_id: int, user_id: int):
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
