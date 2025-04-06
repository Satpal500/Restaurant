
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Restaurant Order Dashboard", layout="wide")

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("cleaned_order_data.csv", parse_dates=['Created'])
    df['Grand Total (₹)'] = pd.to_numeric(df['Grand Total (₹)'], errors='coerce')
    df['Delivery Charge (₹)'] = pd.to_numeric(df['Delivery Charge (₹)'], errors='coerce')
    df['Container Charge (₹)'] = pd.to_numeric(df['Container Charge (₹)'], errors='coerce')
    df['Total Tax (₹)'] = pd.to_numeric(df['Total Tax (₹)'], errors='coerce')
    return df.dropna(subset=['Created'])

df = load_data()

# Sidebar
st.sidebar.image("https://img.icons8.com/color/96/restaurant.png", width=80)
st.sidebar.title("Restaurant Orders")
st.sidebar.markdown("Use the filters below to explore the data.")
date_range = st.sidebar.date_input("📅 Date Range", [df['Created'].min(), df['Created'].max()])
df_filtered = df[(df['Created'] >= pd.to_datetime(date_range[0])) & (df['Created'] <= pd.to_datetime(date_range[1]))]

# Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📌 Overview", "📦 Order Insights", "💰 Revenue & Charges", "🏆 Top Performers", "📄 Raw Data"])

with tab1:
    st.markdown("## 📌 Business Overview")
    col1, col2, col3 = st.columns(3)
    col1.metric("🧾 Total Orders", len(df_filtered))
    col2.metric("💳 Avg. Order Value", f"₹{df_filtered['Grand Total (₹)'].mean():.2f}")
    col3.metric("💰 Total Revenue", f"₹{df_filtered['Grand Total (₹)'].sum():,.0f}")

    st.markdown("---")
    st.subheader("📈 Revenue Trend")
    daily_rev = df_filtered.groupby(df_filtered['Created'].dt.date)['Grand Total (₹)'].sum().reset_index()
    fig = px.line(daily_rev, x="Created", y="Grand Total (₹)", title="Daily Revenue", markers=True)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("💳 Payment Method Distribution")
    pay_fig = px.pie(df_filtered, names='Payment Type', title='Payments by Type')
    st.plotly_chart(pay_fig, use_container_width=True)

with tab2:
    st.markdown("## 📦 Order Insights")
    with st.expander("🔍 Filter Options"):
        order_type = st.multiselect("Order Type", df_filtered['Order Type'].dropna().unique(), default=df_filtered['Order Type'].dropna().unique())
        sub_type = st.multiselect("Sub Order Type", df_filtered['Sub Order Type'].dropna().unique(), default=df_filtered['Sub Order Type'].dropna().unique())
        pay_type = st.multiselect("Payment Type", df_filtered['Payment Type'].dropna().unique(), default=df_filtered['Payment Type'].dropna().unique())

    filtered = df_filtered[
        df_filtered['Order Type'].isin(order_type) &
        df_filtered['Sub Order Type'].isin(sub_type) &
        df_filtered['Payment Type'].isin(pay_type)
    ]

    st.dataframe(filtered[['Order No.', 'Client OrderID', 'Order Type', 'Sub Order Type', 'Grand Total (₹)', 'Payment Type', 'Created']])

with tab3:
    st.markdown("## 💰 Revenue & Charges")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📦 Delivery & Container Charges")
        st.metric("Delivery Charges", f"₹{df_filtered['Delivery Charge (₹)'].sum():.2f}")
        st.metric("Container Charges", f"₹{df_filtered['Container Charge (₹)'].sum():.2f}")
    with col2:
        st.subheader("🧾 Taxes")
        st.metric("Total Tax Collected", f"₹{df_filtered['Total Tax (₹)'].sum():.2f}")

    st.markdown("---")
    st.subheader("📊 Revenue Breakdown by Payment Type")
    rev_by_type = df_filtered.groupby("Payment Type")['Grand Total (₹)'].sum().reset_index()
    bar = px.bar(rev_by_type, x="Payment Type", y="Grand Total (₹)", title="Revenue by Payment Type", text_auto=True)
    st.plotly_chart(bar, use_container_width=True)

with tab4:
    st.markdown("## 🏆 Top Performing Days")
    top_days = daily_rev.sort_values(by="Grand Total (₹)", ascending=False).head(10)
    fig_top = px.bar(top_days, x="Created", y="Grand Total (₹)", title="Top 10 Revenue Days", text_auto=True)
    st.plotly_chart(fig_top, use_container_width=True)

with tab5:
    st.markdown("## 📄 Full Dataset")
    st.dataframe(df_filtered)
    csv = df_filtered.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Download CSV", data=csv, file_name="filtered_order_data.csv", mime="text/csv")
