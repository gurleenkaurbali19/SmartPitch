import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv

# Loading environment variables from .env file
load_dotenv()

SMTP_HOST = os.getenv('SMTP_HOST')
SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
SMTP_USERNAME = os.getenv('SMTP_USERNAME')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
EMAIL_FROM = os.getenv('EMAIL_FROM')
EMAIL_FROM_NAME = os.getenv('EMAIL_FROM_NAME')

def send_otp_email(to_email: str, otp_code: str):
    # Create message container
    msg = MIMEMultipart('alternative')
    msg['Subject'] = 'Your SmartPitch OTP Code'
    msg['From'] = f"{EMAIL_FROM_NAME} <{EMAIL_FROM}>"
    msg['To'] = to_email

    # Email body in HTML
    html_content = f"""
    <html>
      <body>
        <p>Dear user,</p>
        <p>Your OTP code is: <b>{otp_code}</b></p>
        <p>This code is valid for 5 minutes.</p>
      </body>
    </html>
    """

    # Attaching HTML content
    msg.attach(MIMEText(html_content, 'html'))

    # Connect to SMTP server and send email
    try:
        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.sendmail(EMAIL_FROM, to_email, msg.as_string())
        server.quit()
        print(f"OTP email sent to {to_email}")
        return True
    except Exception as e:
        print(f"Failed to send OTP email: {e}")
        return False
