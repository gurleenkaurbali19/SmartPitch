from app.database import SessionLocal
from app.models import EmailLog, User

def view_all_email_logs():
    db = SessionLocal()
    try:
        email_logs = db.query(EmailLog).all()
        for log in email_logs:
            user = db.query(User).filter(User.user_id == log.user_id).first()
            user_email = user.email if user else "Unknown"
            print(f"Log ID: {log.sent_id}, User ID: {log.user_id} ({user_email}), Recipient: {log.recipient_email}, Subject: {log.subject}, Sent At: {log.sent_at}")
    finally:
        db.close()

if __name__ == "__main__":
    view_all_email_logs()
