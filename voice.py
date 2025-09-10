import openai
import pyttsx3
import pandas as pd
import streamlit as st
import tempfile

# Set up OpenAI API key
openai.api_key = 'YOUR-API-KEY-HERE'  # Ganti dengan API key dari OpenAI

# Initialize pyttsx3 engine for audio
engine = pyttsx3.init()
engine.setProperty('rate', 150)  # Mengatur kecepatan suara
engine.setProperty('volume', 1)  # Mengatur volume suara

# Fungsi untuk generate file audio
def generate_audio(text):
    # Menyimpan file audio di folder /mnt/data, yang bisa diakses oleh Streamlit
    audio_file_path = '/mnt/data/kpi_narration.mp3'
    
    # Menyimpan file audio yang di-generate
    engine.save_to_file(text, audio_file_path)
    engine.runAndWait()
    
    return audio_file_path

# Streamlit Title
st.title("Interactive Voice Assistant with KPI Dashboard")

# Contoh input pengguna dan hasil dari ChatGPT
user_input = st.text_input("Tanyakan sesuatu tentang Dashboard KPI:")
if user_input:
    # Ambil response dari ChatGPT
    response = openai.Completion.create(
        engine="text-davinci-003",  # Pilih model yang diinginkan
        prompt=user_input,
        max_tokens=150
    )
    
    # Mendapatkan teks dari response
    gpt_response = response.choices[0].text.strip()
    
    # Tampilkan response di Streamlit
    st.write(f"ChatGPT's answer: {gpt_response}")
    
    # Generate audio untuk response
    audio_file_path = generate_audio(gpt_response)
    
    # Putar audio di Streamlit
    st.audio(audio_file_path, format='audio/mp3')
