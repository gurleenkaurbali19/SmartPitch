from app.database import SessionLocal
from app.models import VectorMeta, User, Resume

def view_all_vector_meta():
    db = SessionLocal()
    try:
        vectors = db.query(VectorMeta).all()
        for vec in vectors:
            user = db.query(User).filter(User.user_id == vec.user_id).first()
            resume = db.query(Resume).filter(Resume.res_id == vec.resume_id).first()
            user_email = user.email if user else "Unknown"
            resume_info = f"Resume ID {vec.resume_id}, Filename: {resume.filename}" if resume else "No Resume"
            print(f"Vector ID: {vec.vector_id}, User ID: {vec.user_id} ({user_email}), {resume_info}, FAISS Vector ID: {vec.faiss_vector_id}, Created At: {vec.created_at}")
    finally:
        db.close()

if __name__ == "__main__":
    view_all_vector_meta()
