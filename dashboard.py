import streamlit as st
import pandas as pd
import plotly.express as px

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(page_title="Syngenta Orders Analysis", layout="wide")

# -------------------------------------------------
# LOAD DATA
# -------------------------------------------------
orders_df = pd.read_excel(
    "orders.xlsx",
    sheet_name="Orders"
)

# st.write("Columns:", orders_df.columns.tolist())

# -------------------------------------------------
# PROCESSING
# -------------------------------------------------
orders_df['Order Date'] = pd.to_datetime(orders_df['Order Date'])
orders_df['Month'] = orders_df['Order Date'].dt.strftime('%B %Y')

# -------------------------------------------------
# MONTH FILTER
# -------------------------------------------------
months = orders_df['Month'].unique()
selected_month = st.selectbox("📅 Select Month", ["All"] + sorted(months))

if selected_month != "All":
    filtered_df = orders_df[orders_df['Month'] == selected_month]
else:
    filtered_df = orders_df

# -------------------------------------------------
# KPIS
# -------------------------------------------------
completed_orders = filtered_df[filtered_df['Order Status'] == 'Completed']['Order Number'].nunique()
processing_orders = filtered_df[filtered_df['Order Status'] == 'Processing']['Order Number'].nunique()
cancelled_orders = filtered_df[filtered_df['Order Status'] == 'Cancelled']['Order Number'].nunique()
refund_orders = filtered_df[filtered_df['Order Status'] == 'Refunded']['Order Number'].nunique()

completed_value = filtered_df[filtered_df['Order Status'] == 'Completed']['Order Subtotal Amount'].sum()
processing_value = filtered_df[filtered_df['Order Status'] == 'Processing']['Order Subtotal Amount'].sum()
cancelled_value = filtered_df[filtered_df['Order Status'] == 'Cancelled']['Order Subtotal Amount'].sum()
refund_value = filtered_df[filtered_df['Order Status'] == 'Refunded']['Order Subtotal Amount'].sum()

# -------------------------------------------------
# DISPLAY TITLE & DATE RANGE
# -------------------------------------------------
st.title("📊 Syngenta Ecommerce Orders Analysis")
# Automatically calculate min & max order dates
min_date = filtered_df['Order Date'].min().strftime("%b %d, %Y")
max_date = filtered_df['Order Date'].max().strftime("%b %d, %Y")

st.markdown(f"### 🗓️ {min_date} to {max_date}")


# -------------------------------------------------
# KPI CARDS
# -------------------------------------------------
def kpi_card(title, value, bgcolor, textcolor):
    return f"""
    <div style="
        background-color: {bgcolor};
        color: {textcolor};
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    ">
        <div style="font-size: 18px; font-weight: 500;">{title}</div>
        <div style="font-size: 28px; font-weight: 700;">{value}</div>
    </div>
    """

col1, col2, col3, col4 = st.columns(4)
col1.markdown(kpi_card("✅ Completed Orders", f"{completed_orders:,}", "#27ae60", "white"), unsafe_allow_html=True)
col2.markdown(kpi_card("🛠️ Processing Orders", f"{processing_orders:,}", "#2980b9", "white"), unsafe_allow_html=True)
col3.markdown(kpi_card("❌ Cancelled Orders", f"{cancelled_orders:,}", "#c0392b", "white"), unsafe_allow_html=True)
col4.markdown(kpi_card("🔄 Refund Orders", f"{refund_orders:,}", "#8e44ad", "white"), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
col5, col6, col7, col8 = st.columns(4)
col5.markdown(kpi_card("💰 Completed Value", f"Rs {int(completed_value):,}", "#27ae60", "white"), unsafe_allow_html=True)
col6.markdown(kpi_card("💸 Processing Value", f"Rs {int(processing_value):,}", "#2980b9", "white"), unsafe_allow_html=True)
col7.markdown(kpi_card("🚫 Cancelled Value", f"Rs {int(cancelled_value):,}", "#c0392b", "white"), unsafe_allow_html=True)
col8.markdown(kpi_card("🔄 Refund Value", f"Rs {int(refund_value):,}", "#8e44ad", "white"), unsafe_allow_html=True)

# -------------------------------------------------
# DAILY SALES TREND
# -------------------------------------------------
sales_trend = (
    filtered_df.groupby(filtered_df['Order Date'].dt.to_period("D"))['Order Subtotal Amount']
    .sum()
    .reset_index()
)
sales_trend['Order Date'] = sales_trend['Order Date'].dt.to_timestamp()

fig_trend = px.line(
    sales_trend,
    x='Order Date',
    y='Order Subtotal Amount',
    markers=True,
    title="📈 Daily Sales Value Trend",
    template='plotly_white'
)
st.plotly_chart(fig_trend, use_container_width=True)

# # -------------------------------------------------
# # TOP CUSTOMERS
# # -------------------------------------------------
# top_customers = (
#     filtered_df.groupby('Email (Billing)')['Order Subtotal Amount']
#     .sum()
#     .reset_index()
#     .rename(columns={'Email (Billing)': 'Customer Email', 'Order Subtotal Amount': 'Total Spend'})
#     .sort_values('Total Spend', ascending=False)
#     .head(10)
# )

# st.subheader("🏆 Top 10 Customers by Total Spend")
# styled_top_customers = top_customers.style.format({"Total Spend": "Rs {:,}"})
# st.dataframe(styled_top_customers)



# -------------------------------------------------
# AVG ITEMS PER ORDER
# -------------------------------------------------
avg_items = (
    filtered_df.groupby('Order Number')['Item Name']
    .nunique()
    .mean()
)
st.metric("🛒 Average Items per Order", f"{avg_items:.2f}")

# -------------------------------------------------
# ORDERS BY ITEM & BY CITY
# -------------------------------------------------
item_summary = (
    filtered_df.groupby('Item Name')['Order Number']
    .nunique()
    .reset_index(name='Order Count')
    .sort_values('Order Count', ascending=True)
)

fig_items = px.bar(
    item_summary,
    x='Order Count',
    y='Item Name',
    orientation='h',
    title="📦 Orders by Item Name",
    color='Order Count',
    color_continuous_scale='Blues',
    template='plotly_white'
)

city_summary = (
    filtered_df.groupby('City (Billing)')['Order Number']
    .nunique()
    .reset_index(name='Order Count')
    .sort_values('Order Count', ascending=True)
)

fig_cities = px.bar(
    city_summary,
    x='Order Count',
    y='City (Billing)',
    orientation='h',
    title="🏙️ Orders by City (Billing)",
    color='Order Count',
    color_continuous_scale='Oranges',
    template='plotly_white'
)

left_col, right_col = st.columns(2)
left_col.plotly_chart(fig_items, use_container_width=True)
right_col.plotly_chart(fig_cities, use_container_width=True)


# -------------------------------------------------
# ITEMS BY TOTAL VALUE
# -------------------------------------------------
item_value = (
    filtered_df.groupby('Item Name')['Order Subtotal Amount']
    .sum()
    .reset_index()
    .rename(columns={'Order Subtotal Amount': 'Total Sales'})
    .sort_values('Total Sales', ascending=True)
)

fig_item_value = px.bar(
    item_value,
    x='Total Sales',
    y='Item Name',
    orientation='h',
    title="Total Sales Value by Item Name",
    color='Total Sales',
    color_continuous_scale='Greens'
)

# -------------------------------------------------
# CITIES BY TOTAL VALUE
# -------------------------------------------------
city_value = (
    filtered_df.groupby('City (Billing)')['Order Subtotal Amount']
    .sum()
    .reset_index()
    .rename(columns={'Order Subtotal Amount': 'Total Sales'})
    .sort_values('Total Sales', ascending=True)
)

fig_city_value = px.bar(
    city_value,
    x='Total Sales',
    y='City (Billing)',
    orientation='h',
    title="Total Sales Value by City (Billing)",
    color='Total Sales',
    color_continuous_scale='Purples'
)

# -------------------------------------------------
# DISPLAY ADDITIONAL CHARTS SIDE BY SIDE
# -------------------------------------------------
col_a, col_b = st.columns(2)
col_a.plotly_chart(fig_item_value, use_container_width=True)
col_b.plotly_chart(fig_city_value, use_container_width=True)
