import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# Konfigurasi halaman Streamlit agar lebih lebar
st.set_page_config(layout="wide")

# --- Fungsi-fungsi dari Notebook ---
# Menggunakan cache agar data tidak di-load ulang setiap ada interaksi
@st.cache_data
def load_data(file_path):
    """
    Fungsi untuk memuat dan membersihkan data dari file Excel,
    diadaptasi dari notebook.
    """
    try:
        df = pd.read_excel(file_path, sheet_name='Perdata Agama')
        df = df.drop(df.index[0])
        df = df.reset_index(drop=True)
        df = df.dropna(subset=['Nomor Putusan'])
        df.columns = [
            'nomor_putusan', 'domisili', 'jk_penggugat', 'jk_tergugat',
            'tgl_nikah', 'tgl_cerai', 'umur_nikah', 'jml_bulan',
            'alasan_pertengkaran', 'alasan_selingkuh', 'alasan_kdrt',
            'alasan_ekonomi', 'status_gugatan'
        ]
        
        df['tgl_nikah'] = pd.to_datetime(df['tgl_nikah'], errors='coerce')
        df['tgl_cerai'] = pd.to_datetime(df['tgl_cerai'], errors='coerce')
        
        # Mengubah tipe data kolom alasan menjadi numerik untuk korelasi
        alasan_cols = ['alasan_pertengkaran', 'alasan_selingkuh', 'alasan_kdrt', 'alasan_ekonomi']
        for col in alasan_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        df[alasan_cols] = df[alasan_cols].fillna(0).astype(int)

        def get_main_reason(row):
            if row['alasan_pertengkaran'] == 1:
                return 'Pertengkaran'
            elif row['alasan_selingkuh'] == 1:
                return 'Perselingkuhan'
            elif row['alasan_kdrt'] == 1:
                return 'KDRT'
            elif row['alasan_ekonomi'] == 1:
                return 'Ekonomi'
            else:
                return 'Tidak Diketahui'

        df['alasan_utama'] = df.apply(get_main_reason, axis=1)
        df['tahun_cerai'] = df['tgl_cerai'].dt.year
        df['tahun_nikah'] = df['jml_bulan'] / 12

        return df
    except Exception as e:
        st.error(f"Error saat memuat data: {e}")
        return None

# --- Load Data ---
df = load_data('Data Presentasii.xlsx')

if df is not None:
    # --- Sidebar untuk Filter ---
    st.sidebar.header("Filter Data")

    # Filter Tahun
    min_year = int(df['tahun_cerai'].min())
    max_year = int(df['tahun_cerai'].max())
    selected_year_range = st.sidebar.slider(
        "Pilih Rentang Tahun Perceraian:",
        min_value=min_year,
        max_value=max_year,
        value=(min_year, max_year)
    )

    # Filter Domisili
    domisili_options = ['Semua'] + sorted(df['domisili'].unique().tolist())
    selected_domisili = st.sidebar.multiselect(
        "Pilih Domisili:",
        options=domisili_options,
        default=['Semua']
    )

    # --- Terapkan Filter ---
    df_filtered = df[
        (df['tahun_cerai'] >= selected_year_range[0]) &
        (df['tahun_cerai'] <= selected_year_range[1])
    ]

    if 'Semua' not in selected_domisili:
        df_filtered = df_filtered[df_filtered['domisili'].isin(selected_domisili)]

    # --- Judul Dashboard ---
    st.title("📊 Dashboard Analisis Data Perceraian Kota Bekasi")
    st.markdown("Dashboard interaktif untuk visualisasi data perkara perdata agama.")

    # --- Ringkasan Utama (KPIs) ---
    st.header("Ringkasan Utama")
    
    total_cases = len(df_filtered)
    if total_cases > 0:
      dikabulkan = len(df_filtered[df_filtered['status_gugatan'] == 'Dikabulkan'])
      success_rate = (dikabulkan / total_cases) * 100 if total_cases > 0 else 0
      avg_duration = df_filtered['tahun_nikah'].mean()
      most_common_reason = df_filtered['alasan_utama'].mode()[0]
    else:
      dikabulkan = 0
      success_rate = 0
      avg_duration = 0
      most_common_reason = "N/A"

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Kasus", f"{total_cases}")
    with col2:
        st.metric("Tingkat Dikabulkan", f"{success_rate:.1f}%")
    with col3:
        st.metric("Rata-rata Durasi Nikah", f"{avg_duration:.1f} Tahun")
    with col4:
        st.metric("Alasan Utama", most_common_reason)

    st.markdown("---")

    # --- Analisis Demografis & Alasan Perceraian ---
    st.header("Analisis Demografis & Alasan Perceraian")
    col1, col2 = st.columns(2)

    with col1:
        # Pie Chart: Alasan Utama
        alasan_counts = df_filtered['alasan_utama'].value_counts().reset_index()
        alasan_counts.columns = ['alasan', 'jumlah']
        fig_pie_alasan = px.pie(alasan_counts, names='alasan', values='jumlah',
                                title='Distribusi Alasan Utama Perceraian', hole=0.3)
        st.plotly_chart(fig_pie_alasan, use_container_width=True)

    with col2:
        # Pie Chart: Jenis Kelamin Penggugat
        gender_counts = df_filtered['jk_penggugat'].value_counts().reset_index()
        gender_counts.columns = ['gender', 'jumlah']
        fig_pie_gender = px.pie(gender_counts, names='gender', values='jumlah',
                                title='Distribusi Jenis Kelamin Penggugat', hole=0.3)
        st.plotly_chart(fig_pie_gender, use_container_width=True)
    
    col3, col4 = st.columns(2)

    with col3:
        # Bar Chart: Top Domisili
        domisili_counts = df_filtered['domisili'].value_counts().head(10).reset_index()
        domisili_counts.columns = ['domisili', 'jumlah']
        fig_bar_domisili = px.bar(domisili_counts.sort_values('jumlah'), y='domisili', x='jumlah', orientation='h',
                                  title='Top 10 Domisili Penggugat')
        st.plotly_chart(fig_bar_domisili, use_container_width=True)

    with col4:
        # Bar Chart: Status Gugatan
        status_counts = df_filtered['status_gugatan'].value_counts().reset_index()
        status_counts.columns = ['status', 'jumlah']
        fig_bar_status = px.bar(status_counts, x='status', y='jumlah',
                                title='Distribusi Status Gugatan')
        st.plotly_chart(fig_bar_status, use_container_width=True)

    st.markdown("---")


    # --- Analisis Temporal ---
    st.header("Analisis Temporal")
    col1, col2 = st.columns(2)
    with col1:
        # Line Chart: Tren Tahunan
        yearly_counts = df_filtered.groupby('tahun_cerai').size().reset_index(name='jumlah')
        fig_line_trend = px.line(yearly_counts, x='tahun_cerai', y='jumlah',
                                 title='Tren Jumlah Perkara per Tahun', markers=True)
        fig_line_trend.update_xaxes(title='Tahun')
        fig_line_trend.update_yaxes(title='Jumlah Kasus')
        st.plotly_chart(fig_line_trend, use_container_width=True)
        
    with col2:
        # Histogram: Durasi Pernikahan
        df_duration = df_filtered.dropna(subset=['tahun_nikah'])
        fig_hist_duration = px.histogram(df_duration, x='tahun_nikah', nbins=20,
                                         title='Distribusi Durasi Pernikahan (Tahun)')
        fig_hist_duration.update_xaxes(title='Durasi Pernikahan (Tahun)')
        st.plotly_chart(fig_hist_duration, use_container_width=True)

    st.markdown("---")


    # --- Analisis Lanjutan Interaktif ---
    st.header("Analisis Interaktif Lanjutan")
    
    col1, col2 = st.columns(2)
    with col1:
        # Sunburst Chart: Alasan berdasarkan Gender
        df_sunburst = df_filtered.groupby(['jk_penggugat', 'alasan_utama']).size().reset_index(name='count')
        fig_sunburst = px.sunburst(
            df_sunburst,
            path=['jk_penggugat', 'alasan_utama'],
            values='count',
            title='Sebaran Alasan berdasarkan Gender Penggugat'
        )
        st.plotly_chart(fig_sunburst, use_container_width=True)

    with col2:
        # Box Plot: Durasi Pernikahan berdasarkan Alasan
        df_box = df_filtered.dropna(subset=['tahun_nikah'])
        fig_box = px.box(
            df_box,
            x='alasan_utama',
            y='tahun_nikah',
            title='Distribusi Durasi Nikah per Alasan',
            labels={'alasan_utama': 'Alasan Perceraian', 'tahun_nikah': 'Durasi Pernikahan (Tahun)'}
        )
        st.plotly_chart(fig_box, use_container_width=True)

    st.markdown("---")

    # --- Data Mentah ---
    with st.expander("Lihat Data Mentah yang Difilter"):
        st.dataframe(df_filtered)

else:
    st.warning("Data tidak berhasil dimuat. Pastikan file 'Data Presentasii.xlsx' berada di folder yang sama.")