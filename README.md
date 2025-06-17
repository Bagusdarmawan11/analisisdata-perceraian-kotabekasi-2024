# Analisis Komprehensif dan Visualisasi Data Perceraian di Bekasi

Proyek ini menyajikan analisis mendalam terhadap data putusan perceraian yang dikabulkan oleh Pengadilan Agama Bekasi. Tujuannya adalah untuk mengidentifikasi pola, tren, dan faktor-faktor dominan yang melatarbelakangi kasus perceraian di wilayah ini. Hasil analisis disajikan dalam sebuah dasbor interaktif yang dibangun menggunakan Streamlit.

 *(Catatan: Gambar ini adalah contoh ilustrasi. Anda dapat menggantinya dengan tangkapan layar dasbor Anda sendiri)*

## 📂 Struktur Proyek

```
.
├── Dataset-Perceraian.csv      # Kumpulan data mentah kasus perceraian
├── Visualisasi_Data_Perceraian.ipynb # Notebook analisis eksplorasi data (EDA)
├── Dashboard                   # Skrip utama untuk menjalankan aplikasi Streamlit
|   ├── dashboard.py
|   ├── requirements.txt        # Daftar dependensi Python yang dibutuhkan
└── README.md                   # Dokumentasi proyek (file ini)
```

## Latar Belakang

Perceraian merupakan fenomena sosial kompleks dengan dampak yang signifikan bagi individu, keluarga, dan masyarakat. Memahami faktor-faktor pendorongnya adalah langkah krusial untuk merancang program intervensi dan dukungan yang efektif. Proyek ini lahir dari kebutuhan untuk menganalisis data perceraian secara kuantitatif di wilayah Bekasi, guna mengubah data mentah menjadi wawasan yang dapat ditindaklanjuti.

## 📊 Dataset

Data utama yang digunakan adalah `Dataset-Perceraian.csv`, yang berisi catatan putusan perceraian yang telah dikabulkan. Setiap baris merepresentasikan satu kasus unik dengan kolom-kolom berikut:

  * `no_putusan`: Nomor unik untuk setiap putusan.
  * `domisili_penggugat`: Wilayah domisili pihak yang mengajukan gugatan.
  * `jenis_kelamin_penggugat` & `jenis_kelamin_tergugat`: Jenis kelamin pihak penggugat dan tergugat.
  * `tanggal_pernikahan` & `tanggal_putusan`: Tanggal pernikahan dan tanggal putusan cerai.
  * `umur_pernikahan_tahun` & `umur_pernikahan_bulan`: Durasi pernikahan dalam tahun dan bulan.
  * `pertengkaran`, `perselingkuhan`, `kdrt`, `ekonomi`: Faktor-faktor penyebab perceraian (diisi dengan "Ya" jika menjadi alasan).
  * `amar_putusan`: Detail putusan hukum.

## 📈 Analisis & Temuan Utama

Analisis data eksploratif dilakukan dalam *notebook* `Visualisasi_Data_Perceraian.ipynb`. Beberapa temuan kunci dari analisis tersebut adalah:

1.  **Durasi Pernikahan Kritis**: Mayoritas perceraian (sekitar **41%**) terjadi pada **5 tahun pertama pernikahan**. Rentang ini merupakan periode paling rentan bagi pasangan.
2.  **Faktor Pemicu Dominan**: **Pertengkaran** dan **Masalah Ekonomi** adalah dua alasan utama yang paling sering muncul dalam gugatan cerai. Seringkali, kedua faktor ini muncul bersamaan sebagai pemicu ganda.
3.  **Perbedaan Gender dalam Gugatan**:
      * Gugatan oleh **Perempuan** (Cerai Gugat) lebih sering didasari oleh faktor **Ekonomi** dan **KDRT**.
      * Gugatan oleh **Laki-laki** (Cerai Talak) hampir secara eksklusif didominasi oleh alasan **Pertengkaran**.
4.  **Distribusi Geografis & Waktu**:
      * **Bekasi Utara** tercatat sebagai wilayah dengan jumlah kasus perceraian tertinggi secara keseluruhan.
      * Secara temporal, putusan paling banyak dikeluarkan pada hari **Kamis**, merefleksikan jadwal persidangan. Puncak kasus tahunan terjadi pada bulan **Agustus**.

## 🚀 Dasbor Interaktif

Untuk mempermudah eksplorasi data, sebuah dasbor interaktif (`dashboard.py`) telah dikembangkan menggunakan **Streamlit**. Dasbor ini memungkinkan pengguna untuk:

  * **Memfilter Data**: Menyaring data berdasarkan domisili penggugat, jenis kelamin, dan rentang usia pernikahan.
  * **Melihat Metrik Utama**: Menampilkan ringkasan statistik seperti total kasus, rata-rata usia pernikahan, dan faktor penyebab utama.
  * **Visualisasi Dinamis**: Menjelajahi data melalui berbagai grafik interaktif, termasuk:
      * Peta Sebaran Kasus per Wilayah.
      * Distribusi Usia Pernikahan.
      * Analisis Faktor Penyebab Perceraian.
      * Tren Bulanan dan Pola Harian Putusan.

## ⚙️ Cara Menjalankan Proyek

Untuk menjalankan dasbor ini di lingkungan lokal Anda, ikuti langkah-langkah berikut:

### 1\. Prasyarat

  * Python 3.7+
  * Pip (manajer paket Python)

### 2\. Instalasi

Clone repositori ini (jika ada) atau cukup unduh semua file ke dalam satu direktori. Kemudian, instal semua dependensi yang diperlukan menggunakan file `requirements.txt`.

```bash
pip install -r requirements.txt
```

Dependensi utama yang akan diinstal adalah:

  * `streamlit`
  * `pandas`
  * `plotly-express`
  * `numpy`

### 3\. Menjalankan Dasbor

Setelah instalasi selesai, jalankan aplikasi Streamlit dengan perintah berikut di terminal Anda dari direktori proyek:

```bash
streamlit run dashboard.py
```

Aplikasi akan terbuka secara otomatis di *browser web default* Anda.

## Rekomendasi

Berdasarkan analisis, direkomendasikan agar program penyuluhan dan konseling keluarga difokuskan pada:

  * **Target Audiens**: Pasangan pada rentang pernikahan **0-5 tahun**.
  * **Target Wilayah**: Prioritas pada wilayah dengan kasus tertinggi seperti **Bekasi Utara**.
  * **Materi Program**: Penekanan pada **manajemen konflik** dan **literasi keuangan** untuk mengatasi akar masalah yang paling dominan.
