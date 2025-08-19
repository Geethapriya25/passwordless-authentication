# db_utils.py
import os
from supabase import create_client
from dotenv import load_dotenv
from common.hash_utils import hash_email

# Load environment variables
load_dotenv()

# Initialize Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
if not SUPABASE_URL or not SUPABASE_KEY:
    raise Exception("SUPABASE_URL or SUPABASE_KEY is missing in .env")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def insert_user_to_supabase(user_data: dict):
    """Insert user data into 'voice_auth_data' table"""
    try:
        result = supabase.table("voice_auth_data").insert(user_data).execute()
        print("[DEBUG] Supabase insert response:", result)
        return result
    except Exception as e:
        print(f"[ERROR insert_user_to_supabase]: {e}")
        raise e

def get_user_by_email_hash(email_hash: str):
    """Fetch a user by hashed email from 'voice_auth_data' table"""
    try:
        result = supabase.table("voice_auth_data").select("*").eq("email_hash", email_hash).execute()
        if result.data and len(result.data) > 0:
            return result.data[0]
        return None
    except Exception as e:
        print(f"[ERROR get_user_by_email_hash]: {e}")
        return None

def update_user_voice_features(email: str, mfcc_vector: list):
    """Update user's voice_features in 'voice_auth_data' table"""
    try:
        email_hash = hash_email(email.strip().lower())
        response = supabase.table("voice_auth_data").update({
            "voice_features": mfcc_vector
        }).eq("email_hash", email_hash).execute()
        return response
    except Exception as e:
        print(f"[ERROR update_user_voice_features]: {e}")
        return None
