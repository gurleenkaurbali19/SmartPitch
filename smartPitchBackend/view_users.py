from app.database import SessionLocal
from app.models import User

def view_all_users():
    db = SessionLocal()
    try:
        users = db.query(User).all()
        for user in users:
            print(f"User ID: {user.user_id}, Email: {user.email}, Created At: {user.created_at}")
    finally:
        db.close()

if __name__ == "__main__":
    view_all_users()
