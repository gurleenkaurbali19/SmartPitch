import time

# Cache dictionary to store OTP data by email:
# Each entry: email -> dict with keys "otp", "attempts", "blocked_until", "timestamp"
otp_cache = {}

# Constants
MAX_ATTEMPTS = 3
BLOCK_DURATION = 3600  # seconds (1 hour)
OTP_EXPIRY = 300       # seconds (5 minutes)


def store_otp(email: str, otp: str):
    """Store OTP and reset attempts and block info"""
    otp_cache[email] = {
        "otp": otp,
        "attempts": 0,
        "blocked_until": 0,
        "timestamp": time.time()
    }

def is_blocked(email: str) -> bool:
    """Return True if user is blocked from OTP verification"""
    blocked_until = otp_cache.get(email, {}).get("blocked_until", 0)
    return time.time() < blocked_until

def verify_otp(email: str, submitted_otp: str) -> bool:
    """Check OTP validity and manage attempt counts and blocking"""
    record = otp_cache.get(email)

    # If no otp for email or expired
    if not record or (time.time() - record['timestamp'] > OTP_EXPIRY):
        return False

    # Check if blocked
    if is_blocked(email):
        return False

    # Check OTP match
    if submitted_otp == record["otp"]:
        # On success, clear record
        otp_cache.pop(email, None)
        return True
    else:
        # Increment attempts
        record["attempts"] += 1
        # Block if max attempts reached
        if record["attempts"] >= MAX_ATTEMPTS:
            record["blocked_until"] = time.time() + BLOCK_DURATION
        return False
