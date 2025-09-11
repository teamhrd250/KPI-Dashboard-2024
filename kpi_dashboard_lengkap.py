import openai
import pyttsx3
import pandas as pd
import streamlit as st
import speech_recognition as sr
from PIL import Image

# Set up OpenAI API key
openai.api_key = 'YOUR-API-KEY-HERE'  # Ganti dengan API key yang lo dapatkan dari OpenAI

# Inisialisasi pyttsx3 untuk audio
engine = pyttsx3.init()
engine.setProperty('rate', 150)  # Kecepatan suara
engine.setProperty('volume', 1)  # Volume suara

# Fungsi untuk generate file audio
def generate_audio(text):
    audio_file_path = '/mnt/data/kpi_narration.mp3'  # Simpan di folder yang bisa diakses Streamlit
    engine.save_to_file(text, audio_file_path)
    engine.runAndWait()
    return audio_file_path

# Simulasi data user yang terdaftar
users_db = {
    'admin': {'password': 'sikasep123'},
    'user1': {'password': 'simanis123'},
}

# Fungsi untuk login
def login():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        logo = Image.open("logo.png")
        st.image(logo, width=200)
        st.markdown("## Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if st.button("Login"):
            if username in users_db and users_db[username]['password'] == password:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success(f"Welcome {username}!")
            else:
                st.error("Invalid credentials, please try again.")

# Mengecek status login sebelum menampilkan konten
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    login()  # Menampilkan form login jika belum login
else:
    st.set_page_config(page_title="Performance & Potential Dashboard", layout="wide")

    # --- PAGE CONFIG ---
    # --- CUSTOM STYLE ---
    st.markdown("""
        <style>
        .main {padding: 1rem !important;}
        .stContainer {
            background-color: #ffffff;
            padding: 1.5rem;
            border-radius: 16px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.05);
            margin-bottom: 1.5rem;
        }
        @media (max-width: 768px) {
            h1, h2, h3, .stMarkdown { font-size: 90% !important; }
        }
        </style>
    """, unsafe_allow_html=True)

    # --- LOGO PERUSAHAAN ---
    logo = Image.open("logo.png")
    st.image(logo, width=180)
    st.title("📊 Performance & Potential - HR Dashboard")

    # --- LOAD DATA ---
    df = pd.read_excel("Data KPI Deviasi.xlsx", sheet_name="Data KPI")
    df.columns = df.columns.str.strip()

    df['Z_KPI'] = (df['Nilai KPI (%)'] - df['Nilai KPI (%)'].mean()) / df['Nilai KPI (%)'].std()
    df['Z_Potential'] = (df['Nilai Potential (%)'] - df['Nilai Potential (%)'].mean()) / df['Nilai Potential (%)'].std()

    def classify_nine_box(row):
        z_kpi = row['Z_KPI']
        z_pot = row['Z_Potential']
        if z_kpi >= 1 and z_pot >= 1:
            return "⭐ Star Player"
        elif z_kpi >= 0 and z_pot >= 1:
            return "🌟 Future Star"
        elif z_kpi <= -1 and z_pot >= 1:
            return "⚠️ Risk of Loss"
        elif z_kpi >= 1 and z_pot <= -1:
            return "💠 Rough Diamond"
        elif z_kpi >= 0 and z_pot <= -1:
            return "🔁 Inconsistent"
        elif z_kpi <= -1 and z_pot <= -1:
            return "❌ Low Performer"
        elif z_kpi <= -1 and z_pot >= 0:
            return "📉 Limited Growth"
        elif z_kpi >= 0 and z_pot >= 0:
            return "🔷 Core Player"
        else:
            return "📌 High Performer"

    df['Z_Category'] = df.apply(classify_nine_box, axis=1)

    # --- Tampilkan Penjelasan Suara dari ChatGPT ---
    if st.button("Explain Core Players"):
        response = openai.Completion.create(
            engine="text-davinci-003",  # Pilih model yang digunakan
            prompt="Explain who the Core Players are in the KPI dashboard and why they belong to this category.",
            max_tokens=150
        )
        
        # Ambil jawaban dari ChatGPT
        gpt_response = response.choices[0].text.strip()
        
        # Tampilkan jawaban dari ChatGPT
        st.write(f"ChatGPT's explanation: {gpt_response}")
        
        # Generate audio untuk penjelasan dari ChatGPT
        audio_file_path = generate_audio(gpt_response)
        
        # Putar audio di Streamlit
        st.audio(audio_file_path, format='audio/mp3')
