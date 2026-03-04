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
    orders = pd.read_csv("orders_dataset.csv")
    payments = pd.read_csv("order_payments_dataset.csv")
    customers = pd.read_csv("customers_dataset.csv")

    orders.columns = orders.columns.str.strip()
    payments.columns = payments.columns.str.strip()
    customers.columns = customers.columns.str.strip()

    return orders, payments, customers

orders_df, payments_df, customers_df = load_data()

# =========================
# FILTER DELIVERED ONLY
# =========================

orders_clean = orders_df[orders_df["order_status"] == "delivered"]

# =========================
# MERGE FOR REVENUE
# =========================

revenue_df = pd.merge(
    orders_clean,
    payments_df,
    on="order_id",
    how="inner"
)

# =========================
# OVERVIEW METRICS
# =========================

total_revenue = revenue_df["payment_value"].sum()
total_orders = revenue_df["order_id"].nunique()
total_customers = orders_clean["customer_id"].nunique()

col1, col2, col3 = st.columns(3)

col1.metric("Total Revenue", f"${total_revenue:,.0f}")
col2.metric("Total Orders", total_orders)
col3.metric("Total Customers", total_customers)

st.markdown("---")

# =========================
# PAYMENT METHOD ANALYSIS
# =========================

st.subheader("💳 Payment Method Distribution")

payment_counts = revenue_df["payment_type"].value_counts()

fig1, ax1 = plt.subplots()
payment_counts.plot(kind="bar", ax=ax1)
ax1.set_title("Payment Method Usage")
st.pyplot(fig1)

st.markdown("---")

# =========================
# CUSTOMER BEHAVIOR
# =========================

st.subheader("👥 Customer Purchase Frequency")

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

fig2, ax2 = plt.subplots()
sns.histplot(freq_df["total_orders"], bins=10, ax=ax2)
ax2.set_title("Distribution of Purchase Frequency")
st.pyplot(fig2)

st.markdown("---")

# =========================
# CUSTOMER LOCATION
# =========================

st.subheader("🌍 Top 10 Customer Cities")

city_counts = customers_df["customer_city"].value_counts().head(10)

fig3, ax3 = plt.subplots()
city_counts.plot(kind="barh", ax=ax3)
ax3.set_title("Top 10 Cities by Number of Customers")
st.pyplot(fig3)
