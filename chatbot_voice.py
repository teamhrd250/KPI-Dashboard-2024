import openai
import pyttsx3
import streamlit as st
import speech_recognition as sr

# Set up OpenAI API key
openai.api_key = 'YOUR-API-KEY-HERE'  # Ganti dengan API key yang lo dapatkan dari OpenAI

# Initialize pyttsx3 engine for audio
engine = pyttsx3.init()
engine.setProperty('rate', 150)  # Adjust the speed of speech
engine.setProperty('volume', 1)  # Set volume level to maximum

# Fungsi untuk generate file audio
def generate_audio(text):
    # Simpan file audio di folder yang bisa diakses Streamlit
    audio_file_path = '/mnt/data/kpi_narration.mp3'
    
    # Menyimpan audio
    engine.save_to_file(text, audio_file_path)
    engine.runAndWait()
    
    return audio_file_path

# Streamlit Title
st.title("Interactive Voice Assistant with KPI Dashboard")

# Create a button to start voice recognition
if st.button("Start Listening"):
    recognizer = sr.Recognizer()

    # Use microphone to listen for user input
    with sr.Microphone() as source:
        st.write("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
    
    # Try recognizing the speech
    try:
        user_input = recognizer.recognize_google(audio)
        st.write(f"You said: {user_input}")
        
        # Get response from ChatGPT API
        response = openai.Completion.create(
            engine="text-davinci-003",  # Model choice
            prompt=user_input,
            max_tokens=150
        )
        
        # Get the response text
        gpt_response = response.choices[0].text.strip()
        
        # Tampilkan jawaban ChatGPT di Streamlit
        st.write(f"ChatGPT's answer: {gpt_response}")
        
        # Generate audio untuk jawaban ChatGPT
        audio_file_path = generate_audio(gpt_response)
        
        # Putar audio di Streamlit
        st.audio(audio_file_path, format='audio/mp3')
    
    except Exception as e:
        st.write("Sorry, I could not understand your request.")
        st.write(f"Error: {e}")
