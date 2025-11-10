import streamlit as st
import google.generativeai as genai
from gtts import gTTS
import speech_recognition as sr
import os
from io import BytesIO
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Initialize Gemini model
model = genai.GenerativeModel("gemini-2.5-flash")

st.set_page_config(page_title="VoiceBot by Anurag", page_icon="🎙️", layout="centered")

# --- Page Title ---
st.markdown(
    "<h1 style='text-align: center;'>🎙️ AI Assistant</h1>", 
    unsafe_allow_html=True
)
st.markdown("<p style='text-align:center;'>Speak or type — I’ll reply instantly in voice & text!</p>", unsafe_allow_html=True)
st.markdown("---")

recognizer = sr.Recognizer()

def record_audio():
    """Record user's voice until silence, with safe timeout handling."""
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.8)
        st.toast("🎧 Listening... Speak now!", icon="🎤")
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
        except sr.WaitTimeoutError:
            st.toast("⏱️ No speech detected. Try again!", icon="⚠️")
            return None

    try:
        text = recognizer.recognize_google(audio)
        st.toast(f"🗣️ You said: {text}", icon="💬")
        return text
    except sr.UnknownValueError:
        st.toast("❌ Sorry, I couldn't understand your voice.", icon="⚠️")
    except sr.RequestError:
        st.toast("⚠️ Speech recognition service unavailable.", icon="🚨")
    return None

def speak_text(text):
    """Convert text to speech and auto-play."""
    tts = gTTS(text=text, lang="en")
    audio_bytes = BytesIO()
    tts.write_to_fp(audio_bytes)
    audio_bytes.seek(0)
    st.audio(audio_bytes.read(), format="audio/mp3", autoplay=True)

# --- Input Section ---
st.markdown("<h3 style='text-align: center;'>💬 Ask me anything!</h3>", unsafe_allow_html=True)

# Center the button and text input
col1, col2, col3 = st.columns([1, 2, 1])

user_input = None

with col2:
    # Centered Speak button
    st.markdown("<div style='text-align:center;'>", unsafe_allow_html=True)
    if st.button("🎤 Speak", key="mic"):
        user_input = record_audio()
    st.markdown("</div>", unsafe_allow_html=True)

    # OR separator
    st.markdown("<p style='text-align:center; margin-top:10px;'>────────── or ──────────</p>", unsafe_allow_html=True)

    # Centered text input
    text_input = st.text_input("Type your question here:", placeholder="e.g. What is AI?")
    if text_input.strip():
        user_input = text_input

# --- Response Section ---
if user_input:
    with st.spinner("🤔 Thinking..."):
        response = model.generate_content(user_input)
        answer = response.text.strip() if response and response.text else "Hmm, not sure about that."

    st.markdown(f"<p style='font-size:18px;'><b>🤖 Bot:</b> {answer}</p>", unsafe_allow_html=True)
    speak_text(answer)

st.markdown("---")
st.caption("Made by **Anurag Chaudhary** for 100x AI Agent Assessment 🚀")
