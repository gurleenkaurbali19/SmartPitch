from sqlalchemy.orm import Session
from app.models import User

def create_user(db: Session, email: str, hashed_password: str):
    user = User(email=email, hashed_password=hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
