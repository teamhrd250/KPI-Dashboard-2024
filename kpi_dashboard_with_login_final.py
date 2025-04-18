
import streamlit as st
import pandas as pd
import numpy as np
import hashlib
import os

# ===== AUTH DATA =====
USERS = {
    "admin": {"pwd": "admin123", "role": "admin"},
    "user1": {"pwd": "user1234", "role": "user"}
}

def _hash(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()

def login():
    st.sidebar.image("logo.png", width=200)
    st.sidebar.markdown("## Login to KPI Dashboard")
    user = st.sidebar.text_input("Username")
    pw = st.sidebar.text_input("Password", type="password")
    login_btn = st.sidebar.button("Login")

    if login_btn:
        if user in USERS and _hash(pw) == _hash(USERS[user]["pwd"]):
            st.session_state.auth = True
            st.session_state.user = user
            st.session_state.role = USERS[user]["role"]
            st.sidebar.success(f"Welcome, {user}!")
        else:
            st.sidebar.error("Username / password salah")

if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    login()
    st.stop()

# ========== MAIN DASHBOARD STARTS HERE ==========
st.title("📊 KPI Performance & Potential Dashboard")
st.caption("Sakeudap nuju di evaluasi KPI na, nyunkeun kesabaranna, hanupis cuy")

role = st.session_state.role
st.markdown(f"### Mode: `{role.upper()}`")

# Load data (contoh)
df = pd.read_excel("Data KPI Deviasi.xlsx")
st.dataframe(df)

# Conditional rendering based on role
if role == "user":
    st.subheader("Update KPI Data")
    uploaded = st.file_uploader("Upload File Baru (Excel)")
    if uploaded:
        df_new = pd.read_excel(uploaded)
        st.success("Data berhasil diupload dan ditampilkan di bawah:")
        st.dataframe(df_new)
        # Simpan atau proses lebih lanjut bisa ditambahkan di sini
else:
    st.info("Mode admin hanya dapat melihat data (read-only).")
