import random
import datetime

def generate_otp(length=6):
    return ''.join([str(random.randint(0, 9)) for _ in range(length)])

def otp_expiry(minutes=5):
    return (datetime.datetime.utcnow() + datetime.timedelta(minutes=minutes)).isoformat()