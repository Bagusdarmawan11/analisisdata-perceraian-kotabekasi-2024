# ======================================
# DASHBOARD ANALISIS DATA PERDATA AGAMA
# Streamlit Dashboard Application
# ======================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
from datetime import datetime
import warnings

warnings.filterwarnings('ignore')

# ======================================
# KONFIGURASI HALAMAN
# ======================================

st.set_page_config(
    page_title="Dashboard Perdata Agama",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ======================================
# LOAD DATA DAN SETUP
# ======================================

@st.cache_data
def load_data():
    """Load dan cache data"""
    try:
        df = pd.read_csv('data_perdata_agama_clean.csv')
        
        # Konversi tipe data
        date_columns = ['Tanggal Pernikahan', 'Tanggal Perceraian']
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        # Konversi kolom numerik
        numeric_columns = ['Pertengkaran', 'Perselingkuhan', 'KDRT', 'Ekonomi', 'Jumlah Bulan']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        return df
    except FileNotFoundError:
        st.error("❌ File 'data_perdata_agama_clean.csv' tidak ditemukan!")
        st.info("📝 Pastikan Anda telah menjalankan notebook analisis terlebih dahulu.")
        return None

@st.cache_data
def load_summary_stats():
    """Load summary statistics"""
    try:
        with open('summary_stats.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return None

# ======================================
# FUNGSI UTILITAS
# ======================================

def create_metric_card(title, value, delta=None, delta_color="normal"):
    """Membuat metric card"""
    col1, col2 = st.columns([3, 1])
    with col1:
        st.metric(
            label=title,
            value=value,
            delta=delta,
            delta_color=delta_color
        )

def apply_filters(df):
    """Apply filters dari sidebar"""
    filtered_df = df.copy()
    
    # Filter Domisili
    if 'domisili_filter' in st.session_state and st.session_state.domisili_filter:
        if st.session_state.domisili_filter != 'Semua':
            filtered_df = filtered_df[filtered_df['Tempat Domisili'] == st.session_state.domisili_filter]
    
    # Filter Jenis Kelamin
    if 'gender_filter' in st.session_state and st.session_state.gender_filter:
        if st.session_state.gender_filter != 'Semua':
            filtered_df = filtered_df[filtered_df['Jenis Kelamin Penggugat'] == st.session_state.gender_filter]
    
    # Filter Status Gugatan
    if 'status_filter' in st.session_state and st.session_state.status_filter:
        if st.session_state.status_filter != 'Semua':
            filtered_df = filtered_df[filtered_df['Status Gugatan'] == st.session_state.status_filter]
    
    return filtered_df

# ======================================
# MAIN DASHBOARD
# ======================================

def main():
    # Header Dashboard
    st.title("⚖️ Dashboard Analisis Data Perdata Agama")
    st.markdown("---")
    
    # Load data
    df = load_data()
    if df is None:
        st.stop()
    
    summary_stats = load_summary_stats()
    
    # ======================================
    # SIDEBAR FILTERS
    # ======================================
    
    st.sidebar.header("🎛️ Filter Data")
    
    # Filter Domisili
    domisili_options = ['Semua'] + sorted(df['Tempat Domisili'].dropna().unique().tolist())
    domisili_filter = st.sidebar.selectbox(
        "📍 Pilih Domisili:",
        options=domisili_options,
        key='domisili_filter'
    )
    
    # Filter Jenis Kelamin
    gender_options = ['Semua'] + sorted(df['Jenis Kelamin Penggugat'].dropna().unique().tolist())
    gender_filter = st.sidebar.selectbox(
        "👤 Pilih Jenis Kelamin Penggugat:",
        options=gender_options,
        key='gender_filter'
    )
    
    # Filter Status Gugatan
    status_options = ['Semua'] + sorted(df['Status Gugatan'].dropna().unique().tolist())
    status_filter = st.sidebar.selectbox(
        "📋 Pilih Status Gugatan:",
        options=status_options,
        key='status_filter'
    )
    
    # Apply filters
    filtered_df = apply_filters(df)
    
    st.sidebar.markdown("---")
    st.sidebar.info(f"📊 Data yang ditampilkan: **{len(filtered_df)}** dari **{len(df)}** kasus")
    
    # ======================================
    # METRICS OVERVIEW
    # ======================================
    
    st.header("📊 Overview Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Kasus",
            value=len(filtered_df),
            delta=f"{len(filtered_df) - len(df)}" if len(filtered_df) != len(df) else None
        )
    
    with col2:
        success_rate = (filtered_df['Status Gugatan'] == 'Dikabulkan').sum() / len(filtered_df) * 100
        st.metric(
            label="Tingkat Keberhasilan",
            value=f"{success_rate:.1f}%"
        )
    
    with col3:
        valid_duration = filtered_df[filtered_df['Jumlah Bulan'].notna()]
        avg_duration = valid_duration['Jumlah Bulan'].mean() / 12 if len(valid_duration) > 0 else 0
        st.metric(
            label="Rata-rata Durasi Nikah",
            value=f"{avg_duration:.1f} tahun"
        )
    
    with col4:
        total_reasons = (filtered_df['Pertengkaran'] + filtered_df['Perselingkuhan'] + 
                        filtered_df['KDRT'] + filtered_df['Ekonomi']).sum()
        st.metric(
            label="Total Alasan",
            value=int(total_reasons)
        )
    
    st.markdown("---")
    
    # ======================================
    # VISUALISASI UTAMA
    # ======================================
    
    # Row 1: Distribusi Domisili dan Jenis Kelamin
    st.header("🏠 Distribusi Geografis dan Demografis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📍 Distribusi per Domisili")
        domisili_counts = filtered_df['Tempat Domisili'].value_counts().head(10)
        
        fig_domisili = px.bar(
            x=domisili_counts.values,
            y=domisili_counts.index,
            orientation='h',
            title="Top 10 Domisili dengan Kasus Terbanyak",
            color=domisili_counts.values,
            color_continuous_scale='Blues'
        )
        fig_domisili.update_layout(
            height=400,
            xaxis_title="Jumlah Kasus",
            yaxis_title="Domisili",
            showlegend=False
        )
        st.plotly_chart(fig_domisili, use_container_width=True)
    
    with col2:
        st.subheader("👤 Distribusi Jenis Kelamin Penggugat")
        gender_counts = filtered_df['Jenis Kelamin Penggugat'].value_counts()
        
        fig_gender = px.pie(
            values=gender_counts.values,
            names=gender_counts.index,
            title="Persentase Jenis Kelamin Penggugat",
            color_discrete_map={
                'Perempuan': '#FF69B4',
                'Laki Laki': '#4169E1', 
                'Tidak diketahui': '#808080'
            }
        )
        fig_gender.update_traces(textposition='inside', textinfo='percent+label')
        fig_gender.update_layout(height=400)
        st.plotly_chart(fig_gender, use_container_width=True)
    
    st.markdown("---")
    
    # Row 2: Status Gugatan dan Alasan Perceraian
    st.header("⚖️ Analisis Status Gugatan dan Alasan Perceraian")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📋 Status Gugatan")
        status_counts = filtered_df['Status Gugatan'].value_counts()
        
        fig_status = px.donut(
            values=status_counts.values,
            names=status_counts.index,
            title="Distribusi Status Gugatan",
            color_discrete_map={
                'Dikabulkan': '#28a745',
                'Cabut Laporan': '#ffc107',
                'Ditolak': '#dc3545',
                'Gugur': '#6c757d'
            }
        )
        fig_status.update_traces(textposition='inside', textinfo='percent+label')
        fig_status.update_layout(height=400)
        st.plotly_chart(fig_status, use_container_width=True)
    
    with col2:
        st.subheader("💔 Alasan Perceraian")
        alasan_data = {
            'Pertengkaran': filtered_df['Pertengkaran'].sum(),
            'Perselingkuhan': filtered_df['Perselingkuhan'].sum(),
            'KDRT': filtered_df['KDRT'].sum(),
            'Ekonomi': filtered_df['Ekonomi'].sum()
        }
        
        fig_alasan = px.bar(
            x=list(alasan_data.keys()),
            y=list(alasan_data.values()),
            title="Distribusi Alasan Perceraian",
            color=list(alasan_data.values()),
            color_continuous_scale='Reds'
        )
        fig_alasan.update_layout(
            height=400,
            xaxis_title="Alasan Perceraian",
            yaxis_title="Jumlah Kasus",
            showlegend=False
        )
        st.plotly_chart(fig_alasan, use_container_width=True)
    
    st.markdown("---")
    
    # Row 3: Analisis Durasi Pernikahan
    st.header("⏰ Analisis Durasi Pernikahan")
    
    col1, col2 = st.columns(2)
    
    valid_duration = filtered_df[filtered_df['Jumlah Bulan'].notna()]
    
    if len(valid_duration) > 0:
        with col1:
            st.subheader("📊 Distribusi Durasi Pernikahan")
            fig_duration = px.histogram(
                valid_duration,
                x='Jumlah Bulan',
                nbins=20,
                title="Histogram Durasi Pernikahan (dalam Bulan)",
                color_discrete_sequence=['#ff7f0e']
            )
            fig_duration.add_vline(
                x=valid_duration['Jumlah Bulan'].mean(),
                line_dash="dash",
                line_color="red",
                annotation_text=f"Rata-rata: {valid_duration['Jumlah Bulan'].mean():.1f} bulan"
            )
            fig_duration.update_layout(height=400)
            st.plotly_chart(fig_duration, use_container_width=True)
        
        with col2:
            st.subheader("📈 Statistik Durasi")
            
            # Box plot
            fig_box = px.box(
                valid_duration,
                y='Jumlah Bulan',
                title="Box Plot Durasi Pernikahan",
                color_discrete_sequence=['#2ca02c']
            )
            fig_box.update_layout(height=400)
            st.plotly_chart(fig_box, use_container_width=True)
            
            # Statistik deskriptif
            st.write("**Statistik Deskriptif:**")
            stats_df = pd.DataFrame({
                'Statistik': ['Rata-rata', 'Median', 'Minimum', 'Maksimum', 'Std Deviasi'],
                'Nilai (Bulan)': [
                    f"{valid_duration['Jumlah Bulan'].mean():.1f}",
                    f"{valid_duration['Jumlah Bulan'].median():.1f}",
                    f"{valid_duration['Jumlah Bulan'].min():.0f}",
                    f"{valid_duration['Jumlah Bulan'].max():.0f}",
                    f"{valid_duration['Jumlah Bulan'].std():.1f}"
                ],
                'Nilai (Tahun)': [
                    f"{valid_duration['Jumlah Bulan'].mean()/12:.1f}",
                    f"{valid_duration['Jumlah Bulan'].median()/12:.1f}",
                    f"{valid_duration['Jumlah Bulan'].min()/12:.1f}",
                    f"{valid_duration['Jumlah Bulan'].max()/12:.1f}",
                    f"{valid_duration['Jumlah Bulan'].std()/12:.1f}"
                ]
            })
            st.dataframe(stats_df, use_container_width=True)
    else:
        st.warning("⚠️ Tidak ada data durasi pernikahan yang valid untuk ditampilkan.")
    
    st.markdown("---")
    
    # ======================================
    # ANALISIS LANJUTAN
    # ======================================
    
    st.header("🔍 Analisis Lanjutan")
    
    # Heatmap korelasi alasan perceraian dengan domisili
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🗺️ Heatmap Alasan vs Domisili")
        
        # Membuat crosstab
        domisili_top = filtered_df['Tempat Domisili'].value_counts().head(8).index
        df_top_domisili = filtered_df[filtered_df['Tempat Domisili'].isin(domisili_top)]
        
        heatmap_data = []
        for domisili in domisili_top:
            domisili_data = df_top_domisili[df_top_domisili['Tempat Domisili'] == domisili]
            heatmap_data.append([
                domisili_data['Pertengkaran'].sum(),
                domisili_data['Perselingkuhan'].sum(),
                domisili_data['KDRT'].sum(),
                domisili_data['Ekonomi'].sum()
            ])
        
        fig_heatmap = px.imshow(
            heatmap_data,
            x=['Pertengkaran', 'Perselingkuhan', 'KDRT', 'Ekonomi'],
            y=domisili_top,
            title="Heatmap Alasan Perceraian per Domisili",
            color_continuous_scale='YlOrRd',
            aspect='auto'
        )
        fig_heatmap.update_layout(height=400)
        st.plotly_chart(fig_heatmap, use_container_width=True)
    
    with col2:
        st.subheader("📊 Analisis Gender vs Status")
        
        # Stacked bar chart gender vs status
        gender_status = pd.crosstab(filtered_df['Jenis Kelamin Penggugat'], 
                                   filtered_df['Status Gugatan'])
        
        fig_gender_status = px.bar(
            gender_status,
            title="Distribusi Status Gugatan per Jenis Kelamin",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig_gender_status.update_layout(
            height=400,
            xaxis_title="Jenis Kelamin",
            yaxis_title="Jumlah Kasus",
            legend_title="Status Gugatan"
        )
        st.plotly_chart(fig_gender_status, use_container_width=True)
    
    st.markdown("---")
    
    # ======================================
    # DATA TABLE
    # ======================================
    
    st.header("📋 Tabel Data Detail")
    
    # Pilihan kolom untuk ditampilkan
    all_columns = filtered_df.columns.tolist()
    selected_columns = st.multiselect(
        "Pilih kolom yang ingin ditampilkan:",
        options=all_columns,
        default=['Nomor Putusan', 'Tempat Domisili', 'Jenis Kelamin Penggugat', 
                'Status Gugatan', 'Umur Pernikahan']
    )
    
    if selected_columns:
        st.dataframe(
            filtered_df[selected_columns].head(100),
            use_container_width=True,
            height=400
        )
        
        # Download button
        csv = filtered_df[selected_columns].to_csv(index=False)
        st.download_button(
            label="📥 Download Data (CSV)",
            data=csv,
            file_name=f"data_perdata_agama_filtered_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    
    st.markdown("---")
    
    # ======================================
    # FOOTER DAN INFO
    # ======================================
    
    st.header("ℹ️ Informasi Dashboard")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("""
        **📊 Dashboard ini menampilkan:**
        - Analisis distribusi kasus per domisili
        - Profil demografis penggugat
        - Status dan outcome gugatan
        - Analisis alasan perceraian
        - Statistik durasi pernikahan
        - Korelasi antar variabel
        """)
    
    with col2:
        st.success(f"""
        **📈 Ringkasan Data Saat Ini:**
        - Total kasus: {len(filtered_df):,}
        - Lokasi unik: {filtered_df['Tempat Domisili'].nunique()}
        - Tingkat keberhasilan: {(filtered_df['Status Gugatan'] == 'Dikabulkan').sum() / len(filtered_df) * 100:.1f}%
        - Periode: 2024
        """)
    
    st.markdown("---")
    st.markdown("*Dashboard dibuat dengan ❤️ menggunakan Streamlit dan Plotly*")

# ======================================
# RUN DASHBOARD
# ======================================

if __name__ == "__main__":
    main()
