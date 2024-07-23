# app/auth/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from datetime import timedelta, time, datetime

import crud
import schemas
from auth_helper import get_db, ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token
from routers.auth_bearer import JWTBearer

router = APIRouter(
    prefix="/api/auth",
    tags=["auth"]
)
SECRET_KEY = "abc-def-ghi"  # Ensure this is consistent across your app
ALGORITHM = "HS256"

@router.post("/signup")
async def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Check if the email is already registered
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create the new user
    new_user = crud.create_user(db=db, user=user)

    # Generate the access token for the new user
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"email": new_user.email}, expires_delta=access_token_expires)

    # Return the access token along with other relevant information
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "email": new_user.email,
        "username": new_user.username  # Include additional information as needed
    }

@router.post("/login")
async def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    # Use email instead of username
    authenticated_user = crud.authenticate_user(db, email=user.email, password=user.password)
    if not authenticated_user:
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"email": authenticated_user.email}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/refresh")
async def refresh_token(token: str = Depends(JWTBearer()), db: Session = Depends(get_db)):
    if not token:
        raise HTTPException(status_code=401, detail="Token is missing or invalid")

    print(f"Token received for refresh: {token}")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print(f"Decoded JWT payload: {payload}")

        username = payload.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="Invalid token")

        current_user = crud.get_user_by_email(db, email=username)
        if not current_user:
            raise HTTPException(status_code=401, detail="User not found")

        # Check if the token is expired
        exp = payload.get('exp')
        if exp and exp < datetime.utcnow().timestamp():
            raise HTTPException(status_code=401, detail="Token expired")

    except JWTError as e:
        print(f"JWTError: {e}")
        raise HTTPException(status_code=401, detail="Invalid token")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    new_access_token = create_access_token(data={"email": current_user.email}, expires_delta=access_token_expires)
    return {"access_token": new_access_token, "token_type": "bearer"}


