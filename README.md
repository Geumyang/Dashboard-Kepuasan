# 🛒 Proyek Analisis Data: E-Commerce Public Dataset

## 📋 Deskripsi Proyek
Proyek ini merupakan analisis data menggunakan **E-Commerce Public Dataset (Olist)** yang mencakup data transaksi e-commerce di Brasil dari tahun 2016 hingga 2018. Analisis mencakup tren penjualan, kategori produk terlaris, distribusi geografis pelanggan, serta segmentasi pelanggan menggunakan teknik RFM Analysis dan Clustering.

## 🔍 Pertanyaan Bisnis
1. Bagaimana tren jumlah pesanan dan total pendapatan per bulan? Apakah ada pola musiman yang dapat dimanfaatkan untuk strategi bisnis?
2. Kategori produk apa yang paling banyak terjual dan menghasilkan pendapatan tertinggi?
3. Bagaimana distribusi geografis pelanggan dan penjual di seluruh wilayah Brasil?
4. Bagaimana segmentasi pelanggan berdasarkan perilaku pembelian (RFM Analysis)?

## 📁 Struktur Direktori
```
submission/
├── dashboard/
│   ├── main_data.csv       # Master dataset hasil preprocessing
│   └── dashboard.py        # Script Streamlit dashboard
├── data/
│   ├── orders_dataset.csv
│   ├── order_items_dataset.csv
│   ├── order_payments_dataset.csv
│   ├── order_reviews_dataset.csv
│   ├── customers_dataset.csv
│   ├── sellers_dataset.csv
│   ├── products_dataset.csv
│   ├── product_category_name_translation.csv
│   └── geolocation_dataset.csv
├── notebook.ipynb          # Notebook analisis data lengkap
├── README.md               # Dokumentasi proyek
├── requirements.txt        # Daftar library yang digunakan
└── url.txt                 # URL deployment Streamlit Cloud
```

## 🚀 Cara Menjalankan Dashboard

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Jalankan Dashboard
```bash
streamlit run dashboard/dashboard.py
```

### 3. Buka di Browser
Dashboard akan otomatis terbuka di `http://localhost:8501`

## 📊 Teknik Analisis yang Digunakan
- **Exploratory Data Analysis (EDA)** — Eksplorasi data untuk menemukan pola dan insight
- **RFM Analysis** — Segmentasi pelanggan berdasarkan Recency, Frequency, dan Monetary
- **Geospatial Analysis** — Analisis distribusi geografis menggunakan Folium Heatmap
- **Clustering (Binning)** — Pengelompokan pelanggan berdasarkan total pengeluaran dan frekuensi pembelian

## 🛠️ Library yang Digunakan
- `pandas` — Manipulasi dan analisis data
- `numpy` — Komputasi numerik
- `matplotlib` & `seaborn` — Visualisasi data
- `folium` — Peta interaktif geospatial
- `streamlit` — Dashboard interaktif
- `streamlit-folium` — Integrasi Folium ke Streamlit

## 👤 Author
- **Nama:** Melani Sulistiawati
- **Email:** cdcc008d6x2288@student.devacademy.id
- **ID Dicoding:** CDCC008D6X2288
