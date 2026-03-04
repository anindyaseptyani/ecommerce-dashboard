import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="E-Commerce Dashboard", layout="wide")
st.title("📊 E-Commerce Business Dashboard")

# =========================
# LOAD DATA
# =========================

@st.cache_data
def load_data():
    orders = pd.read_csv("orders_dataset.csv", sep=';')
    payments = pd.read_csv("order_payments_dataset.csv", sep=';')
    customers = pd.read_csv("customers_dataset.csv", sep=';')  # ✅ FIX

    orders.columns = orders.columns.str.strip()
    payments.columns = payments.columns.str.strip()
    customers.columns = customers.columns.str.strip()

    return orders, payments, customers

orders_df, payments_df, customers_df = load_data()

# =========================
# DATA CLEANING (SAMA SEPERTI NOTEBOOK)
# =========================

orders_df["order_purchase_timestamp"] = pd.to_datetime(
    orders_df["order_purchase_timestamp"],
    format="%d/%m/%Y %H:%M"
)

orders_clean = orders_df[orders_df["order_status"] == "delivered"]

revenue_df = pd.merge(
    orders_clean,
    payments_df,
    on="order_id",
    how="inner"
)

# =========================
# SIDEBAR FILTER
# =========================

st.sidebar.header("🔎 Filter Data")

min_date = revenue_df["order_purchase_timestamp"].min()
max_date = revenue_df["order_purchase_timestamp"].max()

date_range = st.sidebar.date_input(
    "Pilih Rentang Tanggal",
    [min_date, max_date]
)

if len(date_range) == 2:
    start_date, end_date = date_range
    revenue_df = revenue_df[
        (revenue_df["order_purchase_timestamp"] >= pd.to_datetime(start_date)) &
        (revenue_df["order_purchase_timestamp"] <= pd.to_datetime(end_date))
    ]
    orders_clean = orders_clean[
        (orders_clean["order_purchase_timestamp"] >= pd.to_datetime(start_date)) &
        (orders_clean["order_purchase_timestamp"] <= pd.to_datetime(end_date))
    ]

# =========================
# METRICS OVERVIEW
# =========================

total_revenue = revenue_df["payment_value"].sum()
total_orders = revenue_df["order_id"].nunique()

col1, col2 = st.columns(2)
col1.metric("Total Revenue", f"${total_revenue:,.0f}")
col2.metric("Total Orders", total_orders)

st.markdown("---")

# ====================================================
# 📈 PERTANYAAN 1: TREN REVENUE BULANAN
# ====================================================

st.subheader("📈 Tren Revenue Bulanan")

revenue_df["year_month"] = revenue_df["order_purchase_timestamp"].dt.to_period("M")

monthly_revenue = (
    revenue_df
    .groupby("year_month")["payment_value"]
    .sum()
    .reset_index()
)

monthly_revenue["year_month"] = monthly_revenue["year_month"].astype(str)

fig1, ax1 = plt.subplots(figsize=(12,5))
ax1.plot(monthly_revenue["year_month"],
         monthly_revenue["payment_value"])
ax1.set_xticklabels(monthly_revenue["year_month"], rotation=45)
ax1.set_title("Tren Revenue Bulanan")
ax1.set_ylabel("Total Revenue")
st.pyplot(fig1)

st.markdown("---")

# ====================================================
# 👥 PERTANYAAN 2: FREKUENSI PEMBELIAN
# ====================================================

st.subheader("👥 Distribusi Frekuensi Pembelian Pelanggan")

customer_orders = pd.merge(
    orders_clean,
    customers_df,
    on="customer_id",
    how="inner"
)

freq_df = (
    customer_orders
    .groupby("customer_unique_id")["order_id"]
    .count()
    .reset_index(name="total_orders")
)

repeat_customers = len(freq_df[freq_df["total_orders"] > 1])
total_unique = len(freq_df)
percentage_repeat = (repeat_customers / total_unique) * 100 if total_unique > 0 else 0

st.metric("Repeat Buyer Percentage", f"{percentage_repeat:.2f}%")

# ====== DISTRIBUTION PLOT ======
fig2, ax2 = plt.subplots(figsize=(8,4))

sns.kdeplot(
    data=freq_df,
    x="total_orders",
    fill=True,
    ax=ax2
)

ax2.set_title("Distribusi Frekuensi Pembelian")
ax2.set_xlabel("Jumlah Order")
ax2.set_ylabel("Density")

st.pyplot(fig2)







