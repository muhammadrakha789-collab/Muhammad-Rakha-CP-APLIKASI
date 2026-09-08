"""Client Ledger — login gateway and professional BI landing page."""
import streamlit as st
import yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth
from style_and_pipeline import inject_style, render_hero, render_brand, section

st.set_page_config(page_title="Client Ledger | Customer Intelligence", page_icon="◆", layout="wide", initial_sidebar_state="expanded")
inject_style(); render_brand()
with open('config.yaml') as file: config=yaml.load(file,Loader=SafeLoader)
authenticator=stauth.Authenticate(config['credentials'],config['cookie']['name'],config['cookie']['key'],config['cookie']['expiry_days'])
try: authenticator.login()
except Exception as e: st.error(f"Terjadi kesalahan saat login: {e}")
status=st.session_state.get('authentication_status')

if status is False:
    render_hero("Akses ditolak","Username atau password yang dimasukkan belum benar. Silakan coba kembali.","SECURE ACCESS · CLIENT LEDGER")
    st.error("Username atau password salah.")
elif status is None:
    render_hero("Client Ledger","Customer intelligence dashboard untuk memahami nilai, perilaku, dan risiko pelanggan melalui RFM + K-Means.","BUSINESS INTELLIGENCE · SECURE ACCESS")
    c1,c2,c3=st.columns(3)
    c1.metric("RFM Analytics","01","Recency · Frequency · Monetary")
    c2.metric("Customer Segments","04","Actionable customer groups")
    c3.metric("ML Pipeline","K-Means","Automated clustering")
    section("Masuk ke workspace","Gunakan akun administrator yang telah dikonfigurasi untuk membuka seluruh modul analitik.")
    st.info("Login diperlukan untuk mengakses dashboard, detail segmen, data pelanggan, dan pipeline upload.")
else:
    name=st.session_state.get('name','Pengguna')
    st.sidebar.markdown(f"**SESSION**  \n{name}")
    authenticator.logout("Keluar","sidebar")
    st.sidebar.markdown("---")
    render_hero("Customer Intelligence Workspace","Satu workspace untuk membaca performa pelanggan, menemukan segmen bernilai, mengidentifikasi risiko churn, dan memproses dataset baru.")
    section("Modul analitik","Klik salah satu tombol modul di bawah untuk membuka halaman analitik.")
    modules=[
        ("01","Ringkasan","KPI, revenue, distribusi segmen, dan customer value map.","pages/1_Ringkasan.py"),
        ("02","Detail Segmen","Profil RFM dan strategi untuk setiap kelompok pelanggan.","pages/2_Detail_Segmen.py"),
        ("03","Data Pelanggan","Cari, filter, eksplorasi, dan ekspor data segmentasi.","pages/3_Data_Pelanggan.py"),
        ("04","Unggah Data Baru","Cleaning, RFM, evaluasi cluster, dan segmentasi otomatis.","pages/4_Unggah_Data_Baru.py")]
    cols=st.columns(4)
    for col,(num,title,desc,page) in zip(cols,modules):
        with col:
            st.markdown(f"<div class='module-card'><div class='module-number'>{num}</div><div class='module-title'>{title}</div><div class='module-desc'>{desc}</div></div>",unsafe_allow_html=True)
            st.page_link(page,label=f"Buka {title}",icon="→",use_container_width=True)
    st.markdown("<div class='insight'><b>Alur sistem:</b> Filter → Explore → Understand → Act. Hasil clustering diterjemahkan menjadi insight pelanggan dan rekomendasi yang dapat digunakan untuk pengambilan keputusan.</div>",unsafe_allow_html=True)
    st.caption("RFM · K-Means Clustering · Silhouette Score · Davies-Bouldin Index")
