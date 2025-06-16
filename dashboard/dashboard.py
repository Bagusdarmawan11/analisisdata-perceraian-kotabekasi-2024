import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# Mengatur konfigurasi halaman (harus menjadi perintah pertama Streamlit)
st.set_page_config(
    page_title="Dashboard Analisis Perceraian Bekasi",
    page_icon="✹",
    layout="wide"
)

# --- FUNGSI UNTUK MEMUAT DAN MEMBERSIHKAN DATA (REVISI) ---
@st.cache_data
def load_and_clean_data():
    # Memuat data
    df = pd.read_csv("Dataset-Perceraian.csv")

    # Mengganti nama kolom
    df.columns = ['no_putusan', 'domisili_penggugat', 'jenis_kelamin_penggugat',
                  'jenis_kelamin_tergugat', 'tanggal_pernikahan', 'tanggal_putusan',
                  'umur_pernikahan_tahun', 'umur_pernikahan_bulan', 'pertengkaran',
                  'perselingkuhan', 'kdrt', 'ekonomi', 'amar_putusan']

    # --- PERBAIKAN DIMULAI DI SINI ---
    # Mengubah 'umur_pernikahan_tahun' menjadi numerik.
    # .str.extract('(\d+)') akan mengambil angka pertama dari teks.
    # .astype(float) mengubahnya menjadi angka.
    df['umur_pernikahan_tahun'] = df['umur_pernikahan_tahun'].str.extract('(\d+)').astype(float)
    # --- PERBAIKAN SELESAI ---

    # Mengubah tipe data tanggal dengan format yang benar
    df['tanggal_putusan'] = pd.to_datetime(df['tanggal_putusan'], format='%d-%b-%y', errors='coerce')

    # Menghapus baris dengan tanggal tidak valid
    df.dropna(subset=['tanggal_putusan', 'umur_pernikahan_tahun'], inplace=True)

    # Menyeragamkan format teks
    for col in ['domisili_penggugat', 'jenis_kelamin_penggugat', 'amar_putusan']:
        df[col] = df[col].str.upper()

    # Memastikan kolom alasan bertipe integer
    for col in ['pertengkaran', 'perselingkuhan', 'kdrt', 'ekonomi']:
        df[col] = df[col].astype(int)

    # Membuat kolom bulan
    df['bulan_putusan'] = df['tanggal_putusan'].dt.month_name()
    return df

# Memuat data menggunakan fungsi
df = load_and_clean_data()

# --- SIDEBAR UNTUK FILTER ---
st.sidebar.header("🔍 Filter Data")

# Filter Kecamatan
selected_kecamatan = st.sidebar.multiselect(
    'Pilih Kecamatan Penggugat:',
    options=sorted(df['domisili_penggugat'].unique()),
    default=[] # Default kosong berarti semua dipilih
)

# Filter Bulan
bulan_order = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
selected_bulan = st.sidebar.multiselect(
    'Pilih Bulan Putusan:',
    options=bulan_order,
    default=[]
)

# Filter Alasan
alasan_list = ['Pertengkaran', 'Ekonomi', 'Perselingkuhan', 'KDRT']
selected_alasan = st.sidebar.multiselect(
    'Pilih Alasan Perceraian:',
    options=alasan_list,
    default=[]
)

# --- MENERAPKAN FILTER KE DATA ---
# Jika filter kosong, gunakan semua data. Jika tidak, filter berdasarkan pilihan.
if not selected_kecamatan:
    df_filtered = df
else:
    df_filtered = df[df['domisili_penggugat'].isin(selected_kecamatan)]

if selected_bulan:
    df_filtered = df_filtered[df_filtered['bulan_putusan'].isin(selected_bulan)]

if selected_alasan:
    # Logika filter untuk alasan: kasus harus mengandung SEMUA alasan yang dipilih
    for alasan in selected_alasan:
        df_filtered = df_filtered[df_filtered[alasan.lower()] == 1]


# --- JUDUL UTAMA DASHBOARD ---
st.title("💔 Dashboard Analisis Kasus Perceraian di Bekasi")
st.markdown("Dashboard ini menganalisis data kasus perceraian yang putusannya dikabulkan sepanjang tahun berjalan.")

# --- METRIK UTAMA (KPI) ---
total_kasus = df_filtered.shape[0]
avg_umur_nikah = df_filtered['umur_pernikahan_tahun'].mean()
persen_wanita = (df_filtered['jenis_kelamin_penggugat'] == 'PEREMPUAN').sum() / total_kasus * 100 if total_kasus > 0 else 0

st.markdown("### Ringkasan Data (Sesuai Filter)")
col1, col2, col3 = st.columns(3)
col1.metric("Total Kasus Dikabulkan", f"{total_kasus}")
col2.metric("Rata-rata Usia Pernikahan", f"{avg_umur_nikah:.1f} Tahun")
col3.metric("Penggugat Perempuan", f"{persen_wanita:.1f}%")

st.markdown("---")


# --- VISUALISASI DATA ---
col_viz1, col_viz2 = st.columns(2)

with col_viz1:
    st.subheader("Kasus per Kecamatan")
    if not df_filtered.empty:
        kasus_kecamatan = df_filtered['domisili_penggugat'].value_counts().sort_values(ascending=True)
        fig_kecamatan = px.bar(
            kasus_kecamatan,
            x=kasus_kecamatan.values,
            y=kasus_kecamatan.index,
            orientation='h',
            title="Distribusi Kasus Berdasarkan Kecamatan",
            labels={'x': 'Jumlah Kasus', 'y': 'Kecamatan'},
            color=kasus_kecamatan.values,
            color_continuous_scale=px.colors.sequential.Teal
        )
        fig_kecamatan.update_layout(showlegend=False)
        st.plotly_chart(fig_kecamatan, use_container_width=True)
    else:
        st.warning("Tidak ada data yang sesuai dengan filter yang dipilih.")

with col_viz2:
    st.subheader("Faktor Penyebab Perceraian")
    if not df_filtered.empty:
        alasan_counts = {
            'Pertengkaran': df_filtered['pertengkaran'].sum(),
            'Ekonomi': df_filtered['ekonomi'].sum(),
            'Perselingkuhan': df_filtered['perselingkuhan'].sum(),
            'KDRT': df_filtered['kdrt'].sum()
        }
        alasan_series = pd.Series(alasan_counts).sort_values(ascending=False)
        fig_alasan = px.bar(
            alasan_series,
            x=alasan_series.index,
            y=alasan_series.values,
            title="Jumlah Kasus Berdasarkan Faktor Penyebab",
            labels={'x': 'Alasan', 'y': 'Jumlah Kasus'},
            color=alasan_series.values,
            color_continuous_scale=px.colors.sequential.Plasma
        )
        st.plotly_chart(fig_alasan, use_container_width=True)
    else:
        st.warning("Tidak ada data yang sesuai dengan filter yang dipilih.")


# --- GRAFIK TREN BULANAN ---
st.subheader("Tren Kasus Perceraian Bulanan")
if not df_filtered.empty:
    df_filtered['bulan_putusan'] = pd.Categorical(df_filtered['bulan_putusan'], categories=bulan_order, ordered=True)
    monthly_counts = df_filtered['bulan_putusan'].value_counts().sort_index()

    fig_tren = px.line(
        monthly_counts,
        x=monthly_counts.index,
        y=monthly_counts.values,
        title="Jumlah Kasus Perceraian per Bulan",
        markers=True,
        labels={'x': 'Bulan', 'y': 'Jumlah Kasus'}
    )
    fig_tren.update_traces(line_color='royalblue', line_width=3)
    st.plotly_chart(fig_tren, use_container_width=True)
else:
    st.warning("Tidak ada data yang sesuai dengan filter yang dipilih.")


# --- MENAMPILKAN DATA MENTAH (SESUAI FILTER) ---
with st.expander("Lihat Data Mentah (Sesuai Filter)"):
    st.dataframe(df_filtered)

# --- FOOTER ---
st.markdown("---")  # Garis pemisah

# Menggunakan HTML untuk membuat teks berada di tengah
st.markdown(
    """
    <div style="text-align: center;">
        <p>Dibuat dengan ❤️ oleh: Milda Nabilah Al-hamaz (202210715079)</p>
    </div>
    """,
    unsafe_allow_html=True
)
