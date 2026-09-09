"""Premium segment intelligence page."""
import streamlit as st,pandas as pd,plotly.graph_objects as go,yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth
from style_and_pipeline import inject_style,render_hero,render_brand,base_layout,section,COLOR_MAP,INITIAL_MAP,ORDER,INSIGHTS
from navigation import render_navigation

st.set_page_config(page_title='Detail Segmen | Client Ledger',page_icon='◆',layout='wide');inject_style();render_brand()
with open('config.yaml') as f: config=yaml.load(f,Loader=SafeLoader)
auth=stauth.Authenticate(config['credentials'],config['cookie']['name'],config['cookie']['key'],config['cookie']['expiry_days']);auth.login()
if not st.session_state.get('authentication_status'): st.warning('Silakan login terlebih dahulu melalui halaman Home.');st.stop()
render_navigation('Detail Segmen',st.session_state.get('name','Pengguna'));auth.logout('Keluar','sidebar')
@st.cache_data
def load(): return pd.read_csv('rfm_segmentasi_pelanggan.csv')
df=load();st.sidebar.markdown('### Filter analitik');segments=st.sidebar.multiselect('Segmen',ORDER,ORDER);filtered=df[df.Segmen.isin(segments)].copy()
render_hero('Segment Intelligence','Pahami karakteristik RFM setiap segmen dan ubah hasil clustering menjadi tindakan pemasaran.','CLIENT LEDGER · SEGMENT INTELLIGENCE')
summary=filtered.groupby('Segmen').agg(Jumlah=('CustomerID','count'),Recency=('Recency','mean'),Frequency=('Frequency','mean'),Monetary=('Monetary','mean'),TotalRevenue=('Monetary','sum')).reindex(ORDER).dropna(how='all').reset_index()
if summary.empty: st.info('Pilih minimal satu segmen.');st.stop()
section('RFM profile','Skor dinormalisasi 0–1; Recency dibalik sehingga skor tinggi berarti lebih baru.')
normalized=summary.copy()
for col in ['Recency','Frequency','Monetary']: normalized[col]=(normalized[col]-normalized[col].min())/(normalized[col].max()-normalized[col].min()+1e-9)
normalized['Recency']=1-normalized['Recency'];fig=go.Figure()
for _,r in normalized.iterrows(): fig.add_trace(go.Scatterpolar(r=[r.Recency,r.Frequency,r.Monetary,r.Recency],theta=['Recency','Frequency','Monetary','Recency'],fill='toself',name=r.Segmen,line_color=COLOR_MAP.get(r.Segmen),fillcolor=COLOR_MAP.get(r.Segmen),opacity=.22))
fig.update_layout(**base_layout(polar=dict(bgcolor='#0D1118',radialaxis=dict(visible=True,range=[0,1],gridcolor='#263143'),angularaxis=dict(gridcolor='#263143'))));st.markdown('<div class="chart-frame">',unsafe_allow_html=True);st.plotly_chart(fig,use_container_width=True);st.markdown('</div>',unsafe_allow_html=True)
section('Segment playbook','Rekomendasi singkat untuk membantu menentukan prioritas campaign.')
for seg in ORDER:
    if seg not in summary.Segmen.values: continue
    r=summary[summary.Segmen==seg].iloc[0];c=COLOR_MAP[seg];share=r.Jumlah/summary.Jumlah.sum()*100
    st.markdown(f"<div class='seg-card'><div class='seg-badge' style='--seg-color:{c}'>{INITIAL_MAP[seg]}</div><div style='width:100%'><b>{seg}</b><span class='desc'>{INSIGHTS[seg]}</span><div class='seg-stat'><span>{int(r.Jumlah):,} pelanggan</span><span>{share:.1f}% share</span><span>R {r.Recency:.0f} hari</span><span>F {r.Frequency:.1f}×</span><span>M £{r.Monetary:,.0f}</span><span>Revenue £{r.TotalRevenue:,.0f}</span></div></div></div>",unsafe_allow_html=True)
section('Segment comparison');st.dataframe(summary[['Segmen','Jumlah','Recency','Frequency','Monetary','TotalRevenue']].style.format({'Jumlah':'{:,.0f}','Recency':'{:,.1f}','Frequency':'{:,.1f}','Monetary':'£{:,.0f}','TotalRevenue':'£{:,.0f}'}),use_container_width=True,hide_index=True)
