import streamlit as st
from gtts import gTTS
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image

# Fungsi untuk membuat TTS
def create_tts(text, lang='id'):
    tts = gTTS(text=text, lang=lang)
    tts.save("audio.mp3")
    st.audio("audio.mp3", format='audio/mp3')

# --- LOGIN FUNCTION ---
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
                create_tts(f"Welcome {username}!")
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

    # Fungsi klasifikasi Nine Box
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

    # --- EXAMPLE TTS FOR DATA DESCRIPTION ---
    st.subheader("📋 Summary Metrics")
    total = len(df)
    summary = df['Z_Category'].value_counts()

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Filtered Total", total)
    m2.metric("Core Players", summary.get("Core Player", 0))
    m3.metric("Low Performers", summary.get("Low Performer", 0))
    m4.metric("Star Players", summary.get("Star Player", 0))

    # Create TTS for the metrics
    metrics_text = f"Total number of employees: {total}. Core Players: {summary.get('Core Player', 0)}. Low Performers: {summary.get('Low Performer', 0)}. Star Players: {summary.get('Star Player', 0)}."
    create_tts(metrics_text)

    # --- PIE & RADAR SIDE BY SIDE ---
    col_pie, col_radar = st.columns(2)

    with col_pie:
        st.subheader("📌 Nine Box Distribution")
        category_counts = df['Z_Category'].value_counts().reset_index()
        category_counts.columns = ['Category', 'Count']
        fig_pie = px.pie(category_counts, names="Category", values="Count", hole=0.4)
        fig_pie.update_traces(textinfo='percent+label')
        fig_pie.update_layout(height=500)
        st.plotly_chart(fig_pie, use_container_width=True)
        
    with col_radar:
        st.subheader("🕵️‍♂️ Radar Chart Karyawan Terpilih")
        selected_radar_name = st.selectbox("Pilih Karyawan untuk Lihat Radar", df['Nama'].unique())
        radar_data = df[df['Nama'] == selected_radar_name][['Nilai KPI (%)', 'Nilai Potential (%)']]
        radar_data.columns = ['KPI', 'Potential']
        radar_data = radar_data.iloc[0]
        radar_df = pd.DataFrame({'Aspek': radar_data.index, 'Nilai': radar_data.values})
        
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

        # Create TTS for the Radar Chart
        radar_text = f"Radar chart for {selected_radar_name} showing KPI and Potential scores."
        create_tts(radar_text)

    # --- KPI BAR CHART ---
    st.subheader("📊 Peringkat Karyawan Berdasarkan KPI")
    bar_chart_df = df[['Nama', 'Nilai KPI (%)']].sort_values(by='Nilai KPI (%)', ascending=False)
    fig_bar = px.bar(bar_chart_df, x='Nama', y='Nilai KPI (%)', text='Nilai KPI (%)', labels={'Nama': 'Karyawan', 'Nilai KPI (%)': 'KPI'}, height=500)
    fig_bar.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    fig_bar.update_layout(xaxis_tickangle=-45, showlegend=False, margin=dict(l=40, r=40, t=40, b=120))
    st.plotly_chart(fig_bar, use_container_width=True)

    # Create TTS for KPI ranking
    ranking_text = "Here is the KPI ranking for all employees based on their performance."
    create_tts(ranking_text)

    # --- OTHER SECTIONS ---

    # Add more parts of your app where you want TTS here...

