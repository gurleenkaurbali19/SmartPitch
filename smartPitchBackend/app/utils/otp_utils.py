import random

def generate_otp(length: int = 6) -> str:
    """
    Generates a random numeric OTP of given length.
    Defaults to 6-digit OTP.
    """
    return ''.join([str(random.randint(0, 9)) for _ in range(length)])
