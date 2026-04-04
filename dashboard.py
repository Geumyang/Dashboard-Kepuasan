import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium
import warnings
warnings.filterwarnings('ignore')

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="E-Commerce Dashboard",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
# STYLING
# ─────────────────────────────────────────────
st.markdown("""
<style>
    .main-header {
        font-size: 2rem;
        font-weight: 700;
        color: #2c3e50;
        text-align: center;
        padding: 1rem 0 0.5rem 0;
    }
    .sub-header {
        font-size: 1rem;
        color: #7f8c8d;
        text-align: center;
        margin-bottom: 1.5rem;
    }
    .section-title {
        font-size: 1.3rem;
        font-weight: 600;
        color: #2c3e50;
        border-left: 4px solid #3498db;
        padding-left: 0.75rem;
        margin: 1rem 0;
    }
    .insight-box {
        background-color: #eaf4fb;
        border-left: 4px solid #3498db;
        padding: 0.75rem 1rem;
        border-radius: 0 8px 8px 0;
        font-size: 0.9rem;
        color: #2c3e50;
        margin-top: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# LOAD DATA 
# ─────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv('main_data.csv')
    df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])
    df['order_year_month'] = df['order_purchase_timestamp'].dt.to_period('M').astype(str)
    return df

master_df = load_data()

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/shopping-cart.png", width=80)
    st.title("🛒 E-Commerce\nDashboard")
    st.markdown("---")

    st.markdown("### 📅 Filter Rentang Waktu")
    min_date = master_df['order_purchase_timestamp'].min().date()
    max_date = master_df['order_purchase_timestamp'].max().date()
    start_date = st.date_input("Tanggal Mulai",
                               value=pd.Timestamp('2017-01-01').date(),
                               min_value=min_date, max_value=max_date)
    end_date   = st.date_input("Tanggal Akhir",
                               value=max_date,
                               min_value=min_date, max_value=max_date)

    st.markdown("### 🗂️ Navigasi Halaman")
    menu = st.radio("Pilih Halaman", [
        "📊 Overview",
        "📈 Tren Penjualan",
        "🏷️ Kategori Produk",
        "🗺️ Geospatial",
        "👥 RFM Analysis",
        "🔵 Clustering"
    ])
    st.markdown("---")
    st.caption("Data:E-Commerce Public Dataset")

# Filter berdasarkan tanggal
mask = ((master_df['order_purchase_timestamp'].dt.date >= start_date) &
        (master_df['order_purchase_timestamp'].dt.date <= end_date))
filtered_df = master_df[mask].copy()

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.markdown('<div class="main-header">🛒 E-Commerce Public Dataset Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Analisis komprehensif performa penjualan, perilaku pelanggan, dan distribusi geografis</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
# KPI METRICS
# ─────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("📦 Total Pesanan", f"{filtered_df['order_id'].nunique():,}")
with col2:
    st.metric("💰 Total Pendapatan", f"$ {filtered_df['payment_value'].sum()/1e6:.2f}M")
with col3:
    st.metric("👤 Pelanggan Unik", f"{filtered_df['customer_unique_id'].nunique():,}")
with col4:
    avg_val = filtered_df.groupby('order_id')['payment_value'].sum().mean()
    st.metric("🧾 Rata-rata Nilai Pesanan", f"$ {avg_val:.2f}")

st.markdown("---")

# ═══════════════════════════════════════════════
# HALAMAN: OVERVIEW
# ═══════════════════════════════════════════════
if menu == "📊 Overview":
    st.markdown('<div class="section-title">📊 Ringkasan Performa Bisnis</div>', unsafe_allow_html=True)

    col_a, col_b = st.columns(2)

    with col_a:
        top5 = filtered_df.groupby('product_category_name').agg(
            total_item=('order_id', 'count')
        ).reset_index().sort_values('total_item', ascending=False).head(5)

        fig, ax = plt.subplots(figsize=(7, 4))
        ax.barh(top5['product_category_name'][::-1], top5['total_item'][::-1],
                color=sns.color_palette('Blues_d', 5))
        ax.set_title('Top 5 Kategori Produk (Volume)', fontsize=12, fontweight='bold')
        ax.set_xlabel('Jumlah Item')
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    with col_b:
        status_dist = master_df['order_status'].value_counts()
        fig, ax = plt.subplots(figsize=(7, 4))
        ax.pie(status_dist.values, labels=status_dist.index, autopct='%1.1f%%',
               colors=sns.color_palette('Set2', len(status_dist)), startangle=90)
        ax.set_title('Distribusi Status Pesanan', fontsize=12, fontweight='bold')
        st.pyplot(fig)
        plt.close()

    st.markdown('<div class="insight-box">💡 <b>Insight:</b> Sebagian besar pesanan (~97%) berstatus <i>delivered</i>. Kategori bed_bath_table mendominasi volume penjualan, diikuti health_beauty dan sports_leisure.</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════
# HALAMAN: TREN PENJUALAN
# ═══════════════════════════════════════════════
elif menu == "📈 Tren Penjualan":
    st.markdown('<div class="section-title">📈 Tren Jumlah Pesanan & Pendapatan per Bulan</div>', unsafe_allow_html=True)

    monthly = filtered_df.groupby('order_year_month').agg(
        total_order=('order_id', 'nunique'),
        total_pendapatan=('payment_value', 'sum')
    ).reset_index().sort_values('order_year_month')

    monthly = monthly[
        (monthly['order_year_month'] >= '2017-01') &
        (monthly['order_year_month'] <= '2018-08')
    ]

    fig, ax1 = plt.subplots(figsize=(14, 6))
    x = range(len(monthly))

    ax1.bar(x, monthly['total_order'], color='steelblue', alpha=0.7, label='Jumlah Pesanan')
    ax1.set_ylabel('Jumlah Pesanan', color='steelblue', fontsize=11)
    ax1.tick_params(axis='y', labelcolor='steelblue')
    ax1.set_xticks(x)
    ax1.set_xticklabels(monthly['order_year_month'], rotation=45, ha='right', fontsize=8)

    ax2 = ax1.twinx()
    ax2.plot(x, monthly['total_pendapatan'], color='darkorange', marker='o',
             linewidth=2, markersize=5, label='Total Pendapatan ($)')
    ax2.set_ylabel('Total Pendapatan ($)', color='darkorange', fontsize=11)
    ax2.tick_params(axis='y', labelcolor='darkorange')
    ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f'${v/1e6:.1f}M'))

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
    plt.title('Tren Jumlah Pesanan dan Total Pendapatan per Bulan\n(Januari 2017 - Agustus 2018)',
              fontsize=13, fontweight='bold')
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

    st.markdown('<div class="insight-box">💡 <b>Insight:</b> Tren menunjukkan pertumbuhan konsisten sepanjang 2017-2018. Lonjakan signifikan terjadi pada November 2017. Strategi promosi Q4 sangat direkomendasikan.</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════
# HALAMAN: KATEGORI PRODUK
# ═══════════════════════════════════════════════
elif menu == "🏷️ Kategori Produk":
    st.markdown('<div class="section-title">🏷️ Analisis Kategori Produk</div>', unsafe_allow_html=True)

    n_top = st.slider("Tampilkan Top N Kategori:", min_value=5, max_value=20, value=10)

    cat_data = filtered_df.groupby('product_category_name').agg(
        total_item=('order_id', 'count'),
        total_pendapatan=('price', 'sum')
    ).reset_index()

    col1, col2 = st.columns(2)

    with col1:
        top_qty = cat_data.sort_values('total_item', ascending=False).head(n_top).sort_values('total_item')
        fig, ax = plt.subplots(figsize=(7, n_top * 0.45 + 1))
        ax.barh(top_qty['product_category_name'], top_qty['total_item'],
                color=sns.color_palette('Blues_d', n_top))
        ax.set_title(f'Top {n_top} Kategori by Volume', fontsize=12, fontweight='bold')
        ax.set_xlabel('Jumlah Item Terjual')
        for i, val in enumerate(top_qty['total_item']):
            ax.text(val + 10, i, f'{val:,}', va='center', fontsize=8)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    with col2:
        top_rev = cat_data.sort_values('total_pendapatan', ascending=False).head(n_top).sort_values('total_pendapatan')
        fig, ax = plt.subplots(figsize=(7, n_top * 0.45 + 1))
        ax.barh(top_rev['product_category_name'], top_rev['total_pendapatan'],
                color=sns.color_palette('Oranges_d', n_top))
        ax.set_title(f'Top {n_top} Kategori by Pendapatan', fontsize=12, fontweight='bold')
        ax.set_xlabel('Total Pendapatan (R$)')
        ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f'R${v/1e6:.1f}M'))
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    st.markdown('<div class="insight-box">💡 <b>Insight:</b> bed_bath_table memimpin volume penjualan. Dari sisi pendapatan, health_beauty dan watches_gifts unggul — mencerminkan harga rata-rata yang lebih tinggi per transaksi.</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════
# HALAMAN: GEOSPATIAL
# ═══════════════════════════════════════════════
elif menu == "🗺️ Geospatial":
    st.markdown('<div class="section-title">🗺️ Distribusi Geografis Pelanggan & Penjual</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        rev_state = filtered_df.groupby('customer_state').agg(
            total_pendapatan=('payment_value', 'sum')
        ).reset_index().sort_values('total_pendapatan', ascending=False)

        fig, ax = plt.subplots(figsize=(7, 5))
        ax.bar(rev_state['customer_state'], rev_state['total_pendapatan'],
               color=sns.color_palette('viridis', len(rev_state)))
        ax.set_title('Total Pendapatan per Negara Bagian', fontsize=12, fontweight='bold')
        ax.set_xlabel('State')
        ax.set_ylabel('Pendapatan (R$)')
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f'R${v/1e6:.1f}M'))
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    with col2:
        city_data = filtered_df.groupby('customer_city').size().reset_index(name='count')
        city_data = city_data.sort_values('count', ascending=False).head(10)

        fig, ax = plt.subplots(figsize=(7, 5))
        ax.barh(city_data['customer_city'][::-1], city_data['count'][::-1],
                color=sns.color_palette('rocket', 10))
        ax.set_title('Top 10 Kota Asal Pelanggan', fontsize=12, fontweight='bold')
        ax.set_xlabel('Jumlah Transaksi')
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    # Heatmap — gunakan lat/lng dari main_data jika tersedia
    st.markdown("#### 🗺️ Heatmap Lokasi Pelanggan")
    if 'lat' in filtered_df.columns and 'lng' in filtered_df.columns:
        geo_data = filtered_df[['lat', 'lng']].dropna()
        m = folium.Map(location=[-14.235, -51.9253], zoom_start=4, tiles='CartoDB positron')
        sample = geo_data.sample(min(3000, len(geo_data)), random_state=42)
        HeatMap(sample.values.tolist(), radius=8, blur=15, min_opacity=0.4,
                gradient={0.2: 'blue', 0.5: 'lime', 1: 'red'}).add_to(m)
        st_folium(m, width=900, height=500)
    else:
        st.info("💡 Untuk menampilkan heatmap, tambahkan kolom 'lat' dan 'lng' ke main_data.csv dengan merge geolocation_dataset.")

    st.markdown('<div class="insight-box">💡 <b>Insight:</b> Konsentrasi pelanggan sangat tinggi di São Paulo (SP) dan sekitarnya. Wilayah utara Brasil merupakan peluang ekspansi yang belum dioptimalkan.</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════
# HALAMAN: RFM ANALYSIS
# ═══════════════════════════════════════════════
elif menu == "👥 RFM Analysis":
    st.markdown('<div class="section-title">👥 RFM Analysis - Segmentasi Pelanggan</div>', unsafe_allow_html=True)

    reference_date = filtered_df['order_purchase_timestamp'].max() + pd.Timedelta(days=1)

    rfm_df = filtered_df.groupby('customer_unique_id').agg(
        Recency=('order_purchase_timestamp', lambda x: (reference_date - x.max()).days),
        Frequency=('order_id', 'nunique'),
        Monetary=('payment_value', 'sum')
    ).reset_index()

    rfm_df['R_Score'] = pd.qcut(rfm_df['Recency'], q=5, labels=[5, 4, 3, 2, 1])
    rfm_df['F_Score'] = pd.qcut(rfm_df['Frequency'].rank(method='first'), q=5, labels=[1, 2, 3, 4, 5])
    rfm_df['M_Score'] = pd.qcut(rfm_df['Monetary'], q=5, labels=[1, 2, 3, 4, 5])
    rfm_df['RFM_Total'] = rfm_df[['R_Score', 'F_Score', 'M_Score']].astype(int).sum(axis=1)

    def rfm_segment(score):
        if score >= 13:   return 'Champions'
        elif score >= 10: return 'Loyal Customers'
        elif score >= 7:  return 'Potential Loyalist'
        elif score >= 5:  return 'At Risk'
        else:             return 'Lost Customers'

    rfm_df['Segment'] = rfm_df['RFM_Total'].apply(rfm_segment)

    segment_order = ['Champions', 'Loyal Customers', 'Potential Loyalist', 'At Risk', 'Lost Customers']
    color_map     = dict(zip(segment_order, ['#2ecc71', '#3498db', '#f39c12', '#e74c3c', '#95a5a6']))

    col1, col2 = st.columns(2)

    with col1:
        seg_data = rfm_df['Segment'].value_counts().reindex(segment_order).dropna()
        fig, ax = plt.subplots(figsize=(6, 5))
        ax.pie(seg_data.values, labels=seg_data.index, autopct='%1.1f%%',
               colors=[color_map[s] for s in seg_data.index], startangle=90)
        ax.set_title('Distribusi Segmen Pelanggan', fontsize=12, fontweight='bold')
        st.pyplot(fig)
        plt.close()

    with col2:
        rfm_mean = rfm_df.groupby('Segment')['Monetary'].mean().reindex(segment_order).dropna()
        fig, ax = plt.subplots(figsize=(6, 5))
        ax.bar(rfm_mean.index, rfm_mean.values,
               color=[color_map[s] for s in rfm_mean.index], alpha=0.85)
        ax.set_title('Rata-rata Monetary per Segmen', fontsize=12, fontweight='bold')
        ax.set_ylabel('Rata-rata Pengeluaran (R$)')
        plt.xticks(rotation=20, ha='right')
        for i, val in enumerate(rfm_mean.values):
            ax.text(i, val + 5, f'R${val:.0f}', ha='center', fontsize=9)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    st.markdown("#### 📋 Ringkasan Segmen RFM")
    summary = rfm_df.groupby('Segment').agg(
        Jumlah_Pelanggan=('customer_unique_id', 'count'),
        Avg_Recency=('Recency', 'mean'),
        Avg_Frequency=('Frequency', 'mean'),
        Avg_Monetary=('Monetary', 'mean')
    ).round(1).reindex(segment_order).dropna()
    st.dataframe(summary, use_container_width=True)

    st.markdown('<div class="insight-box">💡 <b>Insight:</b> Sebagian besar pelanggan masuk segmen <b>Potential Loyalist</b> dan <b>Loyal Customers</b>. Strategi retensi seperti email remarketing dan diskon loyalitas diperlukan untuk mengkonversi mereka menjadi <b>Champions</b>.</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════
# HALAMAN: CLUSTERING
# ═══════════════════════════════════════════════
elif menu == "🔵 Clustering":
    st.markdown('<div class="section-title">🔵 Clustering - Segmentasi Berdasarkan Perilaku Belanja</div>', unsafe_allow_html=True)

    cust_cluster = filtered_df.groupby('customer_unique_id').agg(
        total_spend=('payment_value', 'sum'),
        total_orders=('order_id', 'nunique'),
    ).reset_index()

    spend_bins   = [0, 100, 300, 700, float('inf')]
    spend_labels = ['Low Spender\n(<R$100)', 'Medium Spender\n(R$100-300)',
                    'High Spender\n(R$300-700)', 'VIP Spender\n(>R$700)']
    cust_cluster['Spend_Segment'] = pd.cut(cust_cluster['total_spend'],
                                            bins=spend_bins, labels=spend_labels)

    freq_bins   = [0, 1, 2, 3, float('inf')]
    freq_labels = ['One-Time Buyer', 'Occasional Buyer', 'Regular Buyer', 'Frequent Buyer']
    cust_cluster['Freq_Segment'] = pd.cut(cust_cluster['total_orders'],
                                           bins=freq_bins, labels=freq_labels)

    col1, col2 = st.columns(2)

    with col1:
        spend_dist = cust_cluster['Spend_Segment'].value_counts()
        fig, ax = plt.subplots(figsize=(7, 5))
        ax.bar(spend_dist.index, spend_dist.values,
               color=['#3498db', '#2ecc71', '#f39c12', '#e74c3c'], edgecolor='white')
        ax.set_title('Segmentasi Pelanggan\nBerdasarkan Total Pengeluaran', fontsize=12, fontweight='bold')
        ax.set_xlabel('Segmen')
        ax.set_ylabel('Jumlah Pelanggan')
        for i, val in enumerate(spend_dist.values):
            pct = val / len(cust_cluster) * 100
            ax.text(i, val + 100, f'{val:,}\n({pct:.1f}%)', ha='center', fontsize=9)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    with col2:
        freq_dist = cust_cluster['Freq_Segment'].value_counts()
        fig, ax = plt.subplots(figsize=(7, 5))
        ax.bar(freq_dist.index, freq_dist.values,
               color=['#9b59b6', '#1abc9c', '#e67e22', '#c0392b'], edgecolor='white')
        ax.set_title('Segmentasi Pelanggan\nBerdasarkan Frekuensi Pembelian', fontsize=12, fontweight='bold')
        ax.set_xlabel('Segmen')
        ax.set_ylabel('Jumlah Pelanggan')
        for i, val in enumerate(freq_dist.values):
            pct = val / len(cust_cluster) * 100
            ax.text(i, val + 100, f'{val:,}\n({pct:.1f}%)', ha='center', fontsize=9)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    st.markdown("#### 🔥 Crosstab: Spend Segment vs Frequency Segment")
    cross = pd.crosstab(cust_cluster['Spend_Segment'], cust_cluster['Freq_Segment'])
    fig, ax = plt.subplots(figsize=(10, 4))
    sns.heatmap(cross, annot=True, fmt='d', cmap='YlOrRd', ax=ax, linewidths=0.5)
    ax.set_title('Distribusi Pelanggan: Spend vs Frequency Segment', fontsize=12, fontweight='bold')
    ax.set_xlabel('Frequency Segment')
    ax.set_ylabel('Spend Segment')
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

    st.markdown('<div class="insight-box">💡 <b>Insight:</b> Sekitar 42% pelanggan adalah <b>Low Spender</b> (<R$100). Lebih dari 90% pelanggan adalah <b>One-Time Buyer</b> — program loyalitas dan personalized recommendation sangat diperlukan untuk meningkatkan customer lifetime value.</div>', unsafe_allow_html=True)
