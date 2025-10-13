import streamlit as st
import pandas as pd
import plotly.express as px
# --- Page Config ---
st.set_page_config(page_title="Recovery Dashboard", layout="wide")

# --- Custom CSS for card styling and background ---
st.markdown(
    """
    <style>
    /* General styles */
    body, .stApp, .main, [data-testid="stSidebar"], [data-testid="stHeader"] {
        background-color: #f8fafc !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    /* Card Container */
    div.element-container div[data-testid="stHorizontalBlock"] > div {
        position: relative;
        padding-top: 2.5rem !important;
    }
    
    /* Card styling */
    .stMetric {
        background: white !important;
        border-radius: 16px !important;
        padding: 1.5rem !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05) !important;
        margin-bottom: 1rem !important;
    }
    
    /* Card Header with Icon */
    .metric-container {
        position: relative;
        margin-bottom: -2.5rem;
        z-index: 1;
    }
    
    .metric-icon {
        width: 48px;
        height: 48px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 24px;
        position: absolute;
        right: 1rem;
        top: 0;
    }
    
    /* Metric Styles */
    .stMetric label {
        font-size: 1rem !important;
        color: #64748b !important;
        font-weight: 500 !important;
        text-transform: none !important;
    }
    
    .stMetric [data-testid="stMetricValue"] {
        font-size: 2rem !important;
        color: #111827 !important;
        font-weight: 600 !important;
    }
    
    .stMetric [data-testid="stMetricDelta"] {
        background-color: #ecfdf5 !important;
        color: #047857 !important;
        padding: 4px 8px !important;
        border-radius: 6px !important;
        font-size: 0.875rem !important;
        margin-top: 0.5rem !important;
        display: inline-block !important;
    }
    
    /* Icons colors */
    .icon-money {
        background-color: #e6faf3;
        color: #10b981;
    }
    
    .icon-warning {
        background-color: #ffe6f0;
        color: #f43f5e;
    }
    
    .icon-doc {
        background-color: #e6faf3;
        color: #10b981;
    }
    
    .icon-chart {
        background-color: #fff7e6;
        color: #f59e42;
    }
    
    /* Other elements */
    .stDataFrame, .stPlotlyChart {
        background: white !important;
        border-radius: 16px !important;
        padding: 1rem !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05) !important;
    }
    
    .stSidebarContent {
        background: white !important;
    }
    
    h1, h2, h3, p {
        color: #111827 !important;
    }
    
    .css-10trblm {
        color: #111827 !important;
        font-weight: 600 !important;
    }
    
    div[data-testid="stMarkdownContainer"] > p {
        color: #6b7280 !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- Sidebar ---
st.sidebar.title("Pourri Intelligence")
st.sidebar.caption("Deduction Recovery")
st.sidebar.markdown("---")
nav = st.sidebar.radio("Navigation", ["Dashboard", "Upload & Map", "Reconciliations", "Settings"])
st.sidebar.markdown("---")
st.sidebar.write("**Pourri Team**  \nRecovery Intelligence")
# --- Dashboard Header ---
st.subheader("Recovery Dashboard")
st.caption("Turn complex data into calm confidence")
# --- KPI Cards ---
col1, col2, col3, col4 = st.columns(4)

# Total Deductions Card
with col1:
    st.markdown('<div class="metric-container"><div class="metric-icon icon-money">💲</div></div>', unsafe_allow_html=True)
    st.metric(
        "Total Deductions",
        "$156K",
        "+8.2% vs prior period",
        help="Last 90 days"
    )

# Recoverable Amount Card
with col2:
    st.markdown('<div class="metric-container"><div class="metric-icon icon-warning">⚠️</div></div>', unsafe_allow_html=True)
    st.metric(
        "Recoverable Amount",
        "$15K",
        "12.5% of total",
        help="Disputable deductions"
    )

# Active Disputes Card
with col3:
    st.markdown('<div class="metric-container"><div class="metric-icon icon-doc">📄</div></div>', unsafe_allow_html=True)
    st.metric(
        "Active Disputes",
        "0",
        "In progress"
    )

# Recovery Rate Card
with col4:
    st.markdown('<div class="metric-container"><div class="metric-icon icon-chart">📈</div></div>', unsafe_allow_html=True)
    st.metric(
        "Recovery Rate",
        "87.3%",
        "vs 82% target",
        help="Historical success"
    )
st.divider()
# --- Sample data for charts ---
months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
confirmed = [140000, 150000, 155000, 160000, 170000, 165000]
under_applied = [120000, 130000, 140000, 150000, 155000, 160000]
disputable = [110000, 120000, 125000, 130000, 135000, 132000]
df_trends = pd.DataFrame({
   "Month": months,
   "Confirmed Valid": confirmed,
   "Under-Applied": under_applied,
   "Disputable": disputable
})
df_variance = pd.DataFrame({
   "Classification": ["Disputable", "Confirmed Valid", "Under-Applied", "Pending Review"],
   "Amount": [15000, 45000, 2000, 30000]
})
# --- Charts Section ---
left, right = st.columns([2, 1])
with left:
   st.subheader("Monthly Deduction Trends")
   fig = px.line(
       df_trends,
       x="Month",
       y=["Confirmed Valid", "Under-Applied", "Disputable"],
       markers=True,
       template="simple_white",
   )
   fig.update_yaxes(title="Amount ($)")
   fig.update_xaxes(title="")
   st.plotly_chart(fig, use_container_width=True)
with right:
   st.subheader("Variance by Classification")
   bar = px.bar(
       df_variance,
       x="Classification",
       y="Amount",
       text="Amount",
       template="simple_white",
   )
   bar.update_yaxes(title="Amount ($)")
   st.plotly_chart(bar, use_container_width=True)
st.divider()
# --- Reconciliations Table ---
st.subheader("Recent Reconciliations")
data = [
   ["AMZ-DED-2024-001", "Jan 15, 2024", "$18,500", "$14,200", "$4,300", "Disputable"],
   ["AMZ-DED-2024-002", "Jan 18, 2024", "$12,600", "$12,800", "$200", "Under-Applied"],
   ["AMZ-DED-2024-003", "Jan 22, 2024", "$25,400", "$19,100", "$6,300", "Disputable"],
   ["AMZ-DED-2024-004", "Jan 25, 2024", "$15,800", "$15,800", "$0", "Confirmed Valid"],
   ["AMZ-DED-2024-005", "Feb 1, 2024", "$21,200", "$16,500", "$4,700", "Disputable"],
   ["AMZ-DED-2024-006", "Feb 5, 2024", "$8,900", "$8,900", "$0", "Confirmed Valid"],
   ["AMZ-DED-2024-007", "Feb 8, 2024", "$34,500", "$28,200", "$6,300", "Pending Review"],
   ["AMZ-DED-2024-008", "Feb 12, 2024", "$19,300", "$19,300", "$0", "Confirmed Valid"],
]
df_table = pd.DataFrame(
   data,
   columns=["Memo ID", "Date", "Actual", "Expected", "Variance", "Classification"],
)
# Use Streamlit built-in DataFrame renderer for stability
st.dataframe(df_table, use_container_width=True)
# --- Footer ---
st.markdown("---")
st.caption("© Pourri Intelligence • Recovery Dashboard Prototype")