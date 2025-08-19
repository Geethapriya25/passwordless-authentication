import streamlit as st
import requests
import io
import sounddevice as sd
import soundfile as sf

st.set_page_config(page_title="Voice + OTP Auth", layout="centered")
BACKEND_URL = "http://localhost:8000"

# Reset session option
if st.sidebar.button("🔃 Reset Session"):
    st.session_state.clear()
    st.rerun()

st.title("🔐 Secure Login / Registration")
menu = st.sidebar.radio("Choose Mode", ["Register", "Login"])

# Voice recording logic
def record_and_store_voice():
    duration = 5
    samplerate = 16000
    st.info("🎙️ Recording for 5 seconds...")
    recording = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1)
    sd.wait()
    st.success("✅ Voice recorded!")

    buffer = io.BytesIO()
    sf.write(buffer, recording, samplerate, format='WAV', subtype='PCM_16')
    buffer.seek(0)
    st.session_state["voice_buffer"] = buffer


def voice_record_ui():
    if "voice_buffer" not in st.session_state:
        if st.button("🎙️ Record Voice"):
            record_and_store_voice()
    else:
        st.audio(st.session_state["voice_buffer"])
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("🔄 Re-record"):
                del st.session_state["voice_buffer"]
                st.rerun()
        with col2:
            if st.button("✅ Confirm Recording"):
                st.session_state["voice_confirmed"] = True
        with col3:
            st.write("🎧 Listen and confirm")

# REGISTER  #
if menu == "Register":
    st.subheader("📋 Register")

    with st.form(key="register_form"):
        email = st.text_input("Email")
        phone = st.text_input("Phone Number")
        auth_method = st.selectbox("Authentication Method", ["otp", "voice"])
        spoken_phrase = None

        if auth_method == "voice":
            spoken_phrase = st.text_input("Passphrase (say this phrase aloud when recording)")

        st.write("### Email OTP Verification")
        send_otp = st.form_submit_button("Send OTP")

        if send_otp:
            if not email:
                st.warning("Please enter an email before sending OTP.")
            else:
                try:
                    resp = requests.post(f"{BACKEND_URL}/send-otp", json={"email": email})
                    otp_data = resp.json()
                    st.session_state["reg_token"] = otp_data["token"]
                    st.success("OTP sent to your email. Valid for 2 minutes.")
                except Exception as e:
                    st.error(f"Failed to send OTP: {str(e)}")

        otp = st.text_input("Enter OTP")
        submit = st.form_submit_button("Submit Registration")

    if auth_method == "voice":
        voice_record_ui()

    if submit:
        voice_buffer = st.session_state.get("voice_buffer", None)
        if auth_method == "voice" and not st.session_state.get("voice_confirmed", False):
            st.error("Please confirm your voice recording before submitting.")
            st.stop()

        form_data = {
            "email": email,
            "phone": phone,
            "auth_method": auth_method,
            "otp": otp,
            "token": st.session_state.get("reg_token", "")
        }
        files = {}

        if auth_method == "voice" and voice_buffer:
            form_data["spoken_phrase"] = spoken_phrase
            files["voice"] = ("voice.wav", voice_buffer, "audio/wav")

        try:
            response = requests.post(f"{BACKEND_URL}/register", data=form_data, files=files)
            if response.status_code == 200:
                st.success("✅ Registered successfully!")
                st.session_state.clear()
            else:
                st.error(response.json().get("detail", "Unknown error"))
        except Exception as e:
            st.error(f"Registration failed: {str(e)}")

# ------------------------ LOGIN ------------------------ #
elif menu == "Login":
    st.subheader("🔐 Login")

    with st.form(key="login_form"):
        email = st.text_input("Email")
        auth_method = st.selectbox("Authentication Method", ["otp", "voice"])
        send_otp = st.form_submit_button("Request OTP/Login")

        if send_otp:
            try:
                login_resp = requests.post(f"{BACKEND_URL}/login", json={"email": email, "auth_method": auth_method})
                if login_resp.status_code == 200:
                    login_data = login_resp.json()
                    st.session_state["login_token"] = login_data["token"]
                    st.success("OTP sent to your email. Valid for 2 minutes.")
                else:
                    st.error(login_resp.json().get("detail", "Login failed."))
            except Exception as e:
                st.error(f"Login request failed: {str(e)}")

    if auth_method == "voice":
        voice_record_ui()

    otp = st.text_input("Enter OTP")
    verify = st.button("Verify")

    if verify:
        if auth_method == "voice" and not st.session_state.get("voice_confirmed", False):
            st.error("Please confirm your voice recording before submitting.")
            st.stop()

        token = st.session_state.get("login_token", "")
        form_data = {
            "email": email,
            "otp": otp,
            "token": token
        }
        files = {}

        if auth_method == "voice":
            voice_buffer = st.session_state.get("voice_buffer", None)
            if voice_buffer:
                files["voice"] = ("voice.wav", voice_buffer, "audio/wav")
                endpoint = "/verify-otp-voice"
            else:
                st.error("Voice recording required.")
                st.stop()
        else:
            endpoint = "/verify-otp"

        try:
            response = requests.post(f"{BACKEND_URL}{endpoint}", data=form_data, files=files)
            if response.status_code == 200:
                st.success("✅ Login successful!")
                st.session_state.clear()
            else:
                st.error(response.json().get("detail", "Verification failed."))
        except Exception as e:
            st.error(f"Verification failed: {str(e)}")
