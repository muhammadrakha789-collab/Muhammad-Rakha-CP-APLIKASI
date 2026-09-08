"""Shared UI styling and RFM + K-Means pipeline for Client Ledger."""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import timedelta
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, davies_bouldin_score

BG = "#07090D"
SURFACE = "#0D1118"
SURFACE_2 = "#111722"
BORDER = "#202938"
TEXT = "#F4F7FB"
MUTED = "#8D98A9"
ACCENT = "#8B5CF6"
ACCENT_2 = "#22D3EE"
SUCCESS = "#34D399"
WARNING = "#FBBF24"
DANGER = "#FB7185"
WHITE = "#FFFFFF"
CARD = SURFACE

COLOR_MAP = {"Champions":"#8B5CF6","Promising/New Active":"#22D3EE","At Risk":"#FBBF24","Lost/Churned":"#FB7185"}
INITIAL_MAP = {"Champions":"C","Promising/New Active":"P","At Risk":"R","Lost/Churned":"L"}
ORDER = ["Champions","Promising/New Active","At Risk","Lost/Churned"]
INSIGHTS = {
    "Champions":"Pelanggan paling bernilai dan paling aktif. Prioritaskan loyalitas, VIP treatment, early access, dan cross-sell.",
    "Promising/New Active":"Pelanggan aktif dengan ruang pertumbuhan. Dorong transaksi berikutnya melalui rekomendasi personal dan insentif ringan.",
    "At Risk":"Pelanggan yang mulai menjauh. Gunakan re-engagement, reminder, personal offer, dan komunikasi berbasis histori.",
    "Lost/Churned":"Pelanggan dengan recency tinggi. Jalankan win-back secara selektif dan ukur biaya retensi terhadap potensi nilai.",
}
GLOSSARY = [
    ("Recency","Jumlah hari sejak transaksi terakhir. Semakin kecil, semakin baru aktivitas pelanggan."),
    ("Frequency","Jumlah transaksi unik pelanggan. Semakin tinggi, semakin sering pelanggan berbelanja."),
    ("Monetary","Total nilai transaksi pelanggan selama periode data."),
    ("K-Means","Algoritma clustering yang mengelompokkan pelanggan berdasarkan kemiripan pola RFM."),
    ("Silhouette Score","Ukuran kualitas pemisahan cluster. Nilai lebih tinggi umumnya menunjukkan cluster yang lebih jelas."),
    ("Davies-Bouldin","Ukuran kemiripan antar-cluster. Nilai lebih rendah umumnya lebih baik."),
]

def inject_style():
    st.markdown(f"""
    <link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap" rel="stylesheet">
    <style>
    .stApp,[data-testid="stAppViewContainer"]{{background:{BG};color:{TEXT}}} [data-testid="stHeader"]{{background:transparent}} *{{font-family:'DM Sans',sans-serif}}
    h1,h2,h3,h4{{font-family:'Space Grotesk',sans-serif!important;color:{TEXT}!important}} .stCaption,[data-testid="stCaptionContainer"] p{{color:{MUTED}!important}}
    section[data-testid="stSidebar"]{{background:linear-gradient(180deg,#0A0D13,#07090D);border-right:1px solid {BORDER}}} section[data-testid="stSidebar"]>div{{padding-top:1.2rem}}
    section[data-testid="stSidebar"] label,section[data-testid="stSidebar"] p{{color:#D7DEE9!important}} section[data-testid="stSidebar"] input{{background:{SURFACE_2}!important;color:{TEXT}!important;border:1px solid {BORDER}!important;border-radius:10px!important}}
    div[data-baseweb="select"]>div{{background:{SURFACE_2}!important;border:1px solid {BORDER}!important;border-radius:10px!important}} div[data-baseweb="popover"] ul{{background:{SURFACE_2}!important;border:1px solid {BORDER}!important}} div[data-baseweb="popover"] li{{color:{TEXT}!important}}
    span[data-baseweb="tag"],div[data-baseweb="tag"]{{background:#1B2230!important;border:1px solid #334155!important;border-radius:7px!important}} span[data-baseweb="tag"] *,div[data-baseweb="tag"] *{{color:{TEXT}!important;background:transparent!important}}
    .brand{{display:flex;align-items:center;gap:11px;padding:6px 2px 22px}} .brand-mark{{width:38px;height:38px;border-radius:11px;background:linear-gradient(135deg,{ACCENT},{ACCENT_2});display:flex;align-items:center;justify-content:center;color:white;font-weight:800;box-shadow:0 8px 30px rgba(139,92,246,.25)}} .brand-title{{font-family:'Space Grotesk';font-weight:700;font-size:1.05rem;color:{TEXT}}}.brand-sub{{font-size:.68rem;color:{MUTED};margin-top:2px}}
    .hero{{position:relative;overflow:hidden;padding:34px 38px;margin:0 0 24px;border:1px solid {BORDER};border-radius:18px;background:radial-gradient(circle at 90% 15%,rgba(139,92,246,.20),transparent 34%),radial-gradient(circle at 70% 100%,rgba(34,211,238,.10),transparent 28%),linear-gradient(135deg,#101621,#0A0D13);box-shadow:0 18px 50px rgba(0,0,0,.22)}} .hero h1{{font-size:2.15rem!important;margin:0 0 9px}} .hero p{{color:#AAB4C4!important;max-width:720px;line-height:1.65;margin:0}} .eyebrow{{color:{ACCENT_2};font-size:.68rem;font-weight:700;text-transform:uppercase;letter-spacing:.16em;margin-bottom:9px}} .hero-badge{{position:absolute;right:28px;top:28px;width:48px;height:48px;border:1px solid #334155;border-radius:14px;display:flex;align-items:center;justify-content:center;color:{ACCENT_2};background:rgba(255,255,255,.025);font-weight:800}}
    .kpi-grid{{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px;margin:0 0 24px}} .kpi{{background:linear-gradient(180deg,{SURFACE_2},{SURFACE});border:1px solid {BORDER};border-radius:14px;padding:18px;min-height:105px;box-shadow:0 10px 25px rgba(0,0,0,.12)}} .kpi-label{{color:{MUTED};font-size:.68rem;text-transform:uppercase;letter-spacing:.09em;font-weight:700}} .kpi-value{{font-family:'Space Grotesk';color:{TEXT};font-size:1.55rem;font-weight:700;margin-top:8px}} .kpi-sub{{color:{MUTED};font-size:.72rem;margin-top:4px}}
    .section-title{{display:flex;align-items:center;gap:10px;color:{TEXT};font-family:'Space Grotesk';font-size:.86rem;font-weight:700;text-transform:uppercase;letter-spacing:.08em;margin:28px 0 9px}} .section-title:after{{content:'';height:1px;background:{BORDER};flex:1}} .section-hint{{color:{MUTED};font-size:.78rem;margin-bottom:13px}}
    .chart-frame{{background:{SURFACE};border:1px solid {BORDER};border-radius:14px;padding:14px;box-shadow:0 10px 28px rgba(0,0,0,.13)}} .insight{{background:linear-gradient(135deg,rgba(139,92,246,.12),rgba(34,211,238,.04));border:1px solid #29334A;border-left:3px solid {ACCENT};border-radius:12px;padding:17px 19px;margin:18px 0;color:#D9E0EA;line-height:1.65;font-size:.86rem}}
    .seg-card{{display:flex;gap:14px;padding:17px;border:1px solid {BORDER};background:{SURFACE};border-radius:14px;margin-bottom:10px}} .seg-badge{{width:42px;height:42px;border-radius:12px;flex:0 0 42px;display:flex;align-items:center;justify-content:center;border:1px solid var(--seg-color);color:var(--seg-color);background:rgba(255,255,255,.025);font-weight:800}} .seg-card b{{color:{TEXT};font-family:'Space Grotesk';font-size:1rem}} .seg-card .desc{{color:{MUTED};display:block;font-size:.8rem;line-height:1.55;margin-top:4px}} .seg-stat{{display:flex;gap:14px;flex-wrap:wrap;color:{MUTED};font-size:.7rem;margin-top:8px}} .seg-stat b{{color:#E6EBF2;font-size:.72rem}}
    .gloss-item{{padding:11px 0;border-bottom:1px solid {BORDER}}}.gloss-item b{{color:#E9EEF6;font-family:'Space Grotesk'}}.gloss-item span{{display:block;color:{MUTED};font-size:.78rem;margin-top:3px;line-height:1.5}}
    div[data-testid="stMetric"]{{background:{SURFACE_2};border:1px solid {BORDER};border-radius:12px;padding:12px}} [data-testid="stMetricValue"]{{color:{TEXT}!important;font-family:'Space Grotesk'!important}} [data-testid="stDataFrame"]{{border:1px solid {BORDER};border-radius:12px;overflow:hidden}}
    .stButton button,.stDownloadButton button{{background:{SURFACE_2}!important;color:{TEXT}!important;border:1px solid {BORDER}!important;border-radius:9px!important;font-weight:600!important}} .stButton button:hover,.stDownloadButton button:hover{{border-color:{ACCENT}!important;background:#171D29!important}}
    .stTabs [data-baseweb="tab-list"]{{gap:5px;border-bottom:1px solid {BORDER}}}.stTabs [data-baseweb="tab"]{{color:{MUTED};padding:9px 15px;font-size:.75rem;font-weight:600}}.stTabs [aria-selected="true"]{{color:{TEXT}!important;border-bottom:2px solid {ACCENT}!important}}
    .streamlit-expanderHeader{{background:{SURFACE}!important;border:1px solid {BORDER}!important;border-radius:10px!important;color:{TEXT}!important}} .streamlit-expanderContent{{background:{SURFACE}!important;border:1px solid {BORDER}!important;border-top:0!important}} hr{{border-color:{BORDER}!important}}
    @media(max-width:900px){{.kpi-grid{{grid-template-columns:repeat(2,minmax(0,1fr))}}.hero{{padding:26px}}.hero-badge{{display:none}}}}
    </style>""",unsafe_allow_html=True)

def base_layout(**overrides):
    layout=dict(paper_bgcolor=SURFACE,plot_bgcolor=SURFACE,font=dict(color="#CBD5E1",family="DM Sans, sans-serif",size=12),xaxis=dict(gridcolor="#1D2634",zerolinecolor="#1D2634",color="#8D98A9"),yaxis=dict(gridcolor="#1D2634",zerolinecolor="#1D2634",color="#8D98A9"),legend=dict(bgcolor="rgba(0,0,0,0)",font=dict(color="#AAB4C4")),margin=dict(t=10,l=10,r=10,b=10),hoverlabel=dict(bgcolor="#111722",bordercolor="#334155",font=dict(color="#F4F7FB")))
    layout.update(overrides); return layout

def render_brand():
    st.sidebar.markdown("<div class='brand'><div class='brand-mark'>CL</div><div><div class='brand-title'>Client Ledger</div><div class='brand-sub'>CUSTOMER INTELLIGENCE</div></div></div>",unsafe_allow_html=True)

def render_hero(title,subtitle,eyebrow="Client Ledger · Business Intelligence"):
    st.markdown(f"<div class='hero'><div class='hero-badge'>◆</div><div class='eyebrow'>{eyebrow}</div><h1>{title}</h1><p>{subtitle}</p></div>",unsafe_allow_html=True)

def render_kpis(items):
    cells=[f"<div class='kpi'><div class='kpi-label'>{label}</div><div class='kpi-value'>{value}</div><div class='kpi-sub'>{sub}</div></div>" for label,value,sub in items]
    st.markdown(f"<div class='kpi-grid'>{''.join(cells)}</div>",unsafe_allow_html=True)

def section(title,hint=None):
    st.markdown(f"<div class='section-title'>{title}</div>",unsafe_allow_html=True)
    if hint: st.markdown(f"<div class='section-hint'>{hint}</div>",unsafe_allow_html=True)

def clean_transactions(df:pd.DataFrame)->pd.DataFrame:
    rename_map={'Invoice':'InvoiceNo','InvoiceNo':'InvoiceNo','Price':'UnitPrice','UnitPrice':'UnitPrice','Customer ID':'CustomerID','CustomerID':'CustomerID'}
    df=df.rename(columns={k:v for k,v in rename_map.items() if k in df.columns}).copy(); df.columns=df.columns.str.strip()
    required={'InvoiceNo','InvoiceDate','Quantity','UnitPrice','CustomerID'}; missing=required-set(df.columns)
    if missing: raise ValueError(f"Kolom wajib tidak ditemukan: {', '.join(sorted(missing))}")
    df=df.dropna(subset=['CustomerID']); df=df[~df['InvoiceNo'].astype(str).str.startswith('C')]
    df=df[(pd.to_numeric(df['Quantity'],errors='coerce')>0)&(pd.to_numeric(df['UnitPrice'],errors='coerce')>0)].drop_duplicates()
    df['CustomerID']=pd.to_numeric(df['CustomerID'],errors='coerce');df['Quantity']=pd.to_numeric(df['Quantity'],errors='coerce');df['UnitPrice']=pd.to_numeric(df['UnitPrice'],errors='coerce');df['InvoiceDate']=pd.to_datetime(df['InvoiceDate'],errors='coerce')
    df=df.dropna(subset=['CustomerID','InvoiceDate','Quantity','UnitPrice']);df['CustomerID']=df['CustomerID'].astype(int);df['TotalPrice']=df['Quantity']*df['UnitPrice'];return df

def compute_rfm(df:pd.DataFrame)->pd.DataFrame:
    snapshot_date=df['InvoiceDate'].max()+timedelta(days=1)
    rfm=df.groupby('CustomerID').agg({'InvoiceDate':lambda x:(snapshot_date-x.max()).days,'InvoiceNo':'nunique','TotalPrice':'sum'}).reset_index();rfm.columns=['CustomerID','Recency','Frequency','Monetary'];return rfm

def _scaled_rfm(rfm):
    return StandardScaler().fit_transform(rfm[['Recency','Frequency','Monetary']].apply(lambda x:np.log1p(x)))

def run_clustering(rfm:pd.DataFrame,k:int=4):
    scaled=_scaled_rfm(rfm); km=KMeans(n_clusters=k,random_state=42,n_init=10); result=rfm.copy();result['Cluster']=km.fit_predict(scaled);sil=silhouette_score(scaled,result['Cluster']);db=davies_bouldin_score(scaled,result['Cluster'])
    stats=result.groupby('Cluster').agg(Recency=('Recency','mean'),Frequency=('Frequency','mean'),Monetary=('Monetary','mean')).reset_index();stats['priority']=stats['Monetary'].rank(ascending=False,method='first')+stats['Recency'].rank(ascending=True,method='first')*.15;stats=stats.sort_values('priority').reset_index(drop=True)
    labels=['Champions','Promising/New Active','At Risk','Lost/Churned'];mapping={row['Cluster']:(labels[i] if i<len(labels) else f'Segmen {i+1}') for i,(_,row) in enumerate(stats.iterrows())};result['Segmen']=result['Cluster'].map(mapping);return result,sil,db

def find_optimal_k(rfm:pd.DataFrame,k_range=range(2,8)):
    scaled=_scaled_rfm(rfm);results=[]
    for k in k_range:
        km=KMeans(n_clusters=k,random_state=42,n_init=10);labels=km.fit_predict(scaled);results.append({'k':k,'inertia':km.inertia_,'silhouette':silhouette_score(scaled,labels),'davies_bouldin':davies_bouldin_score(scaled,labels)})
    return pd.DataFrame(results)
