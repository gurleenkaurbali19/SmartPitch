#This file will contain your authentication-related endpoints, including OTP request and verification.
from fastapi import APIRouter, HTTPException
from app.schemas.auth_schemas import EmailSchema
from app.utils.otp_utils import generate_otp
from app.utils.otp_cache import store_otp, is_blocked
from app.utils.email_utils import send_otp_email

from app.schemas.auth_schemas import OTPVerifySchema
from app.utils.otp_cache import verify_otp



router = APIRouter(prefix="/auth", tags=["auth"])  #api router instance


#OTP Requst Endpoint:
@router.post("/request-otp")
def request_otp(data: EmailSchema):
    email = data.email

    if is_blocked(email):
        raise HTTPException(status_code=403, detail="Too many failed attempts. Try again later.")

    otp = generate_otp()
    store_otp(email, otp)

    if send_otp_email(email, otp):
        return {"message": "OTP sent to your email."}
    else:
        raise HTTPException(status_code=500, detail="Failed to send OTP email.")


#OTP Verification Endpoint:
@router.post("/verify-otp")
def verify_otp_endpoint(data: OTPVerifySchema):
    email = data.email
    otp = data.otp

    if verify_otp(email, otp):
        return {"message": "OTP verified successfully."}
    else:
        raise HTTPException(status_code=401, detail="Invalid or expired OTP.")
