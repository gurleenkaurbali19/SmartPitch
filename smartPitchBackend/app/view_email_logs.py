from app.database import SessionLocal
from app.models import EmailLog
from sqlalchemy.orm import Session

def print_email_logs(db: Session):
    print("\nTable: EmailLogs")
    emails = db.query(EmailLog).all()
    if not emails:
        print(" No rows found.")
    for e in emails:
        print(vars(e))

if __name__ == "__main__":
    db = SessionLocal()
    try:
        print_email_logs(db)
    finally:
        db.close()
