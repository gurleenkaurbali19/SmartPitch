from sqlalchemy.orm import Session
from app import models
from app.security import hash_password, verify_password


def create_user(db: Session, email: str, password: str) -> models.User:
    """
    Create a new user record in the database.
    Inputs:
      - db: database session
      - email: user's email 
      - password: the plaintext password to be hashed and stored
    Returns:
      - the new User model instance saved in the DB
    """

    # Hash the plain password to securely store it
    hashed_pw = hash_password(password)
    
    # Create the User model instance
    user = models.User(email=email, hashed_password=hashed_pw)
    
    # Stage the user creation for commit
    db.add(user)
    
    # Commit to save changes permanently
    db.commit()
    
    # Refresh the instance with updated DB info
    db.refresh(user)
    
    return user


def authenticate_user(db: Session, email: str, password: str) -> models.User | None:
    """
    Authenticate a user attempting to log in.
    Inputs:
      - db: database session
      - email: user email to lookup
      - password: plaintext password entered by user
    Returns:
      - User instance if authentication succeeds
      - None if credentials are invalid
    """

    # Query the user by email
    user = db.query(models.User).filter(models.User.email == email).first()

    # If user not found, return None
    if not user:
        return None

    # Verify that the input password matches stored hashed password
    if not verify_password(password, user.hashed_password):
        return None

    # Valid credentials, return User instance
    return user
