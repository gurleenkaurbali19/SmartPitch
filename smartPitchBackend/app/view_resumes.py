from app.database import SessionLocal
from app.models import Resume, User

def view_all_resumes():
    db = SessionLocal()
    try:
        resumes = db.query(Resume).all()
        for res in resumes:
            user = db.query(User).filter(User.user_id == res.user_id).first()
            user_email = user.email if user else "Unknown"
            print(f"Resume ID: {res.res_id}, User ID: {res.user_id} ({user_email}), Filename: {res.filename}, Uploaded At: {res.uploaded_at}")
    finally:
        db.close()

if __name__ == "__main__":
    view_all_resumes()
