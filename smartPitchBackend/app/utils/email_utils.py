import json
import requests
import os

BREVO_API_KEY = os.getenv('BREVO_API_KEY')
BREVO_SENDER_EMAIL = os.getenv('BREVO_SENDER_EMAIL')

def send_otp_email(to_email: str, otp: str):
    url = "https://api.brevo.com/v3/smtp/email"
    headers = {
        "accept": "application/json",
        "api-key": BREVO_API_KEY,
        "content-type": "application/json",
    }
    payload = {
        "sender": {"name": "SmartPitch", "email": BREVO_SENDER_EMAIL},
        "to": [{"email": to_email}],
        "subject": "Your SmartPitch OTP Code",
        "textContent": f"Your SmartPitch OTP code is: {otp}. It is valid for 5 minutes."
    }

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 201:
        print("OTP email sent successfully")
        return True
    else:
        print(f"Failed to send OTP email: {response.status_code} - {response.text}")
        return False
