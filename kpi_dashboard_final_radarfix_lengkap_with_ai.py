
import streamlit as st
import pandas as pd
import openai
from gtts import gTTS

# ================== CONFIG ==================
st.set_page_config(layout="wide")
openai.api_key = "YOUR-OPENAI-API-KEY"  # Ganti dengan API key kamu

# ================== LOAD DATA ==================
df = pd.read_excel("Data KPI Deviasi.xlsx", sheet_name="Data KPI")
df.columns = df.columns.str.strip()

# ================== Z-SCORE & CATEGORIZATION ==================
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

df['Nine Box Category'] = df.apply(classify_nine_box, axis=1)

# ================== UI DISPLAY ==================
st.title("📊 Dashboard KPI Interaktif + ChatGPT Voice + Voice Input")
st.dataframe(df)

# ============ AI Assistant with Voice Input ============
st.markdown("---")
st.header("🎙️ AI Assistant KPI")
st.write("Tanyakan apa saja tentang performa tim berdasarkan data KPI di atas.")

user_input = st.text_input("Masukkan pertanyaanmu di sini:")

st.components.v1.html('''
<script>
document.addEventListener("DOMContentLoaded", function() {
    const input = window.parent.document.querySelector("input[type='text']");
    window.SpeechRecognition = window.SpeechRecognition || webkitSpeechRecognition;
    const recognition = new SpeechRecognition();
    recognition.lang = "id-ID";
    recognition.onresult = function(event) {
        const transcript = event.results[0][0].transcript;
        input.value = transcript;
        input.dispatchEvent(new Event('input', { bubbles: true }));
    }
    document.addEventListener("keydown", function(event) {
        if (event.key === "v") {
            recognition.start();
        }
    });
});
</script>
<p>🎤 Tekan tombol <kbd>V</kbd> di keyboard untuk bicara langsung</p>
''', height=100)

if st.button("Tanya ChatGPT"):
    if user_input.strip() == "":
        st.warning("Masukkan pertanyaan terlebih dahulu.")
    else:
        with st.spinner("Sedang menjawab dengan AI..."):
            prompt = f"Berdasarkan data berikut:\n{df[['Nama', 'Nilai KPI (%)', 'Nilai Potential (%)', 'Nine Box Category']].to_string(index=False)}\n\nJawab pertanyaan ini:\n{user_input}"
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=prompt,
                max_tokens=300,
                temperature=0.7
            )
            gpt_answer = response.choices[0].text.strip()
            st.success("Jawaban dari AI:")
            st.markdown(f"**{gpt_answer}**")

            # Narasi suara
            tts = gTTS(text=gpt_answer, lang='id')
            audio_path = "/tmp/kpi_voice.mp3"
            tts.save(audio_path)
            st.audio(audio_path, format="audio/mp3")
