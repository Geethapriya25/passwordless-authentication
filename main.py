from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from supabase import create_client
from typing import Optional
from dotenv import load_dotenv
import os
import sys

# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

load_dotenv()

from common.aes_utils import encrypt_data, decrypt_data
from common.hash_utils import hash_email
from common.email_otp import generate_otp, generate_otp_token, verify_otp_token, send_otp_email
from common.voice_utils import get_voice_embedding, match_spoken_phrase
from common.db_utils import get_user_by_email_hash, insert_user_to_supabase

app = FastAPI()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise Exception("Supabase credentials missing in .env")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

#  Models
class OTPRequest(BaseModel):
    email: str

class OTPVerify(BaseModel):
    email: str
    otp: str
    token: str

class UserLogin(BaseModel):
    email: str
    auth_method: Optional[str] = None

#  Routes 

@app.post("/send-otp")
def send_otp(request: OTPRequest):
    normalized_email = request.email.strip().lower()
    otp = generate_otp()
    token = generate_otp_token(normalized_email, otp)
    try:
        send_otp_email(normalized_email, otp)
        return {"token": token, "message": "OTP sent to email"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sending email: {str(e)}")

@app.post("/verify-otp")
def verify_otp(data: OTPVerify):
    normalized_email = data.email.strip().lower()
    if verify_otp_token(normalized_email, data.otp, data.token):
        return {"message": "OTP verified successfully"}
    else:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")

@app.post("/register")
async def register_user(
    email: str = Form(...),
    phone: str = Form(...),
    auth_method: str = Form(...),
    otp: str = Form(...),
    token: str = Form(...),
    spoken_phrase: Optional[str] = Form(None),
    voice: Optional[UploadFile] = File(None)
):
    try:
        if not verify_otp_token(email, otp, token):
            raise HTTPException(status_code=400, detail="Invalid or expired OTP")

        email = email.strip().lower()
        phone = phone.strip()
        email_hash = hash_email(email)

        encrypted_email = encrypt_data(email)
        encrypted_phone = encrypt_data(phone)

        voice_url = None
        voice_embedding = None
        if auth_method == "voice" and voice is not None:
            voice_data = await voice.read()
            voice_embedding = get_voice_embedding(voice_data)
            voice_url = None

        insert_user_to_supabase({
            "email": encrypted_email,
            "phone": encrypted_phone,
            "email_hash": email_hash,
            "spoken_phrase": spoken_phrase,
            "voice_features": voice_embedding,
            "voice_url": voice_url
        })

        return {"message": "User registered successfully"}

    except Exception as e:
        print(f"[REGISTER ERROR] {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/login")
def login_user(user: UserLogin):
    normalized_email = user.email.strip().lower()
    email_hash = hash_email(normalized_email)

    result = supabase.table("voice_auth_data").select("*").eq("email_hash", email_hash).execute()
    if not result.data or len(result.data) == 0:
        raise HTTPException(status_code=404, detail="User not found")

    user_data = result.data[0]
    user_data["email"] = decrypt_data(user_data["email"])
    user_data["phone"] = decrypt_data(user_data["phone"])
    user_data["auth_method"] = user.auth_method

    otp = generate_otp()
    token = generate_otp_token(normalized_email, otp)

    try:
        send_otp_email(normalized_email, otp)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sending OTP email: {str(e)}")

    return {
        "message": "OTP sent to your email",
        "user": user_data,
        "token": token
    }

@app.post("/verify-otp-voice")
async def verify_otp_voice(
    email: str = Form(...),
    otp: str = Form(...),
    token: str = Form(...),
    voice: Optional[UploadFile] = File(None)
):
    normalized_email = email.strip().lower()

    if not verify_otp_token(normalized_email, otp, token):
        raise HTTPException(status_code=400, detail="Invalid or expired OTP.")

    user = get_user_by_email_hash(hash_email(normalized_email))
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    if user.get("auth_method") == "voice":
        if not voice:
            raise HTTPException(status_code=400, detail="Voice sample required.")

        voice_bytes = await voice.read()

        try:
            stored_phrase = user.get("spoken_phrase", "").strip().lower()
            if not stored_phrase:
                raise HTTPException(status_code=400, detail="No phrase stored for user.")

            if not match_spoken_phrase(voice_bytes, stored_phrase):
                raise HTTPException(status_code=401, detail="Voice biometrics do not match (phrase mismatch).")

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Voice phrase verification failed: {str(e)}")

    return {"message": "OTP and voice phrase verified successfully.", "user": user}

