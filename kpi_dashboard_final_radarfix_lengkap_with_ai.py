import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
import openai
from gtts import gTTS
import os

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
# =============== MAIN CONTENT ===============
else:
    st.set_page_config(page_title="Dashboard KPI + Voice AI", layout="wide")
    logo = Image.open("logo.png")
    st.image(logo, width=180)
    st.title("📊 Dashboard KPI Interaktif + ChatGPT Voice + Voice Input")

    # --- LOAD DATA ---
    df = pd.read_excel("Data KPI Deviasi.xlsx", sheet_name="Data KPI")
    df.columns = df.columns.str.strip()

    df['Z_KPI'] = (df['Nilai KPI (%)'] - df['Nilai KPI (%)'].mean()) / df['Nilai KPI (%)'].std()
    df['Z_Potential'] = (df['Nilai Potential (%)'] - df['Nilai Potential (%)'].mean()) / df['Nilai Potential (%)'].std()

    # --- KATEGORI Z_SCORE ---
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

    # --- TAMPILKAN TABEL SAJA SEBAGAI DEMO ---
    st.dataframe(df[['Nama', 'Nilai KPI (%)', 'Nilai Potential (%)', 'Z_Category']], use_container_width=True)

    # =============== AI ASSISTANT VOICE ===============
    st.markdown("---")
    st.header("🎙️ AI Assistant KPI Berbasis Suara")
    st.caption("🗣️ Klik tombol di bawah ini untuk bicara (Gunakan Google Chrome).")

    # Web Speech API untuk input suara
    st.components.v1.html("""
        <script>
        const input = window.parent.document.querySelector('input[type="text"]');
        const micBtn = document.createElement("button");
        micBtn.innerHTML = "🎤 Mulai Bicara";
        micBtn.style.fontSize = "16px";
        micBtn.style.padding = "10px 20px";
        micBtn.style.marginBottom = "10px";
        micBtn.style.backgroundColor = "#4CAF50";
        micBtn.style.color = "white";
        micBtn.style.border = "none";
        micBtn.style.borderRadius = "5px";
        micBtn.style.cursor = "pointer";
        input.parentElement.prepend(micBtn);

        window.SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        const recognition = new SpeechRecognition();
        recognition.lang = 'id-ID';

        micBtn.onclick = () => recognition.start();
        recognition.onresult = function(event) {
            const result = event.results[0][0].transcript;
            input.value = result;
            input.dispatchEvent(new Event('input', { bubbles: true }));
        };
        </script>
    """, height=0)

    user_question = st.text_input("Pertanyaan Anda (otomatis dari suara):")

    if st.button("Tanya AI") and user_question:
        try:
            openai.api_key = os.getenv("OPENAI_API_KEY") or "YOUR-API-KEY"
            prompt = f"""Berikut data karyawan:\n{df[['Nama', 'Nilai KPI (%)', 'Nilai Potential (%)', 'Z_Category']].to_string(index=False)}\n\nJawab secara profesional: {user_question}"""
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=prompt,
                max_tokens=300,
                temperature=0.5
            )
            answer = response.choices[0].text.strip()
            st.success("Jawaban AI:")
            st.write(answer)

            tts = gTTS(answer, lang='id')
            audio_file = "/tmp/jawaban_ai.mp3"
            tts.save(audio_file)
            st.audio(audio_file)
        except Exception as e:
            st.error(f"Error: {e}")
