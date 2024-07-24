from fastapi import APIRouter, Depends, HTTPException
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from datetime import timedelta, datetime

import crud
import schemas
from auth_helper import get_db, ACCESS_TOKEN_EXPIRE_MINUTES

from routers.auth_bearer import JWTBearer
from routers.auth_handler import create_access_token

router = APIRouter(prefix="/api/auth", tags=["auth"])
SECRET_KEY = "abc-def-ghi"
ALGORITHM = "HS256"


@router.post("/signup")
async def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):

    db_user = crud.get_user_by_email(
        db, email=user.email
    )  # checking if the email is already registered
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = crud.create_user(db=db, user=user)  # Creating the new user

    access_token_expires = timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )  # generating the access token for the new user
    access_token = create_access_token(
        data={"email": new_user.email}, expires_delta=access_token_expires
    )

    return {  # Returning the access token along with other relevant information
        "access_token": access_token,
        "token_type": "bearer",
        "email": new_user.email,
        "username": new_user.username,
    }


@router.post("/login")
async def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    authenticated_user = crud.authenticate_user(
        db, email=user.email, password=user.password
    )  # using email for authentication
    if not authenticated_user:
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"email": authenticated_user.email}, expires_delta=access_token_expires
    )
    return {"jwt_token": access_token, "token_type": "bearer"}


@router.post("/refresh")
async def refresh_token(
    token: str = Depends(JWTBearer()), db: Session = Depends(get_db)
):
    if not token:
        raise HTTPException(status_code=401, detail="Token is missing or invalid")

    print(f"Token received for refresh: {token}")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print(f"Decoded JWT payload: {payload}")

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
        print(f"JWTError: {e}")
        raise HTTPException(status_code=401, detail="Invalid token")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    new_access_token = create_access_token(
        data={"email": current_user.email}, expires_delta=access_token_expires
    )
    return {"access_token": new_access_token, "token_type": "bearer"}
