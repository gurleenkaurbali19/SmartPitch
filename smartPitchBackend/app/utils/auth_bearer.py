from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.status import HTTP_403_FORBIDDEN
from app.utils.auth_handler import decode_access_token  


class JWTBearer(HTTPBearer):
    """
    Custom JWT Bearer class that validates Authorization header token
    for secured routes using FastAPI's security dependency system.
    """

    def __init__(self, auto_error: bool = True):
        """
        :param auto_error: If True, raises HTTPException for auth errors automatically.
        """
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        """
        Called for every request using this dependency.

        Validates Authorization header and verifies JWT token.
        """
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)

        if credentials:
            if credentials.scheme.lower() != "bearer":
                raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Invalid authentication scheme.")
            if not self.verify_jwt(credentials.credentials):
                raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Invalid or expired token.")
            return credentials.credentials  # Return the token for route use
        else:
            raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Invalid authorization header.")

    def verify_jwt(self, jwtoken: str) -> bool:
        """
        Verify the JWT token validity.

        :param jwtoken: JWT token string
        :return: True if token is valid, else False
        """
        try:
            payload = decode_access_token(jwtoken)  # Decodes and validates token
            if payload:
                return True
            return False
        except Exception:
            return False
