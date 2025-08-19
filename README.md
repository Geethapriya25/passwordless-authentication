#  OTP + Voice Authentication System

A secure authentication system that combines OTP-based verification and Voice Biometrics to ensure stronger user identity validation.

This project integrates FastAPI (backend), Streamlit (frontend), SendGrid (email OTP), and Supabase (database + storage).
It demonstrates a multi-factor authentication system suitable for modern security applications.

## Features

### 1. Email OTP Authentication:

OTP generation & expiry (otp_utils.py)

Secure email delivery using SendGrid (email_otp.py)

OTP validation with expiry check

### 2. Voice Authentication:

Voice recording from frontend (app.py)

Voice embeddings extracted using Wav2Vec2 (SpeechBrain + Torchaudio)

Cosine similarity for voice match (voice_utils.py)

### 3. Database Integration:

Supabase for secure storage (db_utils.py)

User email is hashed before storage (hash_utils.py)

Stores OTPs, expiry, and voice embeddings

### 4. Security:

AES encryption for sensitive data (aes_utils.py)

SHA-256 hashing for emails (hash_utils.py)

Environment variables stored in .env

## Project structure:

## Project Structure

```bash
OTP AND VOICE AUTHEN/
│── common/                
│   ├── aes_utils.py       # AES encryption/decryption 
│   ├── db_utils.py        # Supabase DB helpers 
│   ├── email_otp.py       # SendGrid OTP email 
│   ├── hash_utils.py      # SHA-256 hashing 
│   ├── otp_utils.py       # OTP generation & expiry 
│   ├── voice_utils.py     # Voice embeddings & similarity 
│   └── __init__.py        
│
│── app.py                 # Streamlit frontend 
│── main.py                # FastAPI backend 
│── requirements.txt       # Python dependencies 
│── .env                   # API keys & secrets     
│── venv/                  # Python virtual environment 
```
## Tech Stack:

1. Frontend: Streamlit

2. Backend: FastAPI + Uvicorn

3. Database: Supabase

4. Email Service: SendGrid

5. Voice Processing: SpeechBrain + Torchaudio

6. Encryption & Hashing: AES, SHA-256


## Installation & Setup:

### 1. Clone the repository
git clone https://github.com/your-username/otp-voice-auth.git
cd otp-voice-auth

### 2. Create Virtual Environment
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows

### 3. Install Dependencies
pip install -r requirements.txt

### 4. Configure Environment Variables
Create a .env file in the root directory:

SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
SENDGRID_API_KEY=your_sendgrid_api_key
JWT_SECRET=your_jwt_secret

### 5. Run Backend (FastAPI)
uvicorn main:app --reload

Backend will be available at:
 http://127.0.0.1:8000

### 6. Run Frontend (Streamlit)
streamlit run app.py

Frontend will be available at:
 http://localhost:8501


## Authentication Flow:

1. User enters email → email is hashed & stored.
2. OTP is generated → sent via SendGrid → stored in DB.
3. User enters OTP → backend validates OTP & expiry.
4. User records voice → embeddings generated & stored.
5. Login attempt → voice is compared with stored embeddings.
If similarity > threshold(0.80) → authentication success.


## API Endpoints (FastAPI):

1. POST /send-otp → Send OTP to user email

2. POST /verify-otp → Verify OTP validity

3. POST /upload-voice → Upload voice sample & generate embeddings

4. POST /verify-voice → Verify voice authentication


## Security Measures:

1. OTP expiry time (default: 5 minutes)
2. Hashed email storage (SHA-256)
3. AES encryption for sensitive fields
4. Voice similarity threshold (default: 0.80)


## Future Improvements:

1. Add SMS OTP support (Twilio)
2. Improve voice anti-spoofing with ML
3. Deploy on cloud (AWS / GCP / Azure)
4. Add JWT-based session management
