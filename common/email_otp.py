import os
import hmac
import hashlib
import base64
import time
import random
import string
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SECRET_KEY = os.getenv("OTP_SECRET", "fallback_secret_key")

def generate_otp(length=10):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choices(characters, k=length))

def generate_otp_token(email: str, otp: str, validity_seconds=300):
    expiry = int(time.time()) + validity_seconds
    msg = f"{email}:{otp}:{expiry}"
    signature = hmac.new(SECRET_KEY.encode(), msg.encode(), hashlib.sha256).hexdigest()
    token = f"{otp}:{expiry}:{signature}"
    return base64.urlsafe_b64encode(token.encode()).decode()

def verify_otp_token(email: str, otp: str, token: str):
    try:
        decoded = base64.urlsafe_b64decode(token).decode()
        otp_value, expiry, signature = decoded.split(":")
        expiry = int(expiry)

        if otp_value != otp:
            return False
        if expiry < int(time.time()):
            return False

        expected_msg = f"{email}:{otp}:{expiry}"
        expected_sig = hmac.new(SECRET_KEY.encode(), expected_msg.encode(), hashlib.sha256).hexdigest()
        return hmac.compare_digest(signature, expected_sig)
    except Exception:
        return False
def send_otp_email(to_email: str, otp: str):
    if not SENDGRID_API_KEY or not SENDER_EMAIL:
        raise ValueError("Missing SendGrid API key or sender email.")

    message = Mail(
        from_email=SENDER_EMAIL,
        to_emails=to_email,
        subject="Your OTP Code for verification",
        plain_text_content=f"Your OTP code is: {otp}. OTP is valid for 2 minutes."
    )
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        print(f"SendGrid status code: {response.status_code}")
    except Exception as e:
        print(f"Error sending OTP email: {e}")
        raise

