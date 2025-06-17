import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import warnings

# Mengabaikan DeprecationWarning agar tampilan bersih
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Mengatur konfigurasi halaman
st.set_page_config(
    page_title="Dashboard Analisis Perceraian Bekasi",
    layout="wide"
)

# --- FUNGSI UNTUK MEMUAT DAN MEMBERSIHKAN DATA (VERSI FINAL) ---
@st.cache_data
def load_and_clean_data():
    df = pd.read_csv("Dataset-Perceraian.csv")
    df.columns = ['no_putusan', 'domisili_penggugat', 'jenis_kelamin_penggugat',
                  'jenis_kelamin_tergugat', 'tanggal_pernikahan', 'tanggal_putusan',
                  'umur_pernikahan_tahun', 'umur_pernikahan_bulan', 'pertengkaran',
                  'perselingkuhan', 'kdrt', 'ekonomi', 'amar_putusan']
    
    df['umur_pernikahan_tahun'] = df['umur_pernikahan_tahun'].str.extract('(\d+)').astype(float)
    df['tanggal_putusan'] = pd.to_datetime(df['tanggal_putusan'], format='%d-%b-%y', errors='coerce')
    df.dropna(subset=['tanggal_putusan', 'umur_pernikahan_tahun'], inplace=True)
    
    for col in ['domisili_penggugat', 'jenis_kelamin_penggugat', 'amar_putusan']:
        df[col] = df[col].str.upper()

    df['jenis_kelamin_penggugat'] = df['jenis_kelamin_penggugat'].replace('TIDAK DIKETAHUI', 'PEREMPUAN')
        
    for col in ['pertengkaran', 'perselingkuhan', 'kdrt', 'ekonomi']:
        df[col] = df[col].astype(int)
        
    df['bulan_putusan'] = df['tanggal_putusan'].dt.month_name()
    df['hari_putusan'] = df['tanggal_putusan'].dt.day_name()
    
    bins = [0, 5, 10, 15, 20, np.inf]
    labels = ['0-5 Thn', '6-10 Thn', '11-15 Thn', '16-20 Thn', '20+ Thn']
    df['grup_usia_nikah'] = pd.cut(df['umur_pernikahan_tahun'], bins=bins, labels=labels, right=False)
    
    kecamatan_counts = df['domisili_penggugat'].value_counts()
    threshold = 5
    kecamatan_lainnya = kecamatan_counts[kecamatan_counts < threshold].index
    df['domisili_penggugat'] = df['domisili_penggugat'].replace(kecamatan_lainnya, 'LAIN-LAIN')

    usia_nikah_counts = df['grup_usia_nikah'].value_counts()
    threshold_usia = 20
    repl_usia = usia_nikah_counts[usia_nikah_counts < threshold_usia].index
    if not repl_usia.empty:
        df['grup_usia_nikah'] = df['grup_usia_nikah'].cat.add_categories(['Lain-lain'])
        df.loc[df['grup_usia_nikah'].isin(repl_usia), 'grup_usia_nikah'] = 'Lain-lain'
        df['grup_usia_nikah'] = df['grup_usia_nikah'].cat.remove_unused_categories()
    
    df['jumlah_alasan'] = df[['pertengkaran', 'ekonomi', 'perselingkuhan', 'kdrt']].sum(axis=1)

    return df

df = load_and_clean_data()

# --- SIDEBAR INTERAKTIF ---
st.sidebar.header("🔍 Filter Interaktif")
kecamatan_options = ['Semua Kecamatan'] + sorted(df['domisili_penggugat'].unique().tolist())
selected_kecamatan = st.sidebar.selectbox('Pilih Kecamatan:', kecamatan_options)
grup_usia_options = ['Semua Grup'] + df['grup_usia_nikah'].cat.categories.tolist()
selected_grup_usia = st.sidebar.selectbox('Pilih Lama Pernikahan:', grup_usia_options)


# --- LOGIKA FILTER ---
df_filtered = df.copy()
if selected_kecamatan != 'Semua Kecamatan':
    df_filtered = df_filtered[df_filtered['domisili_penggugat'] == selected_kecamatan]
if selected_grup_usia != 'Semua Grup':
    df_filtered = df_filtered[df_filtered['grup_usia_nikah'] == selected_grup_usia]

# --- JUDUL UTAMA ---
st.title("Dashboard Interaktif Analisis Perceraian di Bekasi")
st.markdown("Analisis Mendalam Terhadap Karakteristik, Faktor Pemicu, dan Tren Kasus Perceraian yang Dikabulkan")

# --- METRIK UTAMA (KPI) ---
total_kasus = len(df_filtered)
if total_kasus > 0:
    avg_umur_nikah = df_filtered['umur_pernikahan_tahun'].mean()
    persen_wanita = (df_filtered['jenis_kelamin_penggugat'] == 'PEREMPUAN').sum() / total_kasus * 100
else:
    avg_umur_nikah = 0; persen_wanita = 0
col1, col2, col3 = st.columns(3)
col1.metric("Total Kasus (Sesuai Filter)", f"{total_kasus}")
col2.metric("Rata-rata Usia Pernikahan", f"{avg_umur_nikah:.1f} Tahun")
col3.metric("Proporsi Penggugat Perempuan", f"{persen_wanita:.1f}%")

st.markdown("---")

# --- MEMBUAT TAB ---
tab1, tab2, tab3, tab4 = st.tabs([
    "📍 Demografi & Geografis", "🔍 Analisis Faktor Penyebab",
    "⏳ Analisis Lama Pernikahan", "🗓️ Analisis Pola Waktu"
])

if df_filtered.empty:
    st.warning("Tidak ada data yang sesuai dengan kombinasi filter yang Anda pilih.")
else:
    with tab1:
        st.header("Analisis Demografi dan Sebaran Wilayah")
        col_t1_1, col_t1_2 = st.columns([2, 1])
        with col_t1_1:
            st.subheader("Peta Sebaran Kasus per Kecamatan")
            kasus_kecamatan = df_filtered['domisili_penggugat'].value_counts()
            
            # PERBAIKAN: Menambahkan label angka & judul bercerita
            fig_domisili = px.bar(
                kasus_kecamatan, 
                y=kasus_kecamatan.index, 
                x=kasus_kecamatan.values, 
                orientation='h', 
                title="<b>Bekasi Utara Menjadi Wilayah dengan Kasus Terbanyak</b>",
                text_auto=True,
                color=kasus_kecamatan.values, 
                color_continuous_scale='blues'
            )
            fig_domisili.update_layout(yaxis={'categoryorder':'total ascending'}, coloraxis_showscale=False)
            fig_domisili.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)
            st.plotly_chart(fig_domisili, use_container_width=True)
            
        with col_t1_2:
            st.subheader("Profil Penggugat")
            fig_gender = px.pie(
                df_filtered, 
                names='jenis_kelamin_penggugat', 
                title="<b>Proporsi Gender Penggugat</b>", 
                hole=.3, 
                color_discrete_sequence=px.colors.qualitative.Set2
            )
            fig_gender.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_gender, use_container_width=True)
            
        st.subheader("Sebaran Lama Pernikahan di Kecamatan (Sesuai Filter)")
        fig_boxplot = px.box(df_filtered, x='domisili_penggugat', y='umur_pernikahan_tahun', color='domisili_penggugat', title="Karakteristik Usia Nikah per Kecamatan")
        fig_boxplot.update_layout(showlegend=False)
        st.plotly_chart(fig_boxplot, use_container_width=True)

    with tab2:
        st.header("Analisis Mendalam Faktor-faktor Penyebab Perceraian")
        col_t2_1, col_t2_2 = st.columns(2)
        with col_t2_1:
            st.subheader("Pemicu Utama Perceraian")
            alasan_counts = pd.Series({'Pertengkaran': df_filtered['pertengkaran'].sum(), 'Ekonomi': df_filtered['ekonomi'].sum(),
                                       'Perselingkuhan': df_filtered['perselingkuhan'].sum(), 'KDRT': df_filtered['kdrt'].sum()}).sort_values(ascending=False)
            fig_alasan = px.bar(
                alasan_counts, 
                x=alasan_counts.index, 
                y=alasan_counts.values, 
                color=alasan_counts.values, 
                color_continuous_scale='plasma',
                text_auto=True
            )
            fig_alasan.update_traces(textfont_size=12, textangle=0)
            st.plotly_chart(fig_alasan, use_container_width=True)
            
        with col_t2_2:
            st.subheader("Kompleksitas Masalah per Kasus")
            jumlah_alasan_counts = df_filtered['jumlah_alasan'].value_counts()
            jumlah_alasan_counts.index = jumlah_alasan_counts.index.map(lambda x: f"{x} Alasan" if x > 0 else "Tidak Ada Data")
            
            fig_jml_alasan = px.pie(
                jumlah_alasan_counts, 
                names=jumlah_alasan_counts.index, 
                values=jumlah_alasan_counts.values, 
                title="<b>Distribusi Jumlah Alasan Perceraian per Kasus</b>", 
                hole=.3
            )
            # PERBAIKAN: Menambahkan persentase + label di dalam pie
            fig_jml_alasan.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_jml_alasan, use_container_width=True)
            
        st.subheader("Perbandingan Alasan Cerai antara Penggugat Laki-laki & Perempuan")
        gender_alasan_melted = df_filtered.groupby('jenis_kelamin_penggugat')[['pertengkaran', 'ekonomi', 'perselingkuhan', 'kdrt']].sum().reset_index().melt(id_vars='jenis_kelamin_penggugat', var_name='alasan', value_name='jumlah')
        color_map = {'PEREMPUAN': '#FF6347', 'LAKI LAKI': '#1E90FF'}
        fig_gender_alasan = px.bar(
            gender_alasan_melted, 
            x='alasan', 
            y='jumlah', 
            color='jenis_kelamin_penggugat', 
            barmode='group', 
            title="<b>Perbedaan Alasan Cerai Berdasarkan Gender</b>",
            color_discrete_map=color_map,
            text_auto=True
        )
        fig_gender_alasan.update_traces(textfont_size=12, textangle=0, textposition="outside")
        st.plotly_chart(fig_gender_alasan, use_container_width=True)

    with tab3:
        st.header("Analisis Berdasarkan Lama Pernikahan")
        st.subheader("Distribusi Kasus Berdasarkan Grup Usia Pernikahan")
        usia_nikah_counts = df_filtered['grup_usia_nikah'].value_counts().sort_index()
        fig_usia_nikah = px.bar(
            usia_nikah_counts, 
            x=usia_nikah_counts.index, 
            y=usia_nikah_counts.values, 
            color=usia_nikah_counts.values, 
            color_continuous_scale='greens', 
            labels={'x':'Grup Lama Pernikahan', 'y':'Jumlah Kasus'},
            text_auto=True,
            title="<b>Perceraian Paling Rawan Terjadi pada 5 Tahun Pertama</b>"
        )
        st.plotly_chart(fig_usia_nikah, use_container_width=True)
        
        st.subheader("Perubahan Tren Alasan Seiring Lamanya Pernikahan")
        alasan_by_usia = df_filtered.groupby('grup_usia_nikah', observed=True)[['pertengkaran', 'ekonomi', 'perselingkuhan', 'kdrt']].sum()
        alasan_sum = alasan_by_usia.sum(axis=1)
        alasan_proporsi = alasan_by_usia.div(alasan_sum, axis=0).fillna(0)
        fig_proporsi = px.bar(
            alasan_proporsi, 
            x=alasan_proporsi.index, 
            y=alasan_proporsi.columns, 
            template='plotly_white', 
            title="<b>Masalah Ekonomi Cenderung Meningkat pada Pernikahan Lama</b>", 
            barmode='stack'
        )
        # PERBAIKAN: Mengubah format sumbu Y menjadi persentase
        fig_proporsi.update_layout(yaxis_tickformat='.0%')
        st.plotly_chart(fig_proporsi, use_container_width=True)

    with tab4:
        st.header("Analisis Pola Berdasarkan Waktu")
        st.subheader("Tren Kasus Perceraian Bulanan")
        bulan_order = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
        df_filtered['bulan_putusan'] = pd.Categorical(df_filtered['bulan_putusan'], categories=bulan_order, ordered=True)
        monthly_counts = df_filtered['bulan_putusan'].value_counts().sort_index()
        fig_tren = px.line(
            monthly_counts, 
            x=monthly_counts.index, 
            y=monthly_counts.values, 
            markers=True, 
            labels={'x': 'Bulan', 'y': 'Jumlah Kasus'},
            title="<b>Puncak Kasus Terjadi di Bulan Agustus</b>"
        )
        fig_tren.update_traces(line_color='royalblue', line_width=3)
        # PERBAIKAN: Anotasi untuk menyorot titik puncak
        if not monthly_counts.empty:
            puncak_bulan = monthly_counts.idxmax()
            puncak_nilai = monthly_counts.max()
            fig_tren.add_annotation(x=puncak_bulan, y=puncak_nilai, text=f"Puncak: {puncak_nilai}", showarrow=True, arrowhead=2, ax=0, ay=-40)
        st.plotly_chart(fig_tren, use_container_width=True)
        
        st.subheader("Pola Putusan Berdasarkan Hari dalam Seminggu")
        hari_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        df_filtered['hari_putusan'] = pd.Categorical(df_filtered['hari_putusan'], categories=hari_order, ordered=True)
        daily_counts = df_filtered['hari_putusan'].value_counts().sort_index()
        fig_hari = px.bar(
            daily_counts, 
            x=daily_counts.index, 
            y=daily_counts.values, 
            color=daily_counts.values, 
            color_continuous_scale='viridis', 
            labels={'x':'Hari', 'y':'Jumlah Kasus'},
            text_auto=True,
            title="<b>Kamis Merupakan Hari Paling Sibuk untuk Putusan Cerai</b>"
        )
        st.plotly_chart(fig_hari, use_container_width=True)

# --- FOOTER ---
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center;">
        <p>Dibuat oleh: Milda Nabilah Al-hamaz (202210715079)</p>
    </div>
    """,
    unsafe_allow_html=True
)
