import streamlit as st
import google.generativeai as genai
from gtts import gTTS
import os
from io import BytesIO
from dotenv import load_dotenv
import sounddevice as sd
from scipy.io.wavfile import write
import speech_recognition as sr
import tempfile
import numpy as np

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

def record_audio(duration=5, fs=44100):
    """Record user's voice and convert to PCM WAV for recognition."""
    st.toast("🎧 Listening... Speak now!", icon="🎤")
    
    # Record audio
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='float32')
    sd.wait()
    
    # Convert to 16-bit PCM
    recording_int16 = np.int16(recording * 32767)
    
    # Save to temporary WAV file
    tmp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    write(tmp_file.name, fs, recording_int16)
    
    # Recognize audio
    with sr.AudioFile(tmp_file.name) as source:
        audio = recognizer.record(source)
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
        user_input = record_audio(duration=7)  # Adjust duration if needed
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

