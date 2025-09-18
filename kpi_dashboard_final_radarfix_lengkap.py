import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image

# ======================
# 🔑 Simulasi User Login
# ======================
users_db = {
    'admin': {'password': 'sikasep123'},
    'user1': {'password': 'simanis123'},
}

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

# ======================
# 🚪 Login Check
# ======================
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    login()
else:
    st.set_page_config(page_title="Performance & Potential Dashboard", layout="wide")

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

    # --- LOGO & TITLE ---
    logo = Image.open("logo.png")
    st.image(logo, width=180)
    st.title("📊 Performance & Potential - HR Dashboard")

    role = st.session_state.username if 'username' in st.session_state else None

    # --- LOAD DATA ---
    df = pd.read_excel("Data KPI Deviasi.xlsx", sheet_name="Data KPI")
    df.columns = df.columns.str.strip()

    # --- Z-Score ---
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

    # --- SIDEBAR FILTER ---
    st.sidebar.header("🔍 Filter Data")
    categories = df['Nine Box Category'].dropna().unique().tolist()
    categories.sort()
    selected_categories = st.sidebar.multiselect("Select Nine Box Category", categories, default=categories)

    names = df['Nama'].dropna().unique().tolist()
    names.sort()
    selected_names = st.sidebar.multiselect("Select Employee Name", names, default=names)

    filtered_df = df[
        (df['Nine Box Category'].isin(selected_categories)) &
        (df['Nama'].isin(selected_names))
    ]

    # --- SUMMARY ---
    st.subheader("📋 Summary Metrics")
    total = len(filtered_df)
    summary = filtered_df['Nine Box Category'].value_counts()

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Filtered Total", total)
    m2.metric("Core Players", summary.get("Core Player", 0))
    m3.metric("Low Performers", summary.get("Low Performer", 0))
    m4.metric("Star Players", summary.get("Star Player", 0))

    # --- PIE & RADAR ---
    col_pie, col_radar = st.columns(2)
    with col_pie:
        st.subheader("📌 Nine Box Distribution")
        category_counts = filtered_df['Nine Box Category'].value_counts().reset_index()
        category_counts.columns = ['Category', 'Count']
        fig_pie = px.pie(category_counts, names="Category", values="Count", hole=0.4)
        fig_pie.update_traces(textinfo='percent+label')
        fig_pie.update_layout(height=500)
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_radar:
        st.subheader("🕵️‍♂️ Radar Chart Karyawan Terpilih")
        selected_radar_name = st.selectbox("Pilih Karyawan untuk Lihat Radar", filtered_df['Nama'].unique())
        radar_data = filtered_df[filtered_df['Nama'] == selected_radar_name][['Nilai KPI (%)', 'Nilai Potential (%)']]
        radar_data.columns = ['KPI', 'Potential']
        radar_data = radar_data.iloc[0]

        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=[radar_data['KPI'], 0, radar_data['KPI']],
            theta=['KPI', 'Potential', 'KPI'],
            name='KPI',
            line=dict(color='royalblue'),
            fill='none'
        ))
        fig_radar.add_trace(go.Scatterpolar(
            r=[0, radar_data['Potential'], radar_data['Potential']],
            theta=['KPI', 'Potential', 'KPI'],
            name='Potential',
            line=dict(color='firebrick'),
            fill='none'
        ))
        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            showlegend=True,
            height=400,
            margin=dict(t=30, b=30)
        )
        st.plotly_chart(fig_radar, use_container_width=True)

    # --- BAR CHART: KPI RANKING ---
    st.subheader("📊 Peringkat Karyawan Berdasarkan KPI")
    bar_chart_df = filtered_df[['Nama', 'Nilai KPI (%)']].sort_values(by='Nilai KPI (%)', ascending=False)
    fig_bar = px.bar(bar_chart_df, x='Nama', y='Nilai KPI (%)', text='Nilai KPI (%)',
                 labels={'Nama': 'Karyawan', 'Nilai KPI (%)': 'KPI'}, height=500)
    fig_bar.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    fig_bar.update_layout(xaxis_tickangle=-45, showlegend=False, margin=dict(l=40, r=40, t=40, b=120))
    st.plotly_chart(fig_bar, use_container_width=True)

    if not bar_chart_df.empty:
        best = bar_chart_df.iloc[0]
        worst = bar_chart_df.iloc[-1]
        st.success(f"🎉 Performer Tertinggi: **{best['Nama']}** dengan KPI {best['Nilai KPI (%)']:.1f}%")
        st.error(f"⚠️ Performer Terendah: **{worst['Nama']}** dengan KPI {worst['Nilai KPI (%)']:.1f}%")

    # --- TABLE DATA ---
    st.subheader("📁 Employee Detail Table")
    st.dataframe(
        filtered_df.style.format({
            "Nilai KPI (%)": "{:.0f}",
            "Nilai Potential (%)": "{:.0f}",
            "Z_KPI": "{:.2f}",
            "Z_Potential": "{:.2f}"
        }),
        use_container_width=True
    )

    # ==============================
    # 🎙️ AI Voice Assistant KPI (SIDEBAR)
    # ==============================
    import openai
    from streamlit_webrtc import webrtc_streamer, AudioProcessorBase

    openai.api_key = st.secrets["OPENAI_API_KEY"]

    st.sidebar.markdown("---")
    st.sidebar.subheader("🤖🎤 Tanya KPI (Voice Assistant)")

    class AudioProcessor(AudioProcessorBase):
        def __init__(self):
            self.frames = []
        def recv_audio(self, frame):
            self.frames.append(frame.to_ndarray().tobytes())
            return frame

    webrtc_ctx = webrtc_streamer(
        key="voice-input",
        mode="SENDRECV",
        audio_processor_factory=AudioProcessor,
        media_stream_constraints={"audio": True, "video": False},
        rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
        sidebar=True
    )

    def transcribe_audio(audio_bytes):
        with open("input.wav", "wb") as f:
            f.write(audio_bytes)
        audio_file = open("input.wav", "rb")
        transcript = openai.audio.transcriptions.create(
            model="gpt-4o-mini-transcribe",
            file=audio_file
        )
        return transcript.text

    def ask_ai(question, df):
        context = df.to_string(index=False)
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Kamu adalah asisten HR yang menjelaskan KPI berdasarkan data berikut:\n" + context},
                {"role": "user", "content": question}
            ]
        )
        return response.choices[0].message.content

    def to_voice(text, filename="answer.mp3"):
        response = openai.audio.speech.create(
            model="gpt-4o-mini-tts",
            voice="alloy",
            input=text
        )
        with open(filename, "wb") as f:
            f.write(response.content)
        return filename

    if webrtc_ctx and webrtc_ctx.state.playing:
        if st.sidebar.button("🎤 Mulai Tanya dengan Suara"):
            audio_bytes = b"".join(webrtc_ctx.audio_processor.frames)
            if audio_bytes:
                question = transcribe_audio(audio_bytes)
                st.sidebar.write(f"**Pertanyaan:** {question}")

                answer = ask_ai(question, filtered_df)
                st.sidebar.write("**Jawaban AI:**")
                st.sidebar.success(answer)

                audio_file = to_voice(answer)
                st.sidebar.audio(audio_file, format="audio/mp3")
