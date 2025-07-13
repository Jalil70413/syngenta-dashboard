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
    "orders-May-13-July-11.xlsx",
    sheet_name="Orders"
)

# DEBUG: See your columns if needed
# st.write("Columns in your dataset:", orders_df.columns.tolist())

# -------------------------------------------------
# ADDITIONAL PROCESSING
# -------------------------------------------------
# Convert order date and extract month
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
# KPI CALCULATIONS using 'Order Status'
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
# DISPLAY TITLE & SUBTITLE
# -------------------------------------------------
st.title("📊 Syngenta Ecommerce Orders Analysis")
st.markdown("### 🗓️ May 13 2025 to july 11 2025")


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

# In your Streamlit code
col1, col2, col3, col4 = st.columns(4)
col1.markdown(kpi_card("Total Completed Orders", f"{completed_orders:,}", "#27ae60", "white"), unsafe_allow_html=True)
col2.markdown(kpi_card("Total Processing Orders", f"{processing_orders:,}", "#2980b9", "white"), unsafe_allow_html=True)
col3.markdown(kpi_card("Total Cancelled Orders", f"{cancelled_orders:,}", "#c0392b", "white"), unsafe_allow_html=True)
col4.markdown(kpi_card("Total Refund Orders", f"{refund_orders:,}", "#8e44ad", "white"), unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)
col5, col6, col7, col8 = st.columns(4)
col5.markdown(kpi_card("Completed Orders Value", f"Rs {int(completed_value):,}", "#27ae60", "white"), unsafe_allow_html=True)
col6.markdown(kpi_card("Processing Orders Value", f"Rs {int(processing_value):,}", "#2980b9", "white"), unsafe_allow_html=True)
col7.markdown(kpi_card("Cancelled Orders Value", f"Rs {int(cancelled_value):,}", "#c0392b", "white"), unsafe_allow_html=True)
col8.markdown(kpi_card("Refund Orders Value", f"Rs {int(refund_value):,}", "#8e44ad", "white"), unsafe_allow_html=True)


# -------------------------------------------------
# BAR CHART: ORDERS BY ITEM NAME
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
    title="Count of Order Number by Item Name",
    color='Order Count',
    color_continuous_scale='Blues'
)

# -------------------------------------------------
# BAR CHART: ORDERS BY CITY
# -------------------------------------------------
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
    title="Count of Order Number by City (Billing)",
    color='Order Count',
    color_continuous_scale='Oranges'
)


# -------------------------------------------------
# DISPLAY CHARTS SIDE BY SIDE
# -------------------------------------------------
left_col, right_col = st.columns(2)
left_col.plotly_chart(fig_items, use_container_width=True)
right_col.plotly_chart(fig_cities, use_container_width=True)
