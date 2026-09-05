"""
Modul bersama: styling (tema Client Ledger) + fungsi pipeline RFM & Clustering.
Diimpor oleh Home.py dan semua file di folder pages/.
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import timedelta
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, davies_bouldin_score

# ---------- Token warna ----------
IVORY = "#F7F4EC"
INK = "#12131A"
CARD = "#FFFFFF"
NAVY_DEEP = "#0F1938"
NAVY = "#1C2B57"
TEXT = "#1A1B22"
TEXT_MUTED = "#54566A"
SIDEBAR_TEXT = "#EDEBE0"
SIDEBAR_MUTED = "#9497AA"

COLOR_MAP = {
    "Champions": "#0F1938",
    "Promising/New Active": "#2B4590",
    "At Risk": "#8A6D2E",
    "Lost/Churned": "#8C2F3B",
}
INITIAL_MAP = {"Champions": "C", "Promising/New Active": "P", "At Risk": "R", "Lost/Churned": "L"}
ORDER = ["Champions", "Promising/New Active", "At Risk", "Lost/Churned"]

INSIGHTS = {
    "Champions": "Pelanggan paling bernilai — baru bertransaksi, frekuensi tinggi, nilai belanja terbesar. "
                 "Diprioritaskan untuk program loyalitas dan akses awal produk baru.",
    "Promising/New Active": "Baru aktif dengan potensi berkembang. "
                             "Didorong lewat rekomendasi personal dan insentif transaksi kedua.",
    "At Risk": "Sebelumnya aktif, kini mulai jarang bertransaksi. "
               "Perlu kampanye keterlibatan ulang sebelum berpindah menjadi Lost.",
    "Lost/Churned": "Sudah lama tidak bertransaksi. "
                     "Kandidat kampanye win-back atau evaluasi ulang biaya retensi.",
}

GLOSSARY = [
    ("Recency (Kebaruan)", "Sudah berapa hari sejak pelanggan terakhir kali belanja. Semakin kecil angkanya, semakin baru ia aktif."),
    ("Frequency (Frekuensi)", "Berapa kali pelanggan tersebut sudah bertransaksi. Semakin sering, semakin loyal."),
    ("Monetary (Nilai)", "Total uang yang sudah dihabiskan pelanggan tersebut sepanjang periode data."),
    ("K-Means Clustering", "Metode statistik yang mengelompokkan pelanggan dengan pola R, F, M yang mirip menjadi satu segmen — tanpa ditentukan manual, algoritma yang menemukan polanya."),
]


def inject_style():
    st.markdown(f"""
    <link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600;9..144,700&family=Inter:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap" rel="stylesheet">
    <style>
        .stApp {{ background: {IVORY}; color: {TEXT}; }}
        * {{ font-family: 'Inter', sans-serif; }}

        section[data-testid="stSidebar"] {{ background: {INK}; }}
        section[data-testid="stSidebar"] label, section[data-testid="stSidebar"] p {{ color: {SIDEBAR_TEXT} !important; }}
        section[data-testid="stSidebar"] .stCaption, section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {{
            color: {SIDEBAR_MUTED} !important;
        }}
        section[data-testid="stSidebar"] h3 {{
            font-family: 'IBM Plex Mono', monospace !important; font-size: 0.72rem !important;
            text-transform: uppercase; letter-spacing: 0.16em; color: {SIDEBAR_MUTED} !important; font-weight: 500 !important;
        }}

        h1, h2, h3, h4, h5 {{ font-family: 'Fraunces', serif !important; font-weight: 600 !important; color: {TEXT} !important; }}
        p, span, label {{ color: {TEXT}; }}
        .stCaption, [data-testid="stCaptionContainer"] p {{ color: {TEXT_MUTED} !important; }}

        .hero {{ padding: 30px 36px; margin-bottom: 22px; background: {INK}; border-bottom: 3px double #3A3C4C; }}
        .hero-top {{ display: flex; justify-content: space-between; align-items: flex-start; gap: 20px; }}
        .crest {{
            width: 44px; height: 44px; border: 1.5px solid #9099B8; border-radius: 50%;
            display: flex; align-items: center; justify-content: center;
            font-family: 'Fraunces', serif; font-size: 1.2rem; color: #C9CEE0; flex-shrink: 0;
        }}

        .kpi-row {{ display: flex; border: 1px solid {INK}; background: {CARD}; flex-wrap: wrap; }}
        .kpi-cell {{ flex: 1; min-width: 160px; padding: 18px 22px; border-right: 1px solid #E3E0D4; }}
        .kpi-cell:last-child {{ border-right: none; }}
        .kpi-label {{
            font-family: 'IBM Plex Mono', monospace; font-size: 0.64rem; text-transform: uppercase;
            letter-spacing: 0.1em; color: {TEXT_MUTED}; margin-bottom: 10px;
        }}
        .kpi-value {{
            font-family: 'IBM Plex Mono', monospace; font-size: 1.5rem; font-weight: 600; color: {NAVY_DEEP};
            font-variant-numeric: tabular-nums;
        }}
        .kpi-sub {{ font-size: 0.72rem; color: {TEXT_MUTED}; margin-top: 4px; }}

        .exec-summary {{
            background: {CARD}; border: 1px solid {INK}; border-left: 4px solid {NAVY_DEEP};
            padding: 20px 24px; margin: 20px 0; font-size: 0.94rem; line-height: 1.75; color: {TEXT};
        }}
        .exec-summary b {{ color: {NAVY_DEEP}; }}

        .panel-title {{
            font-family: 'IBM Plex Mono', monospace; font-size: 0.68rem; text-transform: uppercase;
            letter-spacing: 0.12em; color: {TEXT_MUTED}; margin: 26px 0 6px; display: flex; align-items: center; gap: 10px;
        }}
        .panel-title::after {{ content: ""; flex: 1; height: 1px; background: #D8D4C4; }}
        .panel-hint {{ font-size: 0.82rem; color: {TEXT_MUTED}; margin-bottom: 14px; font-style: italic; }}

        .chart-frame {{ background: {CARD}; border: 1px solid {INK}; padding: 18px 20px; }}

        .seg-card {{ display: flex; gap: 16px; padding: 18px 4px; border-bottom: 1px solid #DDD9CB; }}
        .seg-badge {{
            width: 40px; height: 40px; border-radius: 50%; flex-shrink: 0; background: {CARD};
            border: 2px solid var(--seg-color); display: flex; align-items: center; justify-content: center;
            font-family: 'Fraunces', serif; font-weight: 700; font-size: 1.05rem; color: var(--seg-color);
        }}
        .seg-card b {{ font-size: 1.12rem; font-family: 'Fraunces', serif; color: {TEXT}; }}
        .seg-card .desc {{ color: {TEXT_MUTED}; font-size: 0.86rem; margin-top: 4px; display: block; line-height: 1.55; }}
        .seg-stat {{ font-family: 'IBM Plex Mono', monospace; font-size: 0.72rem; color: {TEXT_MUTED}; margin-top: 6px; display: flex; gap: 14px; flex-wrap: wrap; }}
        .seg-stat b {{ color: {TEXT}; }}

        .gloss-item {{ padding: 10px 0; border-bottom: 1px solid #E3E0D4; }}
        .gloss-item b {{ font-family: 'Fraunces', serif; font-size: 1rem; color: {NAVY_DEEP}; }}
        .gloss-item span {{ display: block; color: {TEXT_MUTED}; font-size: 0.85rem; margin-top: 3px; line-height: 1.55; }}

        div[data-testid="stMetric"] {{ background: {CARD}; padding: 10px; border: 1px solid {INK}; }}

        .stTabs [data-baseweb="tab-list"] {{ gap: 0; border-bottom: 1px solid {INK}; }}
        .stTabs [data-baseweb="tab"] {{
            color: {TEXT_MUTED}; background: transparent; font-family: 'IBM Plex Mono', monospace;
            font-size: 0.76rem; text-transform: uppercase; letter-spacing: 0.08em; padding: 0 18px 12px;
        }}
        .stTabs [aria-selected="true"] {{ color: {NAVY_DEEP} !important; border-bottom: 2px solid {NAVY_DEEP} !important; }}
        .stTabs [data-baseweb="tab-highlight"] {{ background-color: {NAVY_DEEP} !important; }}

        span[data-baseweb="tag"], div[data-baseweb="tag"] {{
            background-color: #1C1E29 !important; border: 1px solid #9099B8 !important; border-radius: 0 !important;
        }}
        span[data-baseweb="tag"] *, div[data-baseweb="tag"] * {{
            color: {SIDEBAR_TEXT} !important; fill: {SIDEBAR_TEXT} !important; background-color: transparent !important;
        }}

        div[data-baseweb="select"] > div {{
            background-color: #1C1E29 !important; border: 1px solid #3A3C4C !important; border-radius: 0 !important;
        }}
        div[data-baseweb="select"] > div:hover {{ border-color: #9099B8 !important; }}
        div[data-baseweb="popover"] ul {{ background-color: {INK} !important; border: 1px solid #3A3C4C !important; }}
        div[data-baseweb="popover"] li {{ color: {SIDEBAR_TEXT} !important; }}
        div[data-baseweb="popover"] li:hover {{ background-color: #1C1E29 !important; }}

        section[data-testid="stSidebar"] input {{
            background-color: #1C1E29 !important; color: {SIDEBAR_TEXT} !important; border: 1px solid #3A3C4C !important;
            border-radius: 0 !important;
        }}

        [data-testid="stDataFrame"] {{ border: 1px solid {INK}; }}

        .stDownloadButton button, .stButton button {{
            background: transparent !important; color: {TEXT} !important; border: 1px solid {INK} !important;
            border-radius: 0 !important; font-family: 'IBM Plex Mono', monospace !important;
            font-size: 0.74rem !important; letter-spacing: 0.06em; text-transform: uppercase;
        }}
        .stDownloadButton button:hover, .stButton button:hover {{ background: {INK} !important; color: #fff !important; }}

        section[data-testid="stSidebar"] .stButton button {{
            color: {SIDEBAR_TEXT} !important; border: 1px solid #9099B8 !important;
        }}
        section[data-testid="stSidebar"] .stButton button:hover {{ background: #1C1E29 !important; }}

        .streamlit-expanderHeader {{
            background: {CARD} !important; border: 1px solid {INK} !important; font-family: 'IBM Plex Mono', monospace !important;
            font-size: 0.78rem !important; text-transform: uppercase; letter-spacing: 0.06em; color: {TEXT} !important;
        }}
        .streamlit-expanderContent {{ background: {CARD} !important; border: 1px solid {INK} !important; border-top: none !important; }}

        [data-testid="stMetricValue"] {{ font-family: 'IBM Plex Mono', monospace !important; color: {NAVY_DEEP} !important; }}

        hr {{ border-color: #DDD9CB !important; }}
        ::-webkit-scrollbar {{ width: 8px; height: 8px; }}
        ::-webkit-scrollbar-thumb {{ background: {INK}; }}
    </style>
    """, unsafe_allow_html=True)


def base_layout(**overrides):
    layout = dict(
        paper_bgcolor=CARD, plot_bgcolor=CARD,
        font=dict(color=TEXT, family="Inter, sans-serif", size=12),
        xaxis=dict(gridcolor="#EDEAE0", zerolinecolor="#EDEAE0", color=TEXT_MUTED),
        yaxis=dict(gridcolor="#EDEAE0", zerolinecolor="#EDEAE0", color=TEXT_MUTED),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=TEXT_MUTED)),
        margin=dict(t=10, l=10, r=10, b=10),
    )
    layout.update(overrides)
    return layout


def render_hero(title, subtitle, eyebrow="Client Ledger · Business Intelligence"):
    st.markdown(f"""
    <div class="hero">
        <div class="hero-top">
            <div>
                <div style="font-family:'IBM Plex Mono',monospace;font-size:0.66rem;text-transform:uppercase;
                            letter-spacing:0.22em;color:#9099B8;margin-bottom:10px;">
                    {eyebrow}
                </div>
                <h1 style="font-size:2rem;margin:0 0 10px;color:#F7F5EF !important;-webkit-text-fill-color:#F7F5EF !important;">
                    {title}
                </h1>
                <p style="color:#C4C6D2 !important;margin:0;font-size:0.9rem;max-width:600px;line-height:1.65;">
                    {subtitle}
                </p>
            </div>
            <div class="crest">◆</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ================= PIPELINE RFM + CLUSTERING (dipakai halaman Upload Data) =================

def clean_transactions(df: pd.DataFrame) -> pd.DataFrame:
    """Menyesuaikan nama kolom & membersihkan data transaksi mentah (format ala Online Retail II)."""
    rename_map = {
        'Invoice': 'InvoiceNo', 'InvoiceNo': 'InvoiceNo',
        'Price': 'UnitPrice', 'UnitPrice': 'UnitPrice',
        'Customer ID': 'CustomerID', 'CustomerID': 'CustomerID',
    }
    df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})
    df.columns = df.columns.str.strip()

    required = {'InvoiceNo', 'InvoiceDate', 'Quantity', 'UnitPrice', 'CustomerID'}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Kolom wajib tidak ditemukan: {', '.join(missing)}")

    df = df.dropna(subset=['CustomerID'])
    df = df[~df['InvoiceNo'].astype(str).str.startswith('C')]
    df = df[(df['Quantity'] > 0) & (df['UnitPrice'] > 0)]
    df = df.drop_duplicates()
    df['CustomerID'] = df['CustomerID'].astype(int)
    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
    df['TotalPrice'] = df['Quantity'] * df['UnitPrice']
    return df


def compute_rfm(df: pd.DataFrame) -> pd.DataFrame:
    snapshot_date = df['InvoiceDate'].max() + timedelta(days=1)
    rfm = df.groupby('CustomerID').agg({
        'InvoiceDate': lambda x: (snapshot_date - x.max()).days,
        'InvoiceNo': 'nunique',
        'TotalPrice': 'sum'
    }).reset_index()
    rfm.columns = ['CustomerID', 'Recency', 'Frequency', 'Monetary']
    return rfm


def run_clustering(rfm: pd.DataFrame, k: int = 4):
    rfm_log = rfm[['Recency', 'Frequency', 'Monetary']].apply(lambda x: np.log1p(x))
    scaler = StandardScaler()
    rfm_scaled = scaler.fit_transform(rfm_log)

    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    rfm = rfm.copy()
    rfm['Cluster'] = kmeans.fit_predict(rfm_scaled)

    sil = silhouette_score(rfm_scaled, rfm['Cluster'])
    db = davies_bouldin_score(rfm_scaled, rfm['Cluster'])

    # Label otomatis berdasarkan urutan rata-rata Monetary & Recency per cluster
    stats = rfm.groupby('Cluster').agg(Recency=('Recency', 'mean'), Monetary=('Monetary', 'mean')).reset_index()
    stats = stats.sort_values('Monetary', ascending=False).reset_index(drop=True)
    rank_to_label = {}
    labels_by_value_rank = ["Champions", "Promising/New Active", "At Risk", "Lost/Churned"]
    # Urutkan juga mempertimbangkan recency agar label lebih masuk akal
    stats_sorted = stats.sort_values(['Monetary', 'Recency'], ascending=[False, True]).reset_index(drop=True)
    for i, row in stats_sorted.iterrows():
        label = labels_by_value_rank[i] if i < len(labels_by_value_rank) else f"Segmen {i+1}"
        rank_to_label[row['Cluster']] = label

    rfm['Segmen'] = rfm['Cluster'].map(rank_to_label)
    return rfm, sil, db


def find_optimal_k(rfm: pd.DataFrame, k_range=range(2, 8)):
    rfm_log = rfm[['Recency', 'Frequency', 'Monetary']].apply(lambda x: np.log1p(x))
    scaler = StandardScaler()
    rfm_scaled = scaler.fit_transform(rfm_log)

    results = []
    for k in k_range:
        km = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = km.fit_predict(rfm_scaled)
        results.append({
            "k": k,
            "inertia": km.inertia_,
            "silhouette": silhouette_score(rfm_scaled, labels),
            "davies_bouldin": davies_bouldin_score(rfm_scaled, labels),
        })
    return pd.DataFrame(results)
