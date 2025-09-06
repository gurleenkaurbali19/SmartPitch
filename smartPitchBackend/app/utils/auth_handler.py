from datetime import datetime, timedelta
from jose import jwt, JWTError
import os

# Loading from environment variables
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRATION = int(os.getenv("JWT_EXPIRATION", 3600))  # default 1 hour

def create_access_token(data: dict) -> str:
    """
    Create a JWT token with embedded user data and expiry
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(seconds=JWT_EXPIRATION)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> dict:
    """
    Decode and validate a JWT token.
    Returns payload dict if valid, None if invalid or expired.
    """
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except JWTError:
        return None

'''
- create_access_token takes user data as a dictionary (like user ID) and creates a JWT token 
  including that data plus an exp (expiration timestamp).

- decode_access_token verifies and decodes the token, returning user info if valid, or None if invalid or expired.

- The exp claim makes the token expire after the configured time.


'''