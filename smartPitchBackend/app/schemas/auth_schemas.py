from pydantic import BaseModel, EmailStr, constr

# Schema for email input during registration or OTP request
class EmailSchema(BaseModel):
    email: EmailStr  # Validates that this is a proper email string

# Schema for OTP verification input
class OTPVerifySchema(BaseModel):
    email: EmailStr    # Email to know which user is verifying
    otp: constr(min_length=6, max_length=6)  # OTP must be exactly 6 chars

class PasswordCreateSchema(BaseModel):
    password: constr(min_length=8)  # Password only
    confirm_password: constr(min_length=8)  # Confirm password
    
# Schema for user login input
class LoginSchema(BaseModel):
    email: EmailStr         # User's email for login
    password: constr(min_length=8)  # Password input

# Schema for login response (e.g. after successful login)
class LoginResponseSchema(BaseModel):
    access_token: str  # Token string (like JWT)
    token_type: str    # Token type (usually "bearer")
