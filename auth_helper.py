from typing import Annotated
from fastapi import Depends, HTTPException, status, APIRouter
from passlib.context import CryptContext
from sqlalchemy.sql import crud

import schemas

from database import SessionLocal

SECRET_KEY = "abc-def-ghi"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

router = APIRouter(prefix="/api/auth", tags=["auth"])

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_current_active_user(
        current_user: Annotated[schemas.User, Depends(crud.get_current_user)]
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
