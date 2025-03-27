# --- MODIFIKASI DASHBOARD RESPONSIF ---
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image

# --- PAGE CONFIG ---
st.set_page_config(page_title="Performance & Potential Dashboard", layout="wide")

# --- LOGO ---
logo = Image.open("logo.png")
st.image(logo, width=180)
st.title("\U0001F4CA Performance & Potential - HR Dashboard")

# --- LOAD DATA ---
df = pd.read_excel("Data KPI Deviasi.xlsx", sheet_name="Data KPI")
df.columns = df.columns.str.strip()

# --- SIDEBAR FILTER ---
st.sidebar.header("\U0001F50D Filter Data")
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

# --- KPI COUNT SUMMARY ---
st.subheader("\U0001F4CB Summary Metrics")
total = len(filtered_df)
summary = filtered_df['Nine Box Category'].value_counts()

# RESPONSIVE METRIC BLOCKS
if st.session_state.get("browser_width", 1000) < 768:
    st.metric("Filtered Total", total)
    st.metric("Core Players", summary.get("Core Player", 0))
    st.metric("Low Performers", summary.get("Low Performer", 0))
    st.metric("Star Players", summary.get("Star Player", 0))
else:
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Filtered Total", total)
    m2.metric("Core Players", summary.get("Core Player", 0))
    m3.metric("Low Performers", summary.get("Low Performer", 0))
    m4.metric("Star Players", summary.get("Star Player", 0))

# --- CHARTS ---
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("\U0001F9DD Z-Score Scatter: KPI vs Potential")
    fig_scatter = px.scatter(
        filtered_df,
        x="Z_KPI",
        y="Z_Potential",
        color="Nine Box Category",
        hover_data=["Nama", "Nilai KPI (%)", "Nilai Potential (%)"],
        symbol="Nine Box Category",
        size_max=10
    )
    fig_scatter.update_layout(xaxis_title="Z KPI", yaxis_title="Z Potential", height=500)
    st.plotly_chart(fig_scatter, use_container_width=True)

with col2:
    st.subheader("\U0001F4CC Nine Box Distribution")
    category_counts = filtered_df['Nine Box Category'].value_counts().reset_index()
    category_counts.columns = ['Category', 'Count']
    fig_pie = px.pie(category_counts, names="Category", values="Count", hole=0.4)
    st.plotly_chart(fig_pie, use_container_width=True)

# --- NINE BOX MATRIX ---
st.subheader("\U0001F9F1 Nine Box Matrix - Z-Score Classification")
z_high = 1
z_low = -1

def classify_nine_box(row):
    z_kpi = row['Z_KPI']
    z_pot = row['Z_Potential']
    if z_kpi >= z_high and z_pot >= z_high:
        return "Star Player"
    elif z_kpi >= 0 and z_pot >= z_high:
        return "Future Star"
    elif z_kpi <= z_low and z_pot >= z_high:
        return "Risk of Loss"
    elif z_kpi >= z_high and z_pot <= z_low:
        return "Rough Diamond"
    elif z_kpi >= 0 and z_pot <= z_low:
        return "Inconsistent"
    elif z_kpi <= z_low and z_pot <= z_low:
        return "Low Performer"
    elif z_kpi <= z_low and z_pot >= 0:
        return "Limited Growth"
    elif z_kpi >= 0 and z_pot >= 0:
        return "Core Player"
    else:
        return "High Performer"

filtered_df['Z_Category'] = filtered_df.apply(classify_nine_box, axis=1)

fig_custom = px.scatter(
    filtered_df,
    x="Z_KPI",
    y="Z_Potential",
    color="Z_Category",
    hover_data=["Nama", "Nilai KPI (%)", "Nilai Potential (%)"],
    symbol="Z_Category",
    title="Nine Box Matrix - Z-Score Classification (Legend)"
)

fig_custom.add_shape(type="line", x0=1, x1=1, y0=-3, y1=3, line=dict(color="Black", width=2, dash="dash"))
fig_custom.add_shape(type="line", x0=-1, x1=-1, y0=-3, y1=3, line=dict(color="Black", width=2, dash="dash"))
fig_custom.add_shape(type="line", x0=-3, x1=3, y0=1, y1=1, line=dict(color="Red", width=2, dash="dash"))
fig_custom.add_shape(type="line", x0=-3, x1=3, y0=-1, y1=-1, line=dict(color="Red", width=2, dash="dash"))

labels = [
    {"x": -2, "y": 2, "text": "⚠️ Risk of Loss"},
    {"x":  0, "y": 2, "text": "🌟 Future Star"},
    {"x":  2, "y": 2, "text": "⭐ Star Player"},
    {"x": -2, "y":  0, "text": "📉 Limited Growth"},
    {"x":  0, "y":  0, "text": "🔷 Core Player"},
    {"x":  2, "y":  0, "text": "📌 High Performer"},
    {"x": -2, "y": -2, "text": "❌ Low Performer"},
    {"x":  0, "y": -2, "text": "🔁 Inconsistent"},
    {"x":  2, "y": -2, "text": "💠 Rough Diamond"}
]
for label in labels:
    fig_custom.add_annotation(
        x=label["x"], y=label["y"],
        text=label["text"],
        showarrow=False,
        font=dict(size=12, color="gray")
    )

fig_custom.update_layout(xaxis_title=", yaxis_title="Potential (Z_Potential)")
st.plotly_chart(fig_custom, use_container_width=True)

# --- TABLE DATA ---
st.subheader("\U0001F4C1 Employee Detail Table")
# HINDARI .style.format karena error Unicode pada Streamlit
st.dataframe(
    filtered_df[["Nama", "Nilai KPI (%)", "Nilai Potential (%)", "Z_KPI", "Z_Potential"]],
    use_container_width=True
)

# --- LEADERBOARD ---
st.markdown("---")
st.subheader("\U0001F3C6 KPI Leaderboard")
leaderboard = filtered_df.sort_values(by="Nilai KPI (%)", ascending=False).reset_index(drop=True)
leaderboard.index += 1
st.dataframe(leaderboard[['Nama', 'Nilai KPI (%)']], use_container_width=True)

# --- FEEDBACK ---
st.markdown("---")
st.subheader("\U0001F9ED Feedback Berdasarkan Nine Box Category")

feedback_dict = {
    "Star Player": {
        "Deskripsi": "Individu dengan kinerja tinggi dan potensi tinggi. Aset strategis perusahaan.",
        "Rekomendasi": "Mentoring, proyek strategis, jalur karier ke posisi pimpinan."
    },
    "Core Player": {
        "Deskripsi": "Stabil, dapat diandalkan, loyal, dengan kontribusi konsisten.",
        "Rekomendasi": "Kembangkan fleksibilitas, dorong inisiatif, pertahankan motivasi."
    },
    "High Potential": {
        "Deskripsi": "Potensi besar namun performa belum optimal.",
        "Rekomendasi": "Coaching, penempatan proyek, tetapkan tujuan jangka pendek."
    },
    "Low Performer": {
        "Deskripsi": "Performa dan potensi rendah, perlu perhatian khusus.",
        "Rekomendasi": "Coaching intensif, rencana peningkatan 3 bulan, identifikasi hambatan."
    },
    "Enigma": {
        "Deskripsi": "Kinerja dan potensi tidak seimbang. Perlu penyesuaian penempatan.",
        "Rekomendasi": "Diskusi karier, pelatihan lanjutan, rotasi jabatan."
    }
}

selected_feedback_category = st.selectbox("Pilih Kategori untuk Lihat Feedback", list(feedback_dict.keys()))

st.markdown(f"**Deskripsi:** {feedback_dict[selected_feedback_category]['Deskripsi']}")
st.markdown(f"**Rekomendasi Tindakan:** {feedback_dict[selected_feedback_category]['Rekomendasi']}")

selected_feedback_df = df[df['Nine Box Category'] == selected_feedback_category]
st.markdown(f"**Jumlah Karyawan di Kategori Ini:** {len(selected_feedback_df)}")
st.dataframe(selected_feedback_df[['Nama', 'Nilai KPI (%)', 'Nilai Potential (%)']])
