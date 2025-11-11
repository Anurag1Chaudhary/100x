import streamlit as st
import google.generativeai as genai
from gtts import gTTS
from io import BytesIO
from dotenv import load_dotenv
import os
import tempfile
import speech_recognition as sr
from streamlit_mic_recorder import mic_recorder
from pydub import AudioSegment
import base64
from streamlit.components.v1 import html

# --- Load environment variables ---
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# --- Initialize Gemini model ---
model = genai.GenerativeModel("gemini-2.5-flash")

# --- Streamlit Page Setup ---
st.set_page_config(page_title="VoiceBot by Anurag", page_icon="🎙️", layout="centered")

# --- Page Header ---
st.markdown(
    "<h1 style='text-align:center;'>🎙️ AI Assistant</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='text-align:center;'>Speak or type — I’ll reply instantly in voice & text!</p>",
    unsafe_allow_html=True,
)
st.markdown("---")

recognizer = sr.Recognizer()


# --- Audio Transcription ---
def transcribe_audio(audio_bytes):
    """Convert WebM/OGG to WAV and transcribe using Google Speech Recognition."""
    try:
        tmp_input = tempfile.NamedTemporaryFile(delete=False, suffix=".webm")
        tmp_input.write(audio_bytes)
        tmp_input.flush()

        tmp_output = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        sound = AudioSegment.from_file(tmp_input.name, format="webm")
        sound.export(tmp_output.name, format="wav")

        with sr.AudioFile(tmp_output.name) as source:
            audio = recognizer.record(source)
            text = recognizer.recognize_google(audio)
            st.toast(f"🗣️ You said: {text}")
            return text

    except sr.UnknownValueError:
        st.toast("❌ Couldn't understand your voice.", icon="⚠️")
    except sr.RequestError:
        st.toast("⚠️ Speech recognition service unavailable.", icon="🚨")
    except Exception as e:
        st.error(f"Error while processing audio: {e}")

    return None


# --- Speak Function (Auto Voice Playback) ---
def speak_text(text):
    """Convert text to speech and auto-play persistently across reruns."""
    try:
        tts = gTTS(text=text, lang="en")
        audio_bytes = BytesIO()
        tts.write_to_fp(audio_bytes)
        audio_bytes.seek(0)
        audio_base64 = base64.b64encode(audio_bytes.read()).decode()

        audio_html = f"""
        <audio id="botVoice" autoplay style="display:none;">
            <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
        </audio>
        <script>
        const a = document.getElementById('botVoice');
        if (a) {{
            a.play().catch(() => {{
                setTimeout(() => a.play(), 500);
            }});
        }}
        </script>
        """

        html(audio_html, height=0, width=0)

    except Exception as e:
        st.error(f"⚠️ Error in voice playback: {e}")


# --- Input Section ---
st.markdown("<h3 style='text-align:center;'>💬 Ask me anything!</h3>", unsafe_allow_html=True)
col1, col2, col3 = st.columns([1, 2, 1])
user_input = None

with col2:
    st.markdown("<div style='text-align:center;'>🎤 <b>Speak below:</b></div>", unsafe_allow_html=True)
    audio = mic_recorder(
        start_prompt="🎙️ Start Speaking",
        stop_prompt="🛑 Stop Recording",
        just_once=True,
        key="recorder"
    )

    if audio and "bytes" in audio:
        st.toast("🎧 Processing your voice...")
        user_input = transcribe_audio(audio["bytes"])

    st.markdown("<p style='text-align:center;'>────────── or ──────────</p>", unsafe_allow_html=True)

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
