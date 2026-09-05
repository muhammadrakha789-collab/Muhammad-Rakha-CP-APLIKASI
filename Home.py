"""
Home.py — Gerbang login + halaman pembuka aplikasi Client Ledger.
Jalankan dengan: streamlit run Home.py
"""

import streamlit as st
import yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth

from style_and_pipeline import inject_style, render_hero

st.set_page_config(
    page_title="Client Ledger — Segmentasi Pelanggan",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_style()

# ---------- Load konfigurasi login ----------
with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
)

# ---------- Form login ----------
try:
    authenticator.login()
except Exception as e:
    st.error(f"Terjadi kesalahan saat login: {e}")

auth_status = st.session_state.get("authentication_status")

if auth_status is False:
    st.error("Username atau password salah.")
elif auth_status is None:
    render_hero(
        "Client Ledger",
        "Silakan masuk untuk mengakses dashboard segmentasi pelanggan berbasis RFM dan K-Means Clustering.",
        eyebrow="Business Intelligence · Akses Terbatas",
    )
    st.info("Gunakan kredensial yang telah diberikan oleh administrator untuk masuk.")
elif auth_status:
    name = st.session_state.get("name", "Pengguna")
    st.sidebar.markdown(f"**Masuk sebagai:** {name}")
    authenticator.logout("Keluar", "sidebar")
    st.sidebar.markdown("---")

    render_hero(
        "Selamat Datang di Client Ledger",
        "Aplikasi Business Intelligence untuk menganalisis dan mengelompokkan pelanggan e-commerce "
        "berdasarkan pola transaksi (RFM), guna mendukung strategi retensi dan akuisisi pelanggan.",
    )

    st.markdown("##### Mulai dari menu di sidebar kiri:")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("**📊 Ringkasan**")
        st.caption("Ikhtisar KPI, sebaran pelanggan, dan kontribusi revenue per segmen.")
    with col2:
        st.markdown("**🎯 Detail Segmen**")
        st.caption("Profil RFM tiap segmen dan rekomendasi strategi pemasaran.")
    with col3:
        st.markdown("**🔍 Data Pelanggan**")
        st.caption("Jelajahi dan unduh data pelanggan hasil segmentasi.")
    with col4:
        st.markdown("**📤 Unggah Data Baru**")
        st.caption("Proses data transaksi baru menjadi segmentasi otomatis.")

    st.markdown("---")
    st.caption("Metode: RFM (Recency, Frequency, Monetary) + K-Means Clustering  ·  "
               "Dikembangkan sebagai bagian dari Comprehensive Project / Tugas Akhir")
