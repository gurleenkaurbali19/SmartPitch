from app.database import SessionLocal
from app.models import User, Resume, VectorMeta, EmailLog, JobDescription
from sqlalchemy.orm import Session

def print_all_rows(db: Session):
    tables = [
        ("Users", User),
        ("Resumes", Resume),
        ("VectorMeta", VectorMeta),
        ("EmailLogs", EmailLog),
        ("JobDescriptions", JobDescription),
    ]

    for table_name, model in tables:
        print(f"\nTable: {table_name}")
        rows = db.query(model).all()
        if not rows:
            print(" No rows found.")
            continue
        for row in rows:
            # Print dict representation to see all columns easily
            print(vars(row))
            

if __name__ == "__main__":
    db = SessionLocal()
    try:
        print_all_rows(db)
    finally:
        db.close()
