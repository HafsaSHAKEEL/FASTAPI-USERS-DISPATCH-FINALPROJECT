from fastapi import HTTPException
from jose import JWTError, jwt

from sqlalchemy.orm import Session
from passlib.context import CryptContext
import models
import schemas

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = "abc_def_ghi"
ALGORITHM = "HS256"

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


def create_role(db: Session, role: schemas.RoleCreate):
    db_role = models.Role(name=role.name)
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role


def assign_role_to_user(db: Session, user_id: int, role_id: int):
    user_role = models.UserRole(user_id=user_id, role_id=role_id)
    db.add(user_role)
    db.commit()
    db.refresh(user_role)
    return user_role


def create_dispatch(db: Session, dispatch: schemas.DispatchCreate, user_id: int):
    db_dispatch = models.Dispatch(**dispatch.model_dump(), owner_id=user_id)
    db.add(db_dispatch)
    db.commit()
    db.refresh(db_dispatch)
    return db_dispatch


def get_dispatches(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Dispatch).offset(skip).limit(limit).all()


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def authenticate_user(db: Session, username: str, password: str):
    user = get_user_by_username(db, username)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user


def get_dispatch_by_id(db: Session, dispatch_id: int):
    return db.query(models.Dispatch).filter(models.Dispatch.id == dispatch_id).first()


def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


def get_current_user(db: Session, token: str):
    payload = verify_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    username = payload.get("sub")
    if username is None:
        raise HTTPException(status_code=401, detail="Token does not contain user information")

    user = get_user_by_username(db, username=username)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")

    return user


def update_dispatch_status(db: Session, dispatch_id: int, status: schemas.DispatchStatus):
    db_dispatch = db.query(models.Dispatch).filter(models.Dispatch.id == dispatch_id).first()
    if db_dispatch:
        db_dispatch.status = status
        db.commit()
        db.refresh(db_dispatch)
    return db_dispatch


def accept_dispatch(db: Session, dispatch_id: int):
    return update_dispatch_status(db, dispatch_id, schemas.DispatchStatus.ACCEPTED)


def start_dispatch(db: Session, dispatch_id: int):
    return update_dispatch_status(db, dispatch_id, schemas.DispatchStatus.STARTED)


def complete_dispatch(db: Session, dispatch_id: int, pod_data: schemas.DispatchComplete):
    db_dispatch = get_dispatch_by_id(db, dispatch_id)
    if db_dispatch:
        db_dispatch.status = schemas.DispatchStatus.COMPLETED
        db_dispatch.pod_image = pod_data.pod_image
        db_dispatch.notes = pod_data.notes
        db_dispatch.recipient_name = pod_data.recipient_name
        db.commit()
        db.refresh(db_dispatch)
    return db_dispatch
