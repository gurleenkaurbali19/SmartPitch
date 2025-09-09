from app.database import SessionLocal
from app.models import Resume, User , VectorMeta , EmailLog , JobDescription
def count_rows(db_session, model):
    return db_session.query(model).count()

db = SessionLocal()
print(f"User rows: {count_rows(db, User)}")  # should print 0 if empty
print(f"Resume rows: {count_rows(db, Resume)}")
print(f"VectorMeta rows: {count_rows(db, VectorMeta)}")
print(f"EmailLog rows: {count_rows(db, EmailLog)}")
print(f"JobDescription rows: {count_rows(db, JobDescription)}")
db.close()
