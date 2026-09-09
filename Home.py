"""Client Ledger — login gateway and executive BI landing page."""
import streamlit as st
import yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth
from style_and_pipeline import inject_style, render_hero, render_brand, render_kpis, section

st.set_page_config(
    page_title="Client Ledger | Customer Intelligence",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_style()
render_brand()

with open("config.yaml") as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config["credentials"],
    config["cookie"]["name"],
    config["cookie"]["key"],
    config["cookie"]["expiry_days"],
)

try:
    authenticator.login()
except Exception as exc:
    st.error(f"Terjadi kesalahan saat login: {exc}")

status = st.session_state.get("authentication_status")

if status is False:
    render_hero(
        "Akses ditolak",
        "Username atau password yang dimasukkan belum benar. Silakan coba kembali.",
        "SECURE ACCESS · CLIENT LEDGER",
    )
    st.error("Username atau password salah.")

elif status is None:
    render_hero(
        "Client Ledger",
        "Customer intelligence workspace untuk membaca nilai pelanggan, menemukan risiko, dan menerjemahkan RFM + K-Means menjadi keputusan yang lebih cepat.",
        "BUSINESS INTELLIGENCE · SECURE ACCESS",
    )

    render_kpis(
        [
            ("RFM Analytics", "03", "Recency · Frequency · Monetary"),
            ("Customer Segments", "04", "Actionable customer groups"),
            ("ML Pipeline", "K-Means", "Automated clustering"),
            ("Decision Flow", "4 STEPS", "Filter → Explore → Act"),
        ]
    )

    left, right = st.columns([1.35, 1])
    with left:
        section("Masuk ke workspace", "Gunakan akun administrator untuk membuka seluruh modul analitik.")
        st.markdown(
            """
            <div class='insight'>
                <b>Siap untuk presentasi.</b><br>
                Workspace dirancang untuk membawa audiens dari data mentah → insight → rekomendasi dalam alur yang sederhana.
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            """
            <div class='section-hint' style='margin-top:16px;'>
                <b>Modul tersedia setelah login:</b> Ringkasan, Detail Segmen, Data Pelanggan, dan Data Lab.
            </div>
            """,
            unsafe_allow_html=True,
        )
    with right:
        section("What you can analyze")
        for title, desc in [
            ("Customer Value", "Siapa pelanggan paling bernilai dan aktif."),
            ("Retention Risk", "Segmen yang mulai menjauh dan perlu ditangani."),
            ("Segment Strategy", "Aksi berbeda untuk tiap kelompok pelanggan."),
        ]:
            st.markdown(
                f"<div class='gloss-item'><b>{title}</b><span>{desc}</span></div>",
                unsafe_allow_html=True,
            )
    st.info("Login diperlukan untuk mengakses dashboard, detail segmen, data pelanggan, dan pipeline upload.")

else:
    name = st.session_state.get("name", "Pengguna")
    st.sidebar.markdown(f"**SESSION**  \n{name}")
    authenticator.logout("Keluar", "sidebar")
    st.sidebar.markdown("---")
    st.sidebar.caption("WORKSPACE · CUSTOMER INTELLIGENCE")

    render_hero(
        "Customer Intelligence Workspace",
        "Satu workspace untuk membaca performa pelanggan, menemukan segmen bernilai, mengidentifikasi risiko churn, dan memproses dataset baru.",
        "CLIENT LEDGER · EXECUTIVE WORKSPACE",
    )

    section("Workspace snapshot", "Pilih titik awal sesuai kebutuhan analisis.")
    render_kpis(
        [
            ("Analytics", "RFM", "Customer value model"),
            ("Segmentation", "K=4", "Actionable groups"),
            ("Risk", "At Risk", "Retention priority"),
            ("Lab", "CSV → ML", "Reusable data pipeline"),
        ]
    )

    section("Modul analitik", "Setiap modul punya tujuan yang berbeda agar alur presentasi lebih mudah diikuti.")
    modules = [
        (
            "01",
            "Ringkasan",
            "Mulai dari KPI, revenue, distribusi segmen, dan customer value map.",
            "pages/1_Ringkasan.py",
            "EXECUTIVE VIEW",
        ),
        (
            "02",
            "Detail Segmen",
            "Bandingkan profil RFM dan tentukan playbook untuk setiap kelompok.",
            "pages/2_Detail_Segmen.py",
            "SEGMENT INTELLIGENCE",
        ),
        (
            "03",
            "Data Pelanggan",
            "Cari, filter, eksplorasi, dan ekspor data pelanggan secara presisi.",
            "pages/3_Data_Pelanggan.py",
            "DATA EXPLORER",
        ),
        (
            "04",
            "Unggah Data Baru",
            "Jalankan cleaning, RFM, evaluasi cluster, dan segmentasi otomatis.",
            "pages/4_Unggah_Data_Baru.py",
            "MACHINE LEARNING LAB",
        ),
    ]

    cols = st.columns(4)
    for col, (num, title, desc, page, tag) in zip(cols, modules):
        with col:
            st.markdown(
                f"""
                <div class='module-card'>
                    <div style='display:flex;justify-content:space-between;align-items:center;gap:8px;'>
                        <div class='module-number'>{num}</div>
                        <div style='font-size:.62rem;color:#8D98A9;letter-spacing:.09em;font-weight:700;'>{tag}</div>
                    </div>
                    <div class='module-title'>{title}</div>
                    <div class='module-desc'>{desc}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.page_link(page, label=f"Buka {title}", icon="→", use_container_width=True)

    section("Recommended flow", "Untuk demo atau presentasi, gunakan urutan berikut agar ceritanya terasa natural.")
    st.markdown(
        """
        <div class='insight'>
            <b>01 · Ringkasan</b> → lihat KPI dan revenue →
            <b>02 · Detail Segmen</b> → pahami perilaku →
            <b>03 · Data Pelanggan</b> → validasi customer →
            <b>04 · Data Lab</b> → uji dataset baru.
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.caption("RFM · K-Means Clustering · Silhouette Score · Davies-Bouldin Index")
