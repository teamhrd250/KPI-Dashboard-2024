import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image

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
    # Cek Role
    role = st.session_state.username if 'username' in st.session_state else None

    # Load data & Z-Score untuk admin
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


    if role == 'admin':
        st.subheader("📌 Nine Box Distribution")
        category_counts = df['Nine Box Category'].value_counts().reset_index()
        category_counts.columns = ['Category', 'Count']
        fig_pie = px.pie(category_counts, names="Category", values="Count", hole=0.4)
        fig_pie.update_traces(textinfo='percent+label')
        fig_pie.update_layout(height=500)
        st.plotly_chart(fig_pie, use_container_width=True)

        st.subheader("🧱 Nine Box Matrix - Z-Score Classification")
        fig_custom = px.scatter(
            df,
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
        st.plotly_chart(fig_custom, use_container_width=True)
        
        st.subheader("📋 Ringkasan Penyebaran")

        kategori_list = [
            "⭐ Star Player", "🌟 Future Star", "⚠️ Risk of Loss", "💠 Rough Diamond",
            "🔁 Inconsistent", "❌ Low Performer", "📉 Limited Growth",
            "🔷 Core Player", "📌 High Performer"
        ]

        for kategori in kategori_list:
            jumlah = df[df['Z_Category'] == kategori].shape[0]
            st.markdown(f"- **{kategori}**: {jumlah if jumlah > 0 else '-'}")

        
        
        
        st.subheader("🧭 Feedback per Kategori")
        feedback_dict = {
            "⭐ Star Player": {
                "Deskripsi": "Karyawan performa tinggi dan potensi tinggi. Aset utama perusahaan dan kandidat kuat untuk posisi strategis.",
                "Pencapaian": "- Mencapai KPI di atas target\n- Menjadi role model dan penggerak tim",
                "Rekomendasi": "- Proyek strategis\n- Program pengembangan kepemimpinan\n- Penghargaan dan jalur karier cepat"
            },
            "🌟 Future Star": {
                "Deskripsi": "Potensi tinggi, performa masih berkembang. Membutuhkan pembinaan untuk naik level.",
                "Pencapaian": "- Antusias belajar\n- Potensi kepemimpinan terlihat",
                "Rekomendasi": "- Coaching rutin\n- Proyek pengembangan\n- Exposure ke tantangan"
            },
            "⚠️ Risk of Loss": {
                "Deskripsi": "Potensi tinggi namun tidak engaged. Bisa resign jika tidak ditangani.",
                "Pencapaian": "- Memiliki skill unggul\n- Riwayat kinerja bagus di masa lalu",
                "Rekomendasi": "- Career discussion\n- Penguatan engagement\n- Identifikasi hambatan kerja"
            },
            "💠 Rough Diamond": {
                "Deskripsi": "Performa tinggi, potensi belum dimaksimalkan. Perlu eksplorasi peran.",
                "Pencapaian": "- Produktif\n- Handal di bidang teknis",
                "Rekomendasi": "- Pelatihan soft skill\n- Mentoring lintas fungsi\n- Rotasi kerja"
            },
            "🔁 Inconsistent": {
                "Deskripsi": "Performa naik turun. Perlu bimbingan dan target yang jelas.",
                "Pencapaian": "- Kadang over-achieve\n- Kadang di bawah standar",
                "Rekomendasi": "- Fokus jangka pendek\n- Coaching performa\n- Review berkala"
            },
            "❌ Low Performer": {
                "Deskripsi": "Performa dan potensi rendah. Perlu penanganan intensif.",
                "Pencapaian": "- Tidak konsisten\n- Sering buat kesalahan",
                "Rekomendasi": "- PIP\n- Pelatihan dasar\n- Evaluasi ulang penempatan"
            },
            "📉 Limited Growth": {
                "Deskripsi": "Potensi rendah, performa sedang. Stabil tapi tidak berkembang.",
                "Pencapaian": "- Tugas rutin diselesaikan\n- Jarang inisiatif",
                "Rekomendasi": "- Penugasan sesuai kapasitas\n- Supervisi berkala\n- Pelatihan sederhana"
            },
            "🔷 Core Player": {
                "Deskripsi": "Performa dan potensi stabil. Tulang punggung operasional.",
                "Pencapaian": "- Menyelesaikan tugas tepat waktu\n- Bisa diandalkan",
                "Rekomendasi": "- Reward regular\n- Pelatihan tambahan\n- Dorongan skill lanjutan"
            },
            "📌 High Performer": {
                "Deskripsi": "Performa tinggi, potensi belum maksimal.",
                "Pencapaian": "- Hasil kerja sangat baik\n- Belum eksplorasi lebih luas",
                "Rekomendasi": "- Tantangan baru\n- Proyek pengembangan\n- Observasi minat & skill lain"
            }
        }

        selected = st.selectbox("Pilih Kategori", list(feedback_dict.keys()), key="admin_feedback_selector")

        st.markdown(f"### 🔸 Kategori: {selected}")
        st.markdown(f"#### 📝 Deskripsi\n{feedback_dict[selected]['Deskripsi']}")
        st.markdown(f"#### 🏅 Pencapaian Umum\n{feedback_dict[selected]['Pencapaian']}")
        st.markdown(f"#### ✅ Tindakan yang Disarankan\n{feedback_dict[selected]['Rekomendasi']}")

        feedback_dict = {
            "⭐ Star Player": {
                "Deskripsi": "Individu dengan performa tinggi dan potensi tinggi. Mereka adalah top performer yang siap dipromosikan ke level lebih tinggi.",
                "Pencapaian": "Selalu mencapai KPI di atas target, proaktif dalam pengambilan keputusan, menjadi role model dalam tim.",
                "Rekomendasi": "Tawarkan proyek strategis, mentoring, dan jalur karier menuju kepemimpinan. Berikan penghargaan formal."
            },
            "🌟 Future Star": {
                "Deskripsi": "Potensi tinggi namun performa masih dalam tahap berkembang. Butuh dorongan dan pembinaan untuk menjadi Star Player.",
                "Pencapaian": "Antusias belajar, berkontribusi dalam ide dan solusi, menunjukan inisiatif meski hasil belum konsisten.",
                "Rekomendasi": "Berikan coaching rutin, program pengembangan kepemimpinan, dan exposure ke proyek besar."
            },
            "⚠️ Risk of Loss": {
                "Deskripsi": "Karyawan dengan potensi tinggi tapi performa sedang/rendah. Rentan kehilangan motivasi dan bisa resign.",
                "Pencapaian": "Pernah tampil cemerlang di masa lalu, memiliki kemampuan tinggi, namun tampak tidak engaged.",
                "Rekomendasi": "Lakukan diskusi pengembangan karier, perkuat engagement, beri dukungan dan dengarkan keluhan."
            },
            "💠 Rough Diamond": {
                "Deskripsi": "Performa tinggi tapi potensi belum tergali. Bisa jadi karena tidak cocok di peran saat ini.",
                "Pencapaian": "Sangat produktif dan andal di pekerjaan teknis, namun belum banyak terlibat dalam hal strategis.",
                "Rekomendasi": "Tawarkan pelatihan soft skill, mentoring lintas divisi, dan pertimbangkan rotasi kerja."
            },
            "🔁 Inconsistent": {
                "Deskripsi": "Performa naik turun dan tidak stabil. Kadang sangat baik, kadang jauh di bawah ekspektasi.",
                "Pencapaian": "Hasil kerja tidak konsisten, tergantung kondisi lingkungan/tim.",
                "Rekomendasi": "Lakukan evaluasi target rutin, tentukan fokus kerja, dan dampingi dengan coaching performance."
            },
            "❌ Low Performer": {
                "Deskripsi": "Performa dan potensi rendah. Perlu penanganan segera dan intensif.",
                "Pencapaian": "Sering tidak memenuhi ekspektasi, banyak melakukan kesalahan mendasar.",
                "Rekomendasi": "Lakukan performance improvement plan (PIP), pelatihan dasar, atau pertimbangkan penempatan ulang."
            },
            "📉 Limited Growth": {
                "Deskripsi": "Potensi rendah, performa sedang. Biasanya cukup stabil tapi tidak berkembang.",
                "Pencapaian": "Menjalankan tugas rutin tanpa inovasi, jarang memberi kontribusi tambahan.",
                "Rekomendasi": "Berikan tugas yang sesuai kapasitas, dukung dengan pelatihan sederhana dan pengawasan berkala."
            },
            "🔷 Core Player": {
                "Deskripsi": "Karyawan andalan yang stabil dan bisa diandalkan, baik dari segi performa maupun attitude.",
                "Pencapaian": "Menyelesaikan pekerjaan tepat waktu, menjadi bagian penting dalam operasional harian.",
                "Rekomendasi": "Pertahankan dengan penghargaan, beri pelatihan tambahan, dan siapkan jenjang karier pelan-pelan."
            },
            "📌 High Performer": {
                "Deskripsi": "Performa tinggi namun potensi ke depan belum terlihat maksimal.",
                "Pencapaian": "Selalu menyelesaikan target dengan baik, namun belum menunjukkan kemampuan untuk berkembang lebih luas.",
                "Rekomendasi": "Berikan tantangan baru, libatkan dalam project development, dan observasi minat serta skill lainnya."
            }
        }

        
        st.markdown(f"**Deskripsi:** {feedback_dict[selected]['Deskripsi']}")
        st.markdown(f"**Pencapaian Umum:** {feedback_dict[selected]['Pencapaian']}")
        st.markdown(f"**Tindakan yang Disarankan:** {feedback_dict[selected]['Rekomendasi']}")

        feedback_dict = {
            "⭐ Star Player": {
                "Deskripsi": "Individu dengan kinerja tinggi dan potensi tinggi. Aset strategis perusahaan.",
                "Rekomendasi": "Mentoring, proyek strategis, jalur karier ke posisi pimpinan."
            },
            "🌟 Future Star": {
                "Deskripsi": "Potensi tinggi namun performa belum optimal.",
                "Rekomendasi": "Coaching rutin, penugasan proyek menantang, tetapkan tujuan pengembangan."
            },
            "⚠️ Risk of Loss": {
                "Deskripsi": "Potensi tinggi, performa rendah. Berisiko kehilangan motivasi.",
                "Rekomendasi": "Diskusi karier, penguatan engagement, identifikasi hambatan kerja."
            },
            "💠 Rough Diamond": {
                "Deskripsi": "Performa tinggi, potensi belum tergali sepenuhnya.",
                "Rekomendasi": "Pembinaan intensif, pelatihan lanjutan, rotasi kerja untuk eksplorasi potensi."
            },
            "🔁 Inconsistent": {
                "Deskripsi": "Performa tidak stabil, fluktuasi hasil kerja signifikan.",
                "Rekomendasi": "Penetapan target jangka pendek, coaching performa, review berkala."
            },
            "❌ Low Performer": {
                "Deskripsi": "Performa dan potensi rendah. Membutuhkan perhatian khusus.",
                "Rekomendasi": "Rencana perbaikan kinerja (PIP), evaluasi kemampuan dan peran kerja."
            },
            "📉 Limited Growth": {
                "Deskripsi": "Potensi rendah, kinerja stagnan atau menurun.",
                "Rekomendasi": "Tugaskan pekerjaan berulang yang sesuai, pantau motivasi, pelatihan dasar."
            },
            "🔷 Core Player": {
                "Deskripsi": "Stabil dan andal. Karyawan inti yang menjaga ritme kerja tim.",
                "Rekomendasi": "Pertahankan motivasi, beri penghargaan, dan dorong peningkatan skill."
            },
            "📌 High Performer": {
                "Deskripsi": "Kinerja tinggi, potensi sedang. Sangat produktif dalam peran saat ini.",
                "Rekomendasi": "Berikan tantangan tambahan, pertimbangkan kenaikan tanggung jawab."
            }
        }

        
        st.markdown(f"**Deskripsi:** {feedback_dict[selected]['Deskripsi']}")
        st.markdown(f"**Rekomendasi Tindakan:** {feedback_dict[selected]['Rekomendasi']}")

        feedback_dict = {
            "⭐ Star Player": "Kinerja & potensi tinggi. Aset strategis.",
            "🌟 Future Star": "Potensi tinggi, perlu pengembangan performa.",
            "⚠️ Risk of Loss": "Potensi tinggi, performa rendah. Risiko keluar.",
            "💠 Rough Diamond": "Performa tinggi, potensi belum tergali.",
            "🔁 Inconsistent": "Performa tidak konsisten. Perlu stabilisasi.",
            "❌ Low Performer": "Performa dan potensi rendah.",
            "📉 Limited Growth": "Potensi rendah, perlu peningkatan kinerja.",
            "🔷 Core Player": "Performa & potensi stabil.",
            "📌 High Performer": "Performa tinggi, potensi sedang."
        }

        selected = st.selectbox("Pilih Kategori", kategori_list)
        st.markdown(f"**Feedback:** {feedback_dict[selected]}")

        st.subheader("📤 Export Ringkasan ke PDF")
        from fpdf import FPDF
        if st.button("Download PDF Ringkasan"):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt="Ringkasan Penyebaran Karyawan", ln=1, align="C")
            pdf.ln(10)
            for kategori in kategori_list:
                jumlah = df[df['Z_Category'] == kategori].shape[0]
                txt = f"{kategori}: {jumlah if jumlah > 0 else '-'}"
                pdf.cell(200, 10, txt=txt, ln=1)
            pdf.output("/mnt/data/ringkasan_kpi_admin.pdf")
            with open("/mnt/data/ringkasan_kpi_admin.pdf", "rb") as f:
                st.download_button("📥 Download Ringkasan PDF", f, file_name="ringkasan_kpi_admin.pdf", mime="application/pdf")

        st.stop()

    df = pd.read_excel("Data KPI Deviasi.xlsx", sheet_name="Data KPI")
    df.columns = df.columns.str.strip()

    # --- Perhitungan Z-Score ---
    df['Z_KPI'] = (df['Nilai KPI (%)'] - df['Nilai KPI (%)'].mean()) / df['Nilai KPI (%)'].std()
    df['Z_Potential'] = (df['Nilai Potential (%)'] - df['Nilai Potential (%)'].mean()) / df['Nilai Potential (%)'].std()

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

    # Terapkan klasifikasi Nine Box
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

    # --- KPI COUNT SUMMARY ---
    st.subheader("📋 Summary Metrics")
    total = len(filtered_df)
    summary = filtered_df['Nine Box Category'].value_counts()

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Filtered Total", total)
    m2.metric("Core Players", summary.get("Core Player", 0))
    m3.metric("Low Performers", summary.get("Low Performer", 0))
    m4.metric("Star Players", summary.get("Star Player", 0))

    # --- PIE & RADAR SIDE BY SIDE ---
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

    # --- PREVIEW PDF SETELAH PIE & RADAR CHART ---
    st.markdown("### 📄 Hasil Psikotest")
    
    import os
    pdf_path = f"psikotest_files/{selected_radar_name}.pdf"
    st.markdown(f"<div style='text-align: center;'>📄 File: {pdf_path}</div>", unsafe_allow_html=True)

    try:
        with open(pdf_path, "rb") as f:
            st.markdown(
                "<div style='width: 60%; margin: auto; text-align: center;'>",
                unsafe_allow_html=True
            )
            st.download_button(
                label="📥 Klik untuk Lihat atau Download Hasil Psikotest",
                data=f,
                file_name=f"{selected_radar_name}.pdf",
                mime="application/pdf"
            )
            st.markdown("</div>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning("⚠️ File psikotest tidak ditemukan untuk karyawan ini.")

    # --- BAR CHART: KPI RANKING ---
    st.subheader("📊 Peringkat Karyawan Berdasarkan KPI")
    bar_chart_df = filtered_df[['Nama', 'Nilai KPI (%)']].sort_values(by='Nilai KPI (%)', ascending=False)
    fig_bar = px.bar(bar_chart_df, x='Nama', y='Nilai KPI (%)', text='Nilai KPI (%)',
                 labels={'Nama': 'Karyawan', 'Nilai KPI (%)': 'KPI'}, height=500)
    fig_bar.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    fig_bar.update_layout(xaxis_tickangle=-45, showlegend=False, margin=dict(l=40, r=40, t=40, b=120))
    st.plotly_chart(fig_bar, use_container_width=True)

    # --- NOTIFIKASI USER FRIENDLY ---
    if not bar_chart_df.empty:
        best = bar_chart_df.iloc[0]
        worst = bar_chart_df.iloc[-1]
        st.success(f"🎉 Performer Tertinggi: **{best['Nama']}** dengan KPI {best['Nilai KPI (%)']:.1f}%")
        st.error(f"⚠️ Performer Terendah: **{worst['Nama']}** dengan KPI {worst['Nilai KPI (%)']:.1f}%")

    # --- Z-SCORE TABLE FRIENDLY ---
    st.subheader("📐 Z-Score Tabel Ringkas")
    st.dataframe(
       filtered_df[['Nama', 'Z_KPI', 'Z_Potential']]
       .sort_values(by='Z_KPI', ascending=False)
       .style.format({"Z_KPI": "{:.2f}", "Z_Potential": "{:.2f}"}),
        use_container_width=True
)

    # --- CUSTOM NINE BOX MATRIX ---
    st.subheader("🧱 Nine Box Matrix - Z-Score Classification")

    z_high = 1
    z_low = -1

    def classify_nine_box(row):
        z_kpi = row['Z_KPI']
        z_pot = row['Z_Potential']
        if z_kpi >= z_high and z_pot >= z_high:
            return "⭐ Star Player"
        elif z_kpi >= 0 and z_pot >= z_high:
            return "🌟 Future Star"
        elif z_kpi <= z_low and z_pot >= z_high:
            return "⚠️ Risk of Loss"
        elif z_kpi >= z_high and z_pot <= z_low:
            return "💠 Rough Diamond"
        elif z_kpi >= 0 and z_pot <= z_low:
            return "🔁 Inconsistent"
        elif z_kpi <= z_low and z_pot <= z_low:
            return "❌ Low Performer"
        elif z_kpi <= z_low and z_pot >= 0:
            return "📉 Limited Growth"
        elif z_kpi >= 0 and z_pot >= 0:
            return "🔷 Core Player"
        else:
            return "📌 High Performer"

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
        fig_custom.add_annotation(x=label["x"], y=label["y"], text=label["text"], showarrow=False, font=dict(size=12, color="gray"))

    fig_custom.update_layout(xaxis_title="Performance (Z_KPI)", yaxis_title="Potential (Z_Potential)")
    st.plotly_chart(fig_custom, use_container_width=True)

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

    # --- LEADERBOARD RANKING ---
    st.markdown("---")
    st.subheader("🏆 KPI Leaderboard")
    leaderboard = filtered_df.sort_values(by="Nilai KPI (%)", ascending=False).reset_index(drop=True)
    leaderboard.index += 1
    st.dataframe(leaderboard[['Nama', 'Nilai KPI (%)']], use_container_width=True)

    # --- FEEDBACK PER KATEGORI ---
    st.markdown("---")
    st.subheader("🧭 Feedback Berdasarkan Nine Box Category")

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
        },
        "Inconsistent": {
            "Deskripsi": "Performa yang tidak konsisten, perlu perhatian untuk mencapai stabilitas.",
            "Rekomendasi": "Penetapan tujuan yang jelas, mentoring intensif, pengelolaan proyek dengan lebih terstruktur."
        },
        "Rough Diamond": {
            "Deskripsi": "Memiliki potensi besar namun membutuhkan pembinaan dan pemolesan lebih lanjut.",
            "Rekomendasi": "Pembinaan intensif, pelatihan keterampilan, dan kesempatan untuk menunjukkan kemampuan."
        },
        "Limited Growth": {
            "Deskripsi": "Karyawan dengan pertumbuhan terbatas dan perlu bantuan untuk mencapai potensi mereka.",
            "Rekomendasi": "Fokus pada perencanaan karier, memberikan proyek yang dapat meningkatkan keterampilan."
        },
        "Risk of Loss": {
            "Deskripsi": "Karyawan yang memiliki risiko kehilangan motivasi atau kinerja rendah yang perlu perhatian serius.",
            "Rekomendasi": "Intervensi segera, coaching dan pemantauan intensif, serta pengaturan ulang tujuan."
        },
        "High Performer": {
            "Deskripsi": "Karyawan dengan kinerja sangat baik, sering kali menjadi contoh bagi rekan kerja lainnya.",
            "Rekomendasi": "Memberikan tantangan yang lebih besar, promosi, dan peluang pengembangan lanjutan."
        }
    }

    selected_feedback_category = st.selectbox("Pilih Kategori untuk Lihat Feedback", list(feedback_dict.keys()))
    st.markdown(f"**Deskripsi:** {feedback_dict[selected_feedback_category]['Deskripsi']}")
    st.markdown(f"**Rekomendasi Tindakan:** {feedback_dict[selected_feedback_category]['Rekomendasi']}")
    selected_feedback_df = df[df['Nine Box Category'] == selected_feedback_category]
    st.markdown(f"**Jumlah Karyawan di Kategori Ini:** {len(selected_feedback_df)}")
    st.dataframe(selected_feedback_df[['Nama', 'Nilai KPI (%)', 'Nilai Potential (%)']])

    # --- PENJELASAN Z-SCORE & NINE BOX ---
    st.markdown("---")
    st.subheader("📘 Penjelasan Z-Score & Nine Box Matrix")

    # 1. Tampilkan gambar ilustrasi
    try:
        explanation_img = Image.open("image.png")
        st.image(explanation_img, caption="Penjelasan Z-Score & Nine Box Classification", use_container_width=True)
    except:
        st.warning("Gambar penjelasan tidak ditemukan. Pastikan 'image.png' ada di folder yang sama.")

    # 2. Tampilkan juga versi teks (markdown)
    st.markdown("""
    ### 🧮 Rumus Z-Score
    Z-Score digunakan untuk menstandarisasi nilai agar bisa dibandingkan secara relatif dalam distribusi data. Rumus:

    **Z = (X - μ) / σ**

    - **X** = Nilai individu (KPI atau Potential)
    - **μ (mu)** = Rata-rata dari seluruh nilai
    - **σ (sigma)** = Standar deviasi dari nilai tersebut

    Z-Score menunjukkan seberapa jauh nilai seseorang dari rata-rata, dalam satuan standar deviasi.

    ---

    ### 🔲 Matriks Nine Box (Z_KPI vs Z_Potential)

    |               | Z_Potential < -1 | -1 ≤ Z_Potential ≤ 1 | Z_Potential > 1 |
    |---------------|------------------|------------------------|-----------------|
    | **Z_KPI < -1** | ❌ Low Performer | 📉 Limited Growth      | ⚠️ Risk of Loss |
    | **-1 ≤ Z_KPI ≤ 1** | 🔁 Inconsistent | 🔷 Core Player        | 🌟 Future Star  |
    | **Z_KPI > 1**  | 💠 Rough Diamond | 📌 High Performer      | ⭐ Star Player   |

    ---

    Kombinasi nilai **Z_KPI** dan **Z_Potential** akan menempatkan seseorang dalam salah satu dari 9 kotak (Nine Box Grid) untuk membantu pengambilan keputusan pengembangan SDM.
    """)
