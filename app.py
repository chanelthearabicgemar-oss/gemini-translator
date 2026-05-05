import streamlit as st
from google import genai
from PIL import Image
from gtts import gTTS
import io

# --- 1. UI Setup ---
st.set_page_config(page_title="Gemini Universal Translator", page_icon="🌍")
st.title("🌍 Gemini Universal Translator")
st.markdown("Translate Text, Images, and Voice using **Gemini 2.5 Flash**")

# --- 2. Configuration ---
# You can also use st.sidebar.text_input for the key to keep it private
import streamlit as st
API_KEY = st.secrets[AIzaSyDxqRiWWLs7qRjUJetZARlgxrFjnujZZXQ]

if API_KEY == "YOUR_GEMINI_API_KEY_HERE":
    st.warning("Please enter your Gemini API Key in the code.")
    st.stop()

client = genai.Client(api_key=API_KEY)

# --- 3. App Sidebar (Settings) ---
st.sidebar.header("Settings")
target_language = st.sidebar.selectbox(
    "Target Language", 
    ["Spanish", "French", "German", "Japanese", "Chinese", "Arabic", "Hindi"]
)
enable_voice = st.sidebar.checkbox("Generate Voice Output", value=True)

# --- 4. Input Sections ---
tab1, tab2, tab3 = st.tabs(["Text", "Image (Pic-to-Text)", "Audio (Voice-to-Voice)"])

with tab1:
    user_text = st.text_area("Enter text to translate:", placeholder="Type something here...")

with tab2:
    uploaded_image = st.file_uploader("Upload an image with text:", type=["jpg", "jpeg", "png"])
    if uploaded_image:
        st.image(uploaded_image, caption="Uploaded Image", use_container_width=True)

with tab3:
    uploaded_audio = st.file_uploader("Upload an audio file:", type=["mp3", "wav", "m4a"])
    if uploaded_audio:
        st.audio(uploaded_audio)

# --- 5. Translation Logic ---
if st.button("Translate Everything"):
    inputs = [f"Translate the provided content into {target_language}. Provide ONLY the translation."]
    
    # Check what inputs are available
    if user_text:
        inputs.append(user_text)
    
    if uploaded_image:
        img = Image.open(uploaded_image)
        inputs.append(img)
        
    if uploaded_audio:
        audio_bytes = uploaded_audio.read()
        inputs.append({"mime_type": "audio/mpeg", "data": audio_bytes})

    if len(inputs) == 1:
        st.error("Please provide some text, an image, or audio first!")
    else:
        with st.spinner("Gemini is thinking..."):
            try:
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=inputs
                )
                
                translation = response.text
                st.success(f"**Translation ({target_language}):**")
                st.write(translation)
                
                # Handle Text-to-Speech
                if enable_voice:
                    tts = gTTS(translation)
                    audio_fp = io.BytesIO()
                    tts.write_to_fp(audio_fp)
                    st.audio(audio_fp, format="audio/mp3")
                    
            except Exception as e:
                st.error(f"Error: {e}")
