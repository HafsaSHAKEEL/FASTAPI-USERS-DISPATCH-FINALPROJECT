from datetime import datetime
from sqlalchemy.orm import Session
import models
import schemas
from passlib.context import CryptContext
from jose import JWTError, jwt

SECRET_KEY = "abc-def-ghi"  # Replace with your actual secret key
ALGORITHM = "HS256"  # Replace with your actual algorithm

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = pwd_context.hash(user.password)
    db_user = models.User(username=user.username, email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_dispatches(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Dispatch).offset(skip).limit(limit).all()


def create_dispatch(db: Session, area: str, created_at: datetime, user_id: int) -> models.Dispatch:
    db_dispatch = models.Dispatch(area=area, created_at=created_at, owner_id=user_id)
    db.add(db_dispatch)
    db.commit()
    db.refresh(db_dispatch)
    return db_dispatch


def get_dispatch_by_id(db: Session, dispatch_id: int) -> models.Dispatch:
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
