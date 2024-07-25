from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from datetime import timedelta, datetime
import os
import crud
import schemas

from database import get_db
from routers.auth_bearer import JWTBearer
from routers.auth_handler import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter(prefix="/api/auth", tags=["auth"])

# Load environment variables from the .env file
load_dotenv()
# Retrieve the database URL from the environment variables
SECRET_KEY= os.getenv("SECRET_KEY")
@router.post("/signup")
async def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = crud.create_user(db=db, user=user)

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"email": new_user.email}, expires_delta=access_token_expires)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "email": new_user.email,
        "username": new_user.username,
    }

@router.post("/login")
async def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    authenticated_user = crud.authenticate_user(db, email=user.email, password=user.password)
    if not authenticated_user:
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"email": authenticated_user.email}, expires_delta=access_token_expires)
    return {"jwt_token": access_token, "token_type": "bearer"}

@router.post("/refresh")
async def refresh_token(token: str = Depends(JWTBearer()), db: Session = Depends(get_db)):
    if not token:
        raise HTTPException(status_code=401, detail="Token is missing or invalid")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[crud.ALGORITHM])
        email = payload.get("email")
        if not email:
            raise HTTPException(status_code=401, detail="Invalid token")

        current_user = crud.get_user_by_email(db, email=email)
        if not current_user:
            raise HTTPException(status_code=401, detail="User not found")

        exp = payload.get("exp")
        if exp and exp < datetime.utcnow().timestamp():
            raise HTTPException(status_code=401, detail="Token expired")

    except JWTError as e:
        raise HTTPException(status_code=401, detail="Invalid token")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    new_access_token = create_access_token(data={"email": current_user.email}, expires_delta=access_token_expires)
    return {"access_token": new_access_token, "token_type": "bearer"}
