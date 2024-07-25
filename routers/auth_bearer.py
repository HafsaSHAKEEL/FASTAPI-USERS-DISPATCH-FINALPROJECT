from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from routers.auth_handler import decode_jwt


class JWTBearer(HTTPBearer):
    """
    A custom HTTPBearer security scheme for JWT authentication.

    This class extends the `HTTPBearer` class from FastAPI to include custom
    logic for validating JWT tokens provided in the Authorization header of
    HTTP requests.
    """

    def __init__(self, auto_error: bool = True):
        """
        Initializes the JWTBearer class.

        Parameters:
        - auto_error (bool): Whether to automatically raise an HTTPException on
          authentication errors.
        """
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        """
        Validates the JWT token from the Authorization header.

        This method extracts the credentials from the request, checks the
        authentication scheme, and verifies the JWT token. Raises an HTTPException
        if the token is invalid, expired, or the scheme is incorrect.

        Parameters:
        - request (Request): The incoming HTTP request containing the Authorization header.

        Returns:
        - str: The JWT token if it is valid.

        Raises:
        - HTTPException: 403 if the authentication scheme is invalid or the token is missing.
        - HTTPException: 401 if the token is invalid or expired.
        """
        credentials: HTTPAuthorizationCredentials = await super(
            JWTBearer, self
        ).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(
                    status_code=403, detail="Invalid authentication scheme."
                )
            if not self.verify_jwt(credentials.credentials):
                raise HTTPException(
                    status_code=401, detail="Invalid token or expired token."
                )
            return credentials.credentials
        else:
            raise HTTPException(status_code=403, detail="Invalid authorization code.")

    def verify_jwt(self, jwtoken: str) -> bool:
        """
        Verifies the validity of the JWT token.

        Attempts to decode the JWT token and returns True if the token is valid.

        Parameters:
        - jwtoken (str): The JWT token to be verified.

        Returns:
        - bool: True if the token is valid, False otherwise.
        """
        isTokenValid: bool = False
        try:
            payload = decode_jwt(jwtoken)
        except:
            payload = None
        if payload:
            isTokenValid = True
        return isTokenValid
