import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="E-Commerce Dashboard",
    page_icon="🛒",
    layout="wide"
)


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
# SIDEBAR - Filter Waktu
# ─────────────────────────────────────────────
st.sidebar.title("🛒 E-Commerce Dashboard")
st.sidebar.markdown("---")
st.sidebar.markdown("### 📅 Filter Rentang Waktu")
 
min_date = master_df['order_purchase_timestamp'].min().date()
max_date = master_df['order_purchase_timestamp'].max().date()
 
start_date = st.sidebar.date_input(
    "Tanggal Mulai",
    value=pd.Timestamp('2017-01-01').date(),
    min_value=min_date,
    max_value=max_date
)
end_date = st.sidebar.date_input(
    "Tanggal Akhir",
    value=max_date,
    min_value=min_date,
    max_value=max_date
)
 
st.sidebar.markdown("---")
st.sidebar.caption("Sumber Data: E-Commerce Public Dataset (Olist) 2017–2018")
 
# Filter data berdasarkan tanggal
mask = (
    (master_df['order_purchase_timestamp'].dt.date >= start_date) &
    (master_df['order_purchase_timestamp'].dt.date <= end_date)
)
df = master_df[mask].copy()
 

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.title("🛒 E-Commerce Public Dataset Dashboard")
st.caption("Analisis performa penjualan e-commerce Brasil periode Januari 2017 – Agustus 2018")
st.markdown("---")
 
# ─────────────────────────────────────────────
# KPI METRICS
# ─────────────────────────────────────────────
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("📦 Total Pesanan", f"{df['order_id'].nunique():,}")
with col2:
    st.metric("💰 Total Pendapatan", f"R$ {df['payment_value'].sum():,.0f}")
with col3:
    st.metric("👤 Pelanggan Unik", f"{df['customer_unique_id'].nunique():,}")
 
st.markdown("---")

# ═══════════════════════════════════════════════
# PERTANYAAN 1: Tren Penjualan Bulanan
# ═══════════════════════════════════════════════
st.subheader("📈 Pertanyaan 1: Bagaimana tren jumlah pesanan dan total pendapatan bulanan pada periode Januari 2017 – Agustus 2018?")
 
monthly = (
    df.groupby('order_year_month')
    .agg(
        total_order=('order_id', 'nunique'),
        total_pendapatan=('payment_value', 'sum')
    )
    .reset_index()
    .sort_values('order_year_month')
)
 
# Batasi ke rentang waktu pertanyaan
monthly = monthly[
    (monthly['order_year_month'] >= '2017-01') &
    (monthly['order_year_month'] <= '2018-08')
]
 
fig, ax = plt.subplots(figsize=(12, 5))
 
ax.bar(
    monthly['order_year_month'],
    monthly['total_order'],
    color='steelblue',
    alpha=0.8,
    label='Jumlah Pesanan'
)
ax.set_ylabel('Jumlah Pesanan', color='steelblue')
ax.tick_params(axis='y', labelcolor='steelblue')
ax.set_xticks(range(len(monthly)))
ax.set_xticklabels(monthly['order_year_month'], rotation=45, ha='right', fontsize=8)
 
ax2 = ax.twinx()
ax2.plot(
    range(len(monthly)),
    monthly['total_pendapatan'],
    color='darkorange',
    marker='o',
    linewidth=2,
    label='Total Pendapatan (R$)'
)
ax2.set_ylabel('Total Pendapatan (R$)', color='darkorange')
ax2.tick_params(axis='y', labelcolor='darkorange')
ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f'R${v/1e6:.1f}M'))
 
ax.set_title(
    'Tren Jumlah Pesanan dan Total Pendapatan per Bulan\n(Januari 2017 – Agustus 2018)',
    fontsize=13, fontweight='bold'
)
 
lines1, labels1 = ax.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
 
plt.tight_layout()
st.pyplot(fig)
plt.close()
 
st.info("💡 **Kesimpulan:** Tren menunjukkan pertumbuhan konsisten sepanjang 2017–2018. Lonjakan tertinggi terjadi pada November 2017. Strategi promosi Q4 sangat direkomendasikan untuk memaksimalkan pendapatan tahunan.")
 
st.markdown("---")
 

# ═══════════════════════════════════════════════
# PERTANYAAN 2: Kategori Produk Terlaris
# ═══════════════════════════════════════════════
st.subheader("🏷️ Pertanyaan 2: Kategori produk apa yang menghasilkan volume penjualan dan pendapatan tertinggi selama 2017–2018?")
 
n_top = st.slider("Tampilkan Top N Kategori:", min_value=5, max_value=15, value=10)
 
cat_data = (
    df.groupby('product_category_name')
    .agg(
        total_item=('order_id', 'count'),
        total_pendapatan=('price', 'sum')
    )
    .reset_index()
)
 
col_a, col_b = st.columns(2)
 
with col_a:
    top_qty = cat_data.sort_values('total_item', ascending=False).head(n_top).sort_values('total_item')
    fig, ax = plt.subplots(figsize=(7, n_top * 0.45 + 1))
    ax.barh(
        top_qty['product_category_name'],
        top_qty['total_item'],
        color=sns.color_palette('Blues_d', n_top)
    )
    ax.set_title(f'Top {n_top} Kategori berdasarkan Volume Penjualan', fontsize=11, fontweight='bold')
    ax.set_xlabel('Jumlah Item Terjual')
    for i, val in enumerate(top_qty['total_item']):
        ax.text(val + 10, i, f'{val:,}', va='center', fontsize=8)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()
 
with col_b:
    top_rev = cat_data.sort_values('total_pendapatan', ascending=False).head(n_top).sort_values('total_pendapatan')
    fig, ax = plt.subplots(figsize=(7, n_top * 0.45 + 1))
    ax.barh(
        top_rev['product_category_name'],
        top_rev['total_pendapatan'],
        color=sns.color_palette('Oranges_d', n_top)
    )
    ax.set_title(f'Top {n_top} Kategori berdasarkan Pendapatan', fontsize=11, fontweight='bold')
    ax.set_xlabel('Total Pendapatan (R$)')
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f'R${v/1e6:.1f}M'))
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()
 
st.info("💡 **Kesimpulan:** Kategori *bed_bath_table* memimpin dari sisi volume. Dari sisi pendapatan, *health_beauty* dan *watches_gifts* unggul karena harga rata-rata per transaksi yang lebih tinggi.")
 
st.markdown("---")

# ═══════════════════════════════════════════════
# PERTANYAAN 3: Distribusi Geografis
# ═══════════════════════════════════════════════
st.subheader("🗺️ Pertanyaan 3: Negara bagian mana yang menyumbang pendapatan terbesar selama 2017–2018?")
 
rev_state = (
    df.groupby('customer_state')
    .agg(total_pendapatan=('payment_value', 'sum'))
    .reset_index()
    .sort_values('total_pendapatan', ascending=False)
)
 
fig, ax = plt.subplots(figsize=(12, 5))
ax.bar(
    rev_state['customer_state'],
    rev_state['total_pendapatan'],
    color=sns.color_palette('viridis', len(rev_state))
)
ax.set_title('Total Pendapatan per Negara Bagian (2017–2018)', fontsize=13, fontweight='bold')
ax.set_xlabel('Negara Bagian')
ax.set_ylabel('Total Pendapatan (R$)')
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f'R${v/1e6:.1f}M'))
plt.xticks(rotation=45)
plt.tight_layout()
st.pyplot(fig)
plt.close()
 
# Hitung kontribusi SP
total_rev = rev_state['total_pendapatan'].sum()
sp_rev = rev_state[rev_state['customer_state'] == 'SP']['total_pendapatan'].values
sp_pct = (sp_rev[0] / total_rev * 100) if len(sp_rev) > 0 else 0
 
st.info(f"💡 **Kesimpulan:** São Paulo (SP) menyumbang sekitar **{sp_pct:.1f}%** dari total pendapatan nasional — jauh melampaui negara bagian lainnya. Wilayah utara Brasil merupakan peluang ekspansi yang belum dioptimalkan.")
 
st.markdown("---")

# ═══════════════════════════════════════════════
# PERTANYAAN 4: Segmentasi Pelanggan (RFM)
# ═══════════════════════════════════════════════
st.subheader("👥 Pertanyaan 4: Berapa persentase pelanggan Champions dan Loyal Customers berdasarkan RFM Analysis 2017–2018?")
 
reference_date = df['order_purchase_timestamp'].max() + pd.Timedelta(days=1)
 
rfm_df = (
    df.groupby('customer_unique_id')
    .agg(
        Recency=('order_purchase_timestamp', lambda x: (reference_date - x.max()).days),
        Frequency=('order_id', 'nunique'),
        Monetary=('payment_value', 'sum')
    )
    .reset_index()
)
 
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
color_map = {
    'Champions': '#2ecc71',
    'Loyal Customers': '#3498db',
    'Potential Loyalist': '#f39c12',
    'At Risk': '#e74c3c',
    'Lost Customers': '#95a5a6'
}
 
seg_counts = rfm_df['Segment'].value_counts().reindex(segment_order).dropna()
seg_pct = (seg_counts / seg_counts.sum() * 100).round(1)
 
col_c, col_d = st.columns(2)
 
with col_c:
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.pie(
        seg_counts.values,
        labels=seg_counts.index,
        autopct='%1.1f%%',
        colors=[color_map[s] for s in seg_counts.index],
        startangle=90
    )
    ax.set_title('Distribusi Segmen Pelanggan (RFM)', fontsize=12, fontweight='bold')
    st.pyplot(fig)
    plt.close()
 
with col_d:
    fig, ax = plt.subplots(figsize=(6, 5))
    bars = ax.bar(
        seg_counts.index,
        seg_counts.values,
        color=[color_map[s] for s in seg_counts.index],
        alpha=0.85
    )
    ax.set_title('Jumlah Pelanggan per Segmen', fontsize=12, fontweight='bold')
    ax.set_ylabel('Jumlah Pelanggan')
    plt.xticks(rotation=20, ha='right')
    for bar, val in zip(bars, seg_counts.values):
        ax.text(bar.get_x() + bar.get_width() / 2, val + 50, f'{val:,}', ha='center', fontsize=9)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()
 
champ_pct = seg_pct.get('Champions', 0)
loyal_pct = seg_pct.get('Loyal Customers', 0)
st.info(f"💡 **Kesimpulan:** Segmen *Champions* sebesar **{champ_pct}%** dan *Loyal Customers* sebesar **{loyal_pct}%** dari total pelanggan. Strategi yang direkomendasikan: email remarketing, diskon loyalitas, dan program referral untuk mendorong lebih banyak pelanggan naik ke segmen *Champions*.")
