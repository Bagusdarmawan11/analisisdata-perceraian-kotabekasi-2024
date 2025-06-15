# dashboard_app.py

import streamlit as st
import pandas as pd
import plotly.express as px
import warnings

warnings.filterwarnings('ignore')

# ----------------- KONFIGURASI HALAMAN -----------------
st.set_page_config(
    page_title="Dashboard Analisis Perceraian",
    page_icon="💔",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------- JUDUL DAN DESKRIPSI -----------------
st.title("📊 Dashboard Analisis Data Perceraian Kota Bekasi")
st.markdown("""
Dashboard ini menyajikan analisis mendalam mengenai data perkara perceraian yang terdaftar di Pengadilan Agama Bekasi. 
Gunakan filter di samping untuk menelusuri data.
""")

# ----------------- FUNGSI UNTUK MEMUAT DATA -----------------
# Menggunakan cache agar data hanya dimuat sekali
@st.cache_data
def load_data(file_path):
    """
    Fungsi untuk memuat dan melakukan pembersihan dasar pada data.
    """
    try:
        df = pd.read_csv(file_path)
        # Asumsi nama kolom berdasarkan konteks, sesuaikan jika perlu
        # Mengubah kolom 'Tahun' menjadi tipe data integer
        if 'Tahun' in df.columns:
            df['Tahun'] = pd.to_numeric(df['Tahun'], errors='coerce').dropna().astype(int)
        # Membersihkan spasi ekstra pada kolom teks
        if 'Jenis Perkara' in df.columns:
            df['Jenis Perkara'] = df['Jenis Perkara'].str.strip()
        if 'Faktor Penyebab' in df.columns:
            df['Faktor Penyebab'] = df['Faktor Penyebab'].str.strip()
        return df
    except FileNotFoundError:
        st.error(f"File tidak ditemukan di path: {file_path}. Pastikan file CSV Anda berada di direktori yang sama dengan script ini.")
        return None
    except Exception as e:
        st.error(f"Terjadi kesalahan saat memuat data: {e}")
        return None

# Ganti dengan path file CSV Anda
file_path = 'Dashboard/Data Presentasii.xlsx - Perdata Agama.csv'
df = load_data(file_path)


# Hentikan aplikasi jika data gagal dimuat
if df is None:
    st.stop()

# ----------------- SIDEBAR UNTUK FILTER -----------------
st.sidebar.header("🔍 Filter Data")

# Filter berdasarkan Tahun
if 'Tahun' in df.columns:
    unique_years = sorted(df['Tahun'].unique())
    selected_year = st.sidebar.multiselect(
        "Pilih Tahun:",
        options=unique_years,
        default=unique_years
    )
else:
    selected_year = []

# Filter berdasarkan Jenis Perkara
if 'Jenis Perkara' in df.columns:
    unique_cases = sorted(df['Jenis Perkara'].unique())
    selected_case = st.sidebar.multiselect(
        "Pilih Jenis Perkara:",
        options=unique_cases,
        default=unique_cases
    )
else:
    selected_case = []

# Filter data berdasarkan pilihan di sidebar
if selected_year and 'Tahun' in df.columns:
    df_filtered = df[df['Tahun'].isin(selected_year)]
else:
    df_filtered = df.copy()

if selected_case and 'Jenis Perkara' in df.columns:
    df_filtered = df_filtered[df_filtered['Jenis Perkara'].isin(selected_case)]


# ----------------- TAMPILAN UTAMA -----------------
st.header("📈 Visualisasi Data")

# Membuat 2 kolom utama
col1, col2 = st.columns((4, 3)) 

with col1:
    # --- Grafik 1: Tren Jumlah Kasus per Tahun ---
    st.subheader("Tren Kasus Tahunan")
    if 'Tahun' in df_filtered.columns:
        yearly_cases = df_filtered.groupby('Tahun').size().reset_index(name='Jumlah Kasus')
        fig_yearly = px.line(
            yearly_cases, 
            x='Tahun', 
            y='Jumlah Kasus', 
            markers=True,
            template='plotly_white'
        )
        fig_yearly.update_layout(xaxis_title="Tahun", yaxis_title="Jumlah Kasus")
        st.plotly_chart(fig_yearly, use_container_width=True)
    else:
        st.warning("Kolom 'Tahun' tidak ditemukan untuk membuat grafik tren.")

with col2:
    # --- Grafik 2: Komposisi Jenis Perkara ---
    st.subheader("Komposisi Jenis Perkara")
    if 'Jenis Perkara' in df_filtered.columns:
        case_composition = df_filtered['Jenis Perkara'].value_counts().reset_index()
        case_composition.columns = ['Jenis Perkara', 'Jumlah']
        fig_pie = px.pie(
            case_composition,
            names='Jenis Perkara',
            values='Jumlah',
            hole=0.4,
            template='plotly_white'
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.warning("Kolom 'Jenis Perkara' tidak ditemukan untuk membuat grafik komposisi.")


# --- Grafik 3: Faktor Penyebab Utama Perceraian (Horizontal Bar Chart) ---
st.subheader("Faktor Penyebab Utama Perceraian")
if 'Faktor Penyebab' in df_filtered.columns:
    # Mengambil top 10 faktor penyebab
    top_factors = df_filtered['Faktor Penyebab'].value_counts().nlargest(10).sort_values(ascending=True)
    fig_factors = px.bar(
        top_factors,
        x=top_factors.values,
        y=top_factors.index,
        orientation='h',
        template='plotly_white',
        labels={'x': 'Jumlah Kasus', 'y': 'Faktor Penyebab'}
    )
    fig_factors.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig_factors, use_container_width=True)
else:
    st.warning("Kolom 'Faktor Penyebab' tidak ditemukan untuk membuat grafik ini.")


# --- Menampilkan Data Tabel (Opsional) ---
if st.checkbox("Tampilkan Data Tabel (Hasil Filter)"):
    st.dataframe(df_filtered)


# ----------------- FOOTER -----------------
st.markdown("---")
footer_html = """
<div style="text-align: center; padding: 10px; font-family: sans-serif;">
    <p>
        Dibuat dengan ❤️ oleh <strong>[Nama Anda]</strong> menggunakan Streamlit
        <br>
        <strong>Sumber Data</strong>: Pengadilan Agama Bekasi (Data Fiktif untuk Simulasi)
    </p>
</div>
"""
st.markdown(footer_html, unsafe_allow_html=True)
