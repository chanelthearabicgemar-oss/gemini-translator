import streamlit as st
from google import genai
from PIL import Image
from gtts import gTTS
import io

# --- 1. UI Setup ---
st.set_page_config(page_title="Gemini Universal Translator", page_icon="🌍", layout="wide")
st.title("🌍 Gemini Universal Translator")

# --- 2. Configuration ---
# SECURITY NOTE: Never hardcode your API key in the code. 
# Use st.secrets or an environment variable.
API_KEY = st.secrets.get("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY_HERE")

if API_KEY == "YOUR_GEMINI_API_KEY_HERE":
    st.warning("Please configure your Gemini API Key in Streamlit Secrets.")
    st.stop()

client = genai.Client(api_key=API_KEY)

# --- 3. Language Selection (Main Menu Style) ---
languages = {
    "Auto-detect": "auto",
    "English": "en",
    "Spanish": "es",
    "French": "fr",
    "German": "de",
    "Japanese": "ja",
    "Chinese": "zh",
    "Arabic": "ar",
    "Hindi": "hi",
    "Portuguese": "pt",
    "Italian": "it",
    "Russian": "ru",
    "Korean": "ko"
}

col1, col2 = st.columns(2)

with col1:
    source_lang = st.selectbox("From:", list(languages.keys()), index=0)

with col2:
    # Remove 'Auto-detect' from target options
    target_options = [l for l in languages.keys() if l != "Auto-detect"]
    target_lang = st.selectbox("To:", target_options, index=1)

st.markdown("---")

# --- 4. Input Sections ---
tab1, tab2, tab3 = st.tabs(["Text", "Image (OCR)", "Audio"])

with tab1:
    user_text = st.text_area("Enter text:", placeholder="Type or paste content here...", height=150)

with tab2:
    uploaded_image = st.file_uploader("Upload an image:", type=["jpg", "jpeg", "png"])
    if uploaded_image:
        st.image(uploaded_image, caption="Source Image", width=300)

with tab3:
    uploaded_audio = st.file_uploader("Upload audio:", type=["mp3", "wav", "m4a"])
    if uploaded_audio:
        st.audio(uploaded_audio)

# --- 5. Settings Sidebar ---
enable_voice = st.sidebar.checkbox("Enable Audio Playback", value=True)
st.sidebar.info("Using gemini-2.5-flash-lite for multimodal translation.")

# --- 6. Translation Logic ---
if st.button("Translate", type="primary"):
    # Constructing the prompt based on selection
    source_info = f"from {source_lang}" if source_lang != "Auto-detect" else "by detecting the source language automatically"
    prompt = f"Translate the following content {source_info} into {target_lang}. Provide ONLY the translated text."

    inputs = [prompt]
    
    if user_text:
        inputs.append(user_text)
    
    if uploaded_image:
        img = Image.open(uploaded_image)
        inputs.append(img)
        
    if uploaded_audio:
        audio_bytes = uploaded_audio.read()
        inputs.append({"mime_type": "audio/mpeg", "data": audio_bytes})

    if len(inputs) == 1:
        st.error("Please provide text, an image, or audio to translate.")
    else:
        with st.spinner(f"Translating to {target_lang}..."):
            try:
                response = client.models.generate_content(
                    model="gemini-2.5-flash-lite",
                    contents=inputs
                )
                
                translation = response.text
                
                # Display Results
                st.subheader(f"Result ({target_lang})")
                st.success(translation)
                
                # Text-to-Speech
                if enable_voice:
                    # gTTS uses ISO codes, we map our dictionary values here
                    lang_code = languages.get(target_lang, 'en')
                    try:
                        tts = gTTS(text=translation, lang=lang_code)
                        audio_fp = io.BytesIO()
                        tts.write_to_fp(audio_fp)
                        st.audio(audio_fp, format="audio/mp3")
                    except Exception as tts_err:
                        st.warning("Audio playback not supported for this specific language.")
                    
            except Exception as e:
                st.error(f"Translation Error: {e}")
