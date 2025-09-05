from app.database import SessionLocal
from app.models import User

def delete_user_by_email(email: str):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if user:
            db.delete(user)
            db.commit()
            print(f"User with email {email} deleted successfully.")
        else:
            print(f"No user found with email {email}.")
    finally:
        db.close()

if __name__ == "__main__":
    email_to_delete = input("Enter the email of the user to delete: ")
    delete_user_by_email(email_to_delete)
