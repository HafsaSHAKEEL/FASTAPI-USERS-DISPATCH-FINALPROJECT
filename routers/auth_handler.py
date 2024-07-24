from datetime import datetime, timedelta
from jose import jwt, JWTError

SECRET_KEY = "abc-def-ghi"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)  # Default expiry time
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_jwt(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print(f"Decoded JWT payload: {payload}")  # Add this line
        if payload.get("exp") and payload["exp"] >= datetime.utcnow().timestamp():
            return payload
        return None
    except JWTError as e:
        print(f"JWTError: {e}")  # Add this line
        return None
