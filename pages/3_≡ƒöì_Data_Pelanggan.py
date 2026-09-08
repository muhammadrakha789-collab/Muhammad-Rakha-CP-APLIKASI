"""Premium customer data explorer."""
import streamlit as st,pandas as pd,yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth
from style_and_pipeline import inject_style,render_hero,render_brand,render_kpis,ORDER,COLOR_MAP
st.set_page_config(page_title="Data Pelanggan | Client Ledger",page_icon="◆",layout="wide");inject_style();render_brand()
with open('config.yaml') as f: config=yaml.load(f,Loader=SafeLoader)
auth=stauth.Authenticate(config['credentials'],config['cookie']['name'],config['cookie']['key'],config['cookie']['expiry_days']);auth.login()
if not st.session_state.get('authentication_status'): st.warning('Silakan login terlebih dahulu melalui halaman Home.');st.stop()
st.sidebar.markdown(f"**SESSION**  \n{st.session_state.get('name','Pengguna')}");auth.logout('Keluar','sidebar');st.sidebar.markdown('---')
@st.cache_data
def load(): return pd.read_csv('rfm_segmentasi_pelanggan.csv')
df=load();st.sidebar.markdown('### Filter data');segments=st.sidebar.multiselect('Segmen',ORDER,ORDER);search=st.sidebar.text_input('Cari Customer ID','');min_freq,max_freq=int(df.Frequency.min()),int(df.Frequency.max());freq=st.sidebar.slider('Frequency',min_freq,max_freq,(min_freq,max_freq));mon_min,mon_max=float(df.Monetary.min()),float(df.Monetary.max());mon=st.sidebar.slider('Monetary',mon_min,mon_max,(mon_min,mon_max));filtered=df[df.Segmen.isin(segments)&df.Frequency.between(freq[0],freq[1])&df.Monetary.between(mon[0],mon[1])].copy()
if search: filtered=filtered[filtered.CustomerID.astype(str).str.contains(search,case=False,na=False)]
render_hero('Customer Explorer','Eksplorasi pelanggan dengan filter interaktif, pencarian ID, metrik RFM, dan ekspor data terpilih.')
render_kpis([('Rows',f'{len(filtered):,}',f'{len(filtered)/len(df)*100:.1f}% dari dataset'),('Revenue',f'£{filtered.Monetary.sum():,.0f}','filtered monetary'),('Avg Frequency',f'{filtered.Frequency.mean():.1f}×','per customer'),('Avg Recency',f'{filtered.Recency.mean():.0f} hari','per customer')])
left,right=st.columns([1,1]);left.caption(f"Menampilkan **{len(filtered):,}** pelanggan");right.download_button('↓  EXPORT CSV',filtered.to_csv(index=False).encode('utf-8'),'customer_segmented_filtered.csv','text/csv',use_container_width=True)
st.dataframe(filtered,use_container_width=True,hide_index=True,height=560,column_config={'Segmen':st.column_config.TextColumn('Segment'),'CustomerID':st.column_config.NumberColumn('Customer ID'),'Monetary':st.column_config.NumberColumn('Monetary',format='£ %.0f'),'Recency':st.column_config.NumberColumn('Recency',format='%d hari'),'Frequency':st.column_config.NumberColumn('Frequency',format='%.0f')})
