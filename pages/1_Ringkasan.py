"""Executive customer intelligence dashboard."""

import streamlit as st
import pandas as pd
import plotly.express as px
import yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth
from style_and_pipeline import inject_style, render_hero, render_brand, render_kpis, base_layout, section, COLOR_MAP, ORDER, GLOSSARY
from navigation import render_navigation

st.set_page_config(page_title="Ringkasan | Client Ledger", page_icon="◆", layout="wide", initial_sidebar_state="expanded")
inject_style()
render_brand()

with open("config.yaml") as f:
    config = yaml.load(f, Loader=SafeLoader)

auth = stauth.Authenticate(config["credentials"], config["cookie"]["name"], config["cookie"]["key"], config["cookie"]["expiry_days"])
auth.login()

if not st.session_state.get("authentication_status"):
    st.warning("Silakan login terlebih dahulu melalui halaman Home.")
    st.stop()

render_navigation("Ringkasan", st.session_state.get("name", "Pengguna"))
auth.logout("Keluar", "sidebar")

@st.cache_data
def load():
    return pd.read_csv("rfm_segmentasi_pelanggan.csv")

df = load()
st.sidebar.markdown("### Filter analitik")
segments = st.sidebar.multiselect("Segmen pelanggan", ORDER, ORDER)
st.sidebar.markdown("<div class='section-hint' style='margin:8px 0 4px;'>Gunakan filter untuk melihat perubahan KPI dan chart secara langsung.</div>", unsafe_allow_html=True)
with st.sidebar.expander("Definisi cepat RFM"):
    st.markdown("**R · Recency** — hari sejak transaksi terakhir")
    st.markdown("**F · Frequency** — jumlah transaksi unik")
    st.markdown("**M · Monetary** — total nilai transaksi")

filtered = df[df.Segmen.isin(segments)].copy()
render_hero("Executive Overview", "Pantau nilai pelanggan, distribusi segmen, dan area risiko dalam satu tampilan analitik yang siap digunakan untuk presentasi.", "CLIENT LEDGER · EXECUTIVE ANALYTICS")
if filtered.empty:
    st.warning("Tidak ada pelanggan untuk filter yang dipilih.")
    st.stop()

render_kpis([
    ("Total Pelanggan", f"{len(filtered):,}", f"{len(filtered) / len(df) * 100:.1f}% dari dataset"),
    ("Total Revenue", f"£{filtered.Monetary.sum():,.0f}", "nilai transaksi terakumulasi"),
    ("Avg Frequency", f"{filtered.Frequency.mean():.1f}×", "transaksi unik / pelanggan"),
    ("Avg Recency", f"{filtered.Recency.mean():.0f} hari", "semakin rendah semakin aktif"),
])
summary = filtered.groupby("Segmen").agg(Jumlah=("CustomerID", "count"), Recency=("Recency", "mean"), Frequency=("Frequency", "mean"), Monetary=("Monetary", "mean"), TotalRevenue=("Monetary", "sum")).reindex(ORDER).dropna(how="all").reset_index()
summary["Persentase"] = summary.Jumlah / summary.Jumlah.sum() * 100

if not summary.empty:
    top = summary.loc[summary.TotalRevenue.idxmax()]
    risk = summary[summary.Segmen == "Lost/Churned"]
    risk_text = f"Lost/Churned mencakup {risk.iloc[0].Persentase:.1f}% pelanggan." if not risk.empty else "Lost/Churned tidak termasuk dalam filter aktif."
    st.markdown(f"<div class='insight'><b>Executive insight</b><br>{top.Segmen} menjadi kontributor revenue terbesar dengan <b>£{top.TotalRevenue:,.0f}</b>. {risk_text}</div>", unsafe_allow_html=True)

section("Customer value map", "Recency × Monetary. Ukuran bubble menunjukkan Frequency.")
a, b = st.columns([1.55, 1])
with a:
    st.markdown('<div class="chart-frame">', unsafe_allow_html=True)
    sample = filtered.sample(min(1800, len(filtered)), random_state=42)
    fig = px.scatter(sample, x="Recency", y="Monetary", color="Segmen", size="Frequency", color_discrete_map=COLOR_MAP, category_orders={"Segmen": ORDER}, log_y=True, hover_data=["CustomerID"])
    fig.update_layout(**base_layout(legend=dict(orientation="h", y=-0.18), xaxis_title="Recency (hari)", yaxis_title="Monetary (£)"))
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
with b:
    st.markdown('<div class="chart-frame">', unsafe_allow_html=True)
    pie = px.pie(summary, names="Segmen", values="Jumlah", hole=0.68, color="Segmen", color_discrete_map=COLOR_MAP, category_orders={"Segmen": ORDER})
    pie.update_traces(textinfo="percent+label", textposition="outside")
    pie.update_layout(**base_layout(showlegend=False))
    st.plotly_chart(pie, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

section("Segment performance", "Bandingkan jumlah pelanggan, average monetary, dan total revenue dalam satu tabel ringkas.")
card_cols = st.columns(min(4, len(summary)))
for col, (_, row) in zip(card_cols, summary.iterrows()):
    color = COLOR_MAP.get(row.Segmen, "#8B5CF6")
    with col:
        st.markdown(f"<div style='background:#0D1118;border:1px solid #202938;border-top:3px solid {color};border-radius:14px;padding:16px;min-height:142px;'><div style='font-size:.68rem;color:#8D98A9;text-transform:uppercase;letter-spacing:.08em;font-weight:700;'>{row.Segmen}</div><div style='font-family:Space Grotesk;font-size:1.45rem;font-weight:700;color:#F4F7FB;margin-top:8px;'>{int(row.Jumlah):,}</div><div style='font-size:.72rem;color:#8D98A9;margin-top:2px;'>{row.Persentase:.1f}% pelanggan</div><div style='font-size:.76rem;color:#CBD5E1;margin-top:11px;'>Revenue <b>£{row.TotalRevenue:,.0f}</b></div></div>", unsafe_allow_html=True)

section("Revenue by segment", "Segmen dengan kontribusi terbesar layak menjadi prioritas retention.")
fig2 = px.bar(summary.sort_values("TotalRevenue"), x="TotalRevenue", y="Segmen", orientation="h", color="Segmen", color_discrete_map=COLOR_MAP, text="TotalRevenue", category_orders={"Segmen": ORDER})
fig2.update_traces(texttemplate="£%{text:,.0f}", textposition="outside")
fig2.update_layout(**base_layout(showlegend=False, xaxis_title="Revenue (£)", yaxis_title=""))
st.plotly_chart(fig2, use_container_width=True)
with st.expander("Panduan metrik & metodologi"):
    for term, desc in GLOSSARY:
        st.markdown(f"<div class='gloss-item'><b>{term}</b><span>{desc}</span></div>", unsafe_allow_html=True)
st.caption("RFM · K-Means Clustering · Silhouette Score · Davies-Bouldin Index")
