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
        
    # --- PERBAIKAN #2.1: Menggabungkan 'TIDAK DIKETAHUI' ke 'PEREMPUAN' ---
    df['jenis_kelamin_penggugat'] = df['jenis_kelamin_penggugat'].replace('TIDAK DIKETAHUI', 'PEREMPUAN')
        
    for col in ['pertengkaran', 'perselingkuhan', 'kdrt', 'ekonomi']:
        df[col] = df[col].astype(int)
        
    df['bulan_putusan'] = df['tanggal_putusan'].dt.month_name()
    df['hari_putusan'] = df['tanggal_putusan'].dt.day_name()
    
    bins = [0, 5, 10, 15, 20, np.inf]
    labels = ['0-5 Thn', '6-10 Thn', '11-15 Thn', '16-20 Thn', '20+ Thn']
    df['grup_usia_nikah'] = pd.cut(df['umur_pernikahan_tahun'], bins=bins, labels=labels, right=False)
    
    kecamatan_counts = df['domisili_penggugat'].value_counts()
    threshold_kecamatan = 5
    kecamatan_lainnya = kecamatan_counts[kecamatan_counts < threshold_kecamatan].index
    df['domisili_penggugat'] = df['domisili_penggugat'].replace(kecamatan_lainnya, 'LAIN-LAIN')
    
    main_df_copy = df.copy()
    usia_nikah_counts = main_df_copy['grup_usia_nikah'].value_counts()
    threshold_usia = 20
    repl_usia = usia_nikah_counts[usia_nikah_counts < threshold_usia].index
    main_df_copy['grup_usia_nikah'] = main_df_copy['grup_usia_nikah'].cat.add_categories(['Lain-lain'])
    main_df_copy.loc[main_df_copy['grup_usia_nikah'].isin(repl_usia), 'grup_usia_nikah'] = 'Lain-lain'
    main_df_copy['grup_usia_nikah'] = main_df_copy['grup_usia_nikah'].cat.remove_unused_categories()
    
    df['jumlah_alasan'] = df[['pertengkaran', 'ekonomi', 'perselingkuhan', 'kdrt']].sum(axis=1)

    return df

df = load_and_clean_data()

# --- SIDEBAR INTERAKTIF ---
st.sidebar.header("🔍 Filter Interaktif")
kecamatan_options = ['Semua Kecamatan'] + sorted(df['domisili_penggugat'].unique().tolist())
selected_kecamatan = st.sidebar.selectbox('Pilih Kecamatan:', kecamatan_options)
grup_usia_options = ['Semua Grup'] + df['grup_usia_nikah'].cat.categories.tolist()
selected_grup_usia = st.sidebar.selectbox('Pilih Lama Pernikahan:', grup_usia_options)
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/9/97/Logo_of_the_Supreme_Court_of_the_Republic_of_Indonesia.svg/1200px-Logo_of_the_Supreme_Court_of_the_Republic_of_Indonesia.svg.png", use_column_width='auto')

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
            fig_domisili = px.bar(kasus_kecamatan, y=kasus_kecamatan.index, x=kasus_kecamatan.values, orientation='h', title="Jumlah Kasus per Kecamatan",
                                  color=kasus_kecamatan.values, color_continuous_scale='blues')
            fig_domisili.update_layout(yaxis={'categoryorder':'total ascending'}, coloraxis_showscale=False)
            st.plotly_chart(fig_domisili, use_container_width=True)
        with col_t1_2:
            st.subheader("Profil Penggugat")
            fig_gender = px.pie(df_filtered, names='jenis_kelamin_penggugat', title="Proporsi Gender Penggugat", hole=.3, color_discrete_sequence=px.colors.qualitative.Set2)
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
            fig_alasan = px.bar(alasan_counts, x=alasan_counts.index, y=alasan_counts.values, color=alasan_counts.values, color_continuous_scale='plasma')
            st.plotly_chart(fig_alasan, use_container_width=True)
            
        with col_t2_2:
            st.subheader("Kompleksitas Masalah per Kasus")
            jumlah_alasan_counts = df_filtered['jumlah_alasan'].value_counts()
            # --- PERBAIKAN #1: Membuat label baru yang lebih deskriptif ---
            jumlah_alasan_counts.index = jumlah_alasan_counts.index.map(lambda x: f"{x} Alasan" if x > 0 else "Tidak Ada Data")
            
            fig_jml_alasan = px.pie(
                jumlah_alasan_counts, 
                names=jumlah_alasan_counts.index, 
                values=jumlah_alasan_counts.values, 
                title="Distribusi Jumlah Alasan per Kasus", 
                hole=.3
            )
            st.plotly_chart(fig_jml_alasan, use_container_width=True)
            
        st.subheader("Perbandingan Alasan Cerai antara Penggugat Laki-laki & Perempuan")
        gender_alasan_melted = df_filtered.groupby('jenis_kelamin_penggugat')[['pertengkaran', 'ekonomi', 'perselingkuhan', 'kdrt']].sum().reset_index().melt(id_vars='jenis_kelamin_penggugat', var_name='alasan', value_name='jumlah')
        
        # --- PERBAIKAN #2.2: Mendefinisikan warna yang kontras ---
        color_map = {'PEREMPUAN': '#FF6347', 'LAKI-LAKI': '#1E90FF'} # Tomato Red & Dodger Blue
        
        fig_gender_alasan = px.bar(
            gender_alasan_melted, 
            x='alasan', 
            y='jumlah', 
            color='jenis_kelamin_penggugat', 
            barmode='group', 
            title="Alasan Cerai Berdasarkan Gender Penggugat",
            color_discrete_map=color_map
        )
        st.plotly_chart(fig_gender_alasan, use_container_width=True)

    with tab3:
        # Kode untuk Tab 3 tetap sama
        st.header("Analisis Berdasarkan Lama Pernikahan")
        # ... (sisa kode tab 3)

    with tab4:
        # Kode untuk Tab 4 tetap sama
        st.header("Analisis Pola Berdasarkan Waktu")
        # ... (sisa kode tab 4)

# --- FOOTER ---
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center;">
        <p>Dibuat dengan ❤️ oleh: Milda Nabilah Al-hamaz (202210715079)</p>
    </div>
    """,
    unsafe_allow_html=True
)
