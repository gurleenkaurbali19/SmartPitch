#This file will contain your authentication-related endpoints, including OTP request and verification.
from fastapi import APIRouter, HTTPException
from app.schemas.auth_schemas import EmailSchema, OTPVerifySchema
from app.utils.otp_utils import generate_otp
from app.utils.otp_cache import store_otp, is_blocked, verify_otp, is_otp_verified
from app.utils.email_utils import send_otp_email
from fastapi import Body
from app.schemas.auth_schemas import PasswordCreateSchema
from app.utils.otp_cache import is_otp_verified, clear_otp_verified
from sqlalchemy.orm import Session
from app.schemas.auth_schemas import PasswordCreateSchema
from app.utils.security import hash_password
from app.utils.otp_cache import clear_otp_verified, otp_cache
from app.crud import create_user
from app.database import get_db
from fastapi import Depends
from app.models import User



router = APIRouter(prefix="/auth", tags=["auth"])

# OTP Request Endpoint:
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

# OTP Verification Endpoint 
@router.post("/verify-otp")
def verify_otp_endpoint(data: OTPVerifySchema):
    email = data.email
    otp = data.otp

    if verify_otp(email, otp):
        return {"message": "OTP verified successfully."}
    else:
        raise HTTPException(status_code=401, detail="Invalid or expired OTP.")

# password creation endpoint
@router.post("/set-password")
def set_password(data: PasswordCreateSchema, db: Session = Depends(get_db)):
    # Find email with OTP verified in cache
    email = None
    for cached_email, record in otp_cache.items():
        if record.get("otp_verified"):
            email = cached_email
            break

    if not email:
        raise HTTPException(status_code=403, detail="OTP verification required.")

    if data.password != data.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match.")

    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists.")

    hashed_pw = hash_password(data.password)
    
    # Use your CRUD function to create the user
    create_user(db=db, email=email, hashed_password=hashed_pw)

    clear_otp_verified(email)

    return {"message": "Account created successfully. You can now log in."}


  