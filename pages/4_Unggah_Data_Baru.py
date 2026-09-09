"""Premium transaction upload and ML pipeline."""
import streamlit as st,pandas as pd,plotly.express as px,yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth
from style_and_pipeline import inject_style,render_hero,render_brand,render_kpis,base_layout,COLOR_MAP,clean_transactions,compute_rfm,run_clustering,find_optimal_k
from navigation import render_navigation

st.set_page_config(page_title='Unggah Data Baru | Client Ledger',page_icon='◆',layout='wide');inject_style();render_brand()
with open('config.yaml') as f: config=yaml.load(f,Loader=SafeLoader)
auth=stauth.Authenticate(config['credentials'],config['cookie']['name'],config['cookie']['key'],config['cookie']['expiry_days']);auth.login()
if not st.session_state.get('authentication_status'): st.warning('Silakan login terlebih dahulu melalui halaman Home.');st.stop()
render_navigation('Unggah Data Baru',st.session_state.get('name','Pengguna'));auth.logout('Keluar','sidebar');st.sidebar.caption('CSV wajib: Invoice/InvoiceNo, InvoiceDate, Quantity, Price/UnitPrice, Customer ID/CustomerID.')
render_hero('Data Lab','Upload transaksi baru dan jalankan seluruh pipeline RFM + K-Means tanpa notebook manual.','CLIENT LEDGER · MACHINE LEARNING PIPELINE')
uploaded=st.file_uploader('Drop file CSV transaksi di sini',type=['csv'])
if uploaded is None: st.markdown("<div class='insight'><b>Pipeline 4 tahap:</b> Validate & Clean → Calculate RFM → Evaluate k → Cluster & Export.</div>",unsafe_allow_html=True);st.stop()
try:
    try: raw=pd.read_csv(uploaded,encoding='ISO-8859-1')
    except Exception: uploaded.seek(0);raw=pd.read_csv(uploaded)
    st.markdown(f"<div class='section-title'>01 · Raw data</div><div class='section-hint'>{len(raw):,} rows · {len(raw.columns)} columns</div>",unsafe_allow_html=True);st.dataframe(raw.head(12),use_container_width=True,hide_index=True)
    with st.spinner('Cleaning transaksi...'): cleaned=clean_transactions(raw)
    render_kpis([('Valid rows',f'{len(cleaned):,}',f'{len(cleaned)/max(len(raw),1)*100:.1f}% retained'),('Customers',f'{cleaned.CustomerID.nunique():,}','unique customers'),('Invoices',f'{cleaned.InvoiceNo.nunique():,}','unique invoices'),('Revenue',f'£{cleaned.TotalPrice.sum():,.0f}','clean transaction value')])
    st.markdown("<div class='insight'><b>Cleaning selesai.</b> Retur, nilai tidak valid, customer kosong, duplikasi, dan tanggal tidak valid telah disaring sebelum analisis.</div>",unsafe_allow_html=True)
    st.markdown("<div class='section-title'>02 · RFM calculation</div>",unsafe_allow_html=True);rfm=compute_rfm(cleaned);st.dataframe(rfm.head(12),use_container_width=True,hide_index=True)
    st.markdown("<div class='section-title'>03 · Cluster evaluation</div><div class='section-hint'>Silhouette lebih tinggi dan Davies-Bouldin lebih rendah umumnya lebih baik.</div>",unsafe_allow_html=True)
    with st.spinner('Evaluating k = 2–7...'): evaluation=find_optimal_k(rfm)
    a,b=st.columns([1.5,1])
    with a:
        fig=px.line(evaluation,x='k',y='silhouette',markers=True);fig.update_traces(line_color=COLOR_MAP['Champions']);fig.update_layout(**base_layout(xaxis_title='Clusters (k)',yaxis_title='Silhouette Score'));st.markdown('<div class="chart-frame">',unsafe_allow_html=True);st.plotly_chart(fig,use_container_width=True);st.markdown('</div>',unsafe_allow_html=True)
    with b: st.dataframe(evaluation.round(3),use_container_width=True,hide_index=True)
    best_k=int(evaluation.loc[evaluation.silhouette.idxmax(),'k']);k=st.slider('Jumlah cluster',2,7,min(best_k,4));st.caption(f'Rekomendasi otomatis: k = {best_k}')
    st.markdown("<div class='section-title'>04 · Segmentation result</div>",unsafe_allow_html=True)
    result,sil,db=run_clustering(rfm,k);render_kpis([('Silhouette',f'{sil:.3f}','higher is better'),('Davies-Bouldin',f'{db:.3f}','lower is better'),('Customers',f'{len(result):,}','clustered'),('Clusters',str(k),'selected k')])
    st.dataframe(result.head(20),use_container_width=True,hide_index=True)
    fig=px.scatter(result.sample(min(1800,len(result)),random_state=42),x='Recency',y='Monetary',color='Segmen',size='Frequency',color_discrete_map=COLOR_MAP,log_y=True,hover_data=['CustomerID']);fig.update_layout(**base_layout(legend=dict(orientation='h',y=-.18)));st.markdown('<div class="chart-frame">',unsafe_allow_html=True);st.plotly_chart(fig,use_container_width=True);st.markdown('</div>',unsafe_allow_html=True)
    st.download_button('↓  EXPORT SEGMENTATION CSV',result.to_csv(index=False).encode('utf-8'),'hasil_segmentasi_baru.csv','text/csv',use_container_width=True)
except Exception as e: st.error(f'Data tidak dapat diproses: {e}')
