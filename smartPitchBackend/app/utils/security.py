from passlib.context import CryptContext

# Create an instance that handles hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """
    Converts a plain password into a secure hashed password.
    This is stored in the database instead of the plain password.
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Check if the plain password entered by user matches the hashed password stored.
    Returns True if they match, False if not.
    """
    return pwd_context.verify(plain_password, hashed_password)
