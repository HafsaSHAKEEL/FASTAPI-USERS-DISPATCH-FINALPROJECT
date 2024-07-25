from datetime import datetime, timedelta
from typing import Annotated

from dotenv import load_dotenv

import schemas

import crud
from fastapi import Depends, HTTPException
from jose import jwt, JWTError
import os
# Load environment variables from the .env file
load_dotenv()

# Retrieve the database URL from the environment variables
SECRET_KEY = os.getenv("SECRET_KEY")


ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def create_access_token(data: dict, expires_delta: timedelta = None):
    """
    Creates a new JWT access token.

    This function generates a JWT token with the given data and optional expiration time.

    Parameters:
    - data (dict): The data to be included in the JWT payload.
    - expires_delta (timedelta, optional): The expiration time for the token. If not provided,
      the token will expire in 15 minutes by default.

    Returns:
    - str: The encoded JWT token.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)  # Default expiry time
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_jwt(token: str):
    """
    Decodes a JWT token and verifies its validity.

    This function attempts to decode the JWT token and checks if it has not expired.

    Parameters:
    - token (str): The JWT token to be decoded.

    Returns:
    - dict or None: The decoded JWT payload if the token is valid and not expired,
      None otherwise.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print(f"Decoded JWT payload: {payload}")  # Add this line
        if payload.get("exp") and payload["exp"] >= datetime.utcnow().timestamp():
            return payload
        return None
    except JWTError as e:
        print(f"JWTError: {e}")  # Add this line
        return None


async def get_current_active_user(
        current_user: Annotated[schemas.User, Depends(crud.get_current_user)]
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
