
import streamlit as st
import pandas as pd
import openai
from gtts import gTTS
import os

# ================= CONFIG =================
openai.api_key = "YOUR-OPENAI-API-KEY"  # Ganti dengan API key lo dari OpenAI

# ================= LOAD DATA =================
df = pd.read_excel("Data KPI Deviasi (7).xlsx", sheet_name="Data KPI")
df.columns = df.columns.str.strip()

# ================= Z-SCORE =================
if 'Z_KPI' not in df.columns:
    df['Z_KPI'] = (df['Nilai KPI (%)'] - df['Nilai KPI (%)'].mean()) / df['Nilai KPI (%)'].std()
if 'Z_Potential' not in df.columns:
    df['Z_Potential'] = (df['Nilai Potential (%)'] - df['Nilai Potential (%)'].mean()) / df['Nilai Potential (%)'].std()

# ================= CLASSIFICATION =================
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

if 'Nine Box Category' not in df.columns:
    df['Nine Box Category'] = df.apply(classify_nine_box, axis=1)

# ================= STREAMLIT UI =================
st.set_page_config(layout="wide")
st.title("📊 Dashboard KPI Interaktif + ChatGPT + Suara (Streamlit Cloud Ready)")

st.subheader("📄 Data KPI")
st.dataframe(df)

# ================= INPUT PERTANYAAN =================
st.subheader("🤖 Tanyakan Apa Saja tentang KPI")
user_input = st.text_input("Masukkan pertanyaan kamu:")

if st.button("Jalankan AI Assistant"):
    with st.spinner("Sedang menganalisis data..."):
        # Kirim ke ChatGPT
        short_data = df[['Nama', 'Nilai KPI (%)', 'Nilai Potential (%)', 'Nine Box Category']].to_string(index=False)
        prompt = f"Berdasarkan data berikut:\n{short_data}\n\nJawab pertanyaan ini:\n{user_input}"
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=300,
            temperature=0.7
        )
        gpt_answer = response.choices[0].text.strip()

        st.success("Jawaban dari ChatGPT:")
        st.markdown(f"**{gpt_answer}**")

        # Generate suara dengan gTTS
        tts = gTTS(text=gpt_answer, lang='id')
        audio_file_path = "/tmp/voice_kpi_answer.mp3"
        tts.save(audio_file_path)

        st.subheader("🔊 Jawaban dalam Suara")
        st.audio(audio_file_path, format="audio/mp3")
