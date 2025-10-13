import streamlit as st
import pandas as pd
import plotly.express as px
# ----------------- Page Config -----------------
st.set_page_config(page_title="Recovery Dashboard", layout="wide")
# ----------------- Custom CSS -----------------
st.markdown("""
<style>
/* Modal Styles */
.modal-backdrop {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.5);
    z-index: 1000;
}

.deduction-modal {
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    background: white;
    padding: 24px;
    border-radius: 12px;
    width: 90%;
    max-width: 800px;
    max-height: 90vh;
    overflow-y: auto;
    z-index: 1001;
    box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
}

.status-badge {
    display: inline-flex;
    padding: 6px 12px;
    border-radius: 9999px;
    font-size: 14px;
    font-weight: 500;
    margin-bottom: 24px;
}

.status-disputable {
    background: #FEF2F2;
    color: #DC2626;
}

.status-under-applied {
    background: #ECFEFF;
    color: #0891B2;
}

.status-confirmed-valid {
    background: #F0FDF4;
    color: #16A34A;
}

.status-pending-review {
    background: #FFF7ED;
    color: #EA580C;
}

.detail-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 16px;
    margin-bottom: 24px;
}

.detail-item {
    background: #F8FAFC;
    padding: 12px;
    border-radius: 8px;
}

.detail-label {
    font-size: 12px;
    color: #64748B;
    margin-bottom: 4px;
}

.detail-value {
    font-size: 16px;
    font-weight: 500;
    color: #0F172A;
}

.analysis-section h4 {
    color: #0F172A;
    font-size: 16px;
    margin-bottom: 12px;
}
    z-index: 1000;
}
.modal-backdrop {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0,0,0,0.5);
    z-index: 999;
}
.status-badge {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 14px;
    font-weight: 500;
    margin-bottom: 16px;
}
.status-disputable {
    background-color: #FFE4E4;
    color: #DC2626;
}
.status-confirmed {
    background-color: #ECFDF5;
    color: #059669;
}
.status-under-applied {
    background-color: #FEF3C7;
    color: #92400E;
}
.status-pending {
    background-color: #EFF6FF;
    color: #2563EB;
}
.detail-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
    margin-bottom: 24px;
}
.detail-item {
    background: #F8FAFC;
    padding: 12px;
    border-radius: 8px;
}
.detail-label {
    color: #64748B;
    font-size: 12px;
    margin-bottom: 4px;
}
.detail-value {
    color: #0F172A;
    font-weight: 600;
}
.analysis-section {
    margin-top: 24px;
    padding-top: 24px;
    border-top: 1px solid #E2E8F0;
}

/* Clickable table rows */
[data-testid="stDataFrame"] table {
    cursor: pointer;
}
[data-testid="stDataFrame"] tbody tr:hover {
    background-color: #F8FAFC !important;
}

/* GLOBAL APP STYLING */
body, .stApp {
   background-color: #f9fafb !important;
   font-family: 'Inter', sans-serif !important;
   color: #1e293b !important;
}
h1, h2, h3, h4, h5 {
   color: #0f172a !important;
   font-weight: 600 !important;
}
.st-emotion-cache-16txtl3, .st-emotion-cache-10trblm {
   color: #1e293b !important;
}
.stSidebar {
   background-color: #ffffff !important;
}
/* SIDEBAR */
section[data-testid="stSidebar"] {
   background-color: #ffffff !important;
   border-right: 1px solid #e2e8f0;
}
[data-testid="stSidebarNav"] a {
   color: #334155 !important;
}
[data-testid="stSidebarNav"] a:hover {
   color: #2563eb !important;
}
/* KPI CARDS */
.metric-card {
   background-color: #ffffff;
   border-radius: 16px;
   padding: 1.5rem;
   box-shadow: 0 4px 6px rgba(0,0,0,0.05);
   position: relative;
   transition: all 0.2s ease-in-out;
}
.metric-card:hover {
   box-shadow: 0 6px 12px rgba(0,0,0,0.08);
   transform: translateY(-2px);
}
.metric-icon {
   width: 48px;
   height: 48px;
   border-radius: 12px;
   display: flex;
   align-items: center;
   justify-content: center;
   font-size: 22px;
   position: absolute;
   right: 1rem;
   top: 1rem;
   color: white;
}
.icon-green { background-color: #10b981; }
.icon-yellow { background-color: #f59e0b; }
.icon-red { background-color: #ef4444; }
.icon-blue { background-color: #3b82f6; }
.metric-label {
   font-size: 1rem;
   color: #64748b;
   margin-bottom: 0.5rem;
}
.metric-value {
   font-size: 2rem;
   font-weight: 700;
   color: #1e293b;
}
.metric-subtext {
   font-size: 0.9rem;
   color: #059669;
   font-weight: 500;
}
/* CHART CONTAINERS */
.chart-container {
   background-color: #ffffff;
   border-radius: 16px;
   padding: 1rem;
   box-shadow: 0 2px 6px rgba(0,0,0,0.05);
   margin-bottom: 2rem;
}
</style>
""", unsafe_allow_html=True)
# ----------------- Sidebar -----------------
st.sidebar.title("Pourri Intelligence")
st.sidebar.caption("Deduction Recovery")
st.sidebar.markdown("---")
nav = st.sidebar.radio("Navigation", ["Dashboard", "Upload & Map", "Reconciliations", "Settings"])
st.sidebar.markdown("---")
st.sidebar.write("**Pourri Team**  \nRecovery Intelligence")

# Additional CSS for Upload page
if nav == "Upload & Map":
    st.markdown("""
    <style>
    /* UPLOAD SECTION STYLING */
    .upload-section {
        background-color: #ffffff;
        border-radius: 16px;
        padding: 2rem;
        margin-bottom: 1rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        border: 1px dashed #e2e8f0;
    }
    .section-number {
        background-color: #f8fafc;
        color: #64748b;
        width: 32px;
        height: 32px;
        border-radius: 50%;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-weight: 600;
        margin-bottom: 1rem;
    }
    .upload-title {
        color: #0f172a;
        font-size: 1.25rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    .upload-description {
        color: #64748b;
        font-size: 0.875rem;
        margin-bottom: 1.5rem;
    }
    .journey-header {
        display: flex;
        align-items: center;
        gap: 1rem;
        margin-bottom: 2rem;
    }
    .journey-icon {
        background-color: #ecfdf5;
        border-radius: 12px;
        padding: 0.75rem;
        color: #10b981;
        font-size: 1.5rem;
    }
    /* File uploader styling */
    .stFileUploader > div {
        padding: 1rem !important;
        border: 2px dashed #e2e8f0 !important;
    }
    .stFileUploader > div:hover {
        border-color: #10b981 !important;
    }
    .css-1q8dd3e {
        color: #10b981 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# ----------------- Page Content Based on Navigation -----------------
if nav == "Dashboard":
    # ----------------- Header -----------------
    st.title("Recovery Dashboard")
    st.caption("Turn complex data into calm confidence")
    # ----------------- KPI Cards -----------------
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("""
    <div class="metric-card">
    <div class="metric-icon icon-green">💲</div>
    <div class="metric-label">Total Deductions</div>
    <div class="metric-value">$156K</div>
    <div class="metric-subtext">+8.2% vs prior period</div>
    </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
    <div class="metric-card">
    <div class="metric-icon icon-red">⚠️</div>
    <div class="metric-label">Recoverable Amount</div>
    <div class="metric-value">$15K</div>
    <div class="metric-subtext">12.5% of total</div>
    </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
    <div class="metric-card">
    <div class="metric-icon icon-blue">📄</div>
    <div class="metric-label">Active Disputes</div>
    <div class="metric-value">0</div>
    <div class="metric-subtext">In progress</div>
    </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown("""
    <div class="metric-card">
    <div class="metric-icon icon-yellow">📈</div>
    <div class="metric-label">Recovery Rate</div>
    <div class="metric-value">87.3%</div>
    <div class="metric-subtext">vs 82% target</div>
    </div>
        """, unsafe_allow_html=True)
# ----------------- Charts -----------------
    st.markdown("<div style='height: 2rem'></div>", unsafe_allow_html=True)
    chart_col1, chart_col2 = st.columns([2, 1])

    with chart_col1:
        st.markdown("### Monthly Deduction Trends")
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
        fig = px.line(df_trends, x="Month", y=["Confirmed Valid", "Under-Applied", "Disputable"],
                    markers=True, template="plotly_white")
        fig.update_traces(line=dict(width=3))
        fig.update_layout(
            height=350,  # Set fixed height
            plot_bgcolor="white",
            paper_bgcolor="white",
            legend=dict(orientation="h", y=-0.2, x=0.15),
            yaxis_title="Amount ($)",
            margin=dict(l=20, r=20, t=20, b=60)
        )
        st.plotly_chart(fig, use_container_width=True)

    with chart_col2:
        st.markdown("### Variance by Classification")
        df_variance = pd.DataFrame({
            "Classification": ["Disputable", "Confirmed Valid", "Under-Applied", "Pending Review"],
            "Amount": [15000, 45000, 2000, 30000]
        })
        bar = px.bar(df_variance, x="Classification", y="Amount", text="Amount", template="plotly_white",
                    color="Classification", color_discrete_sequence=px.colors.qualitative.Set2)
        bar.update_layout(
            height=350,  # Set fixed height
            plot_bgcolor="white",
            paper_bgcolor="white",
            yaxis_title="Amount ($)",
            showlegend=False,
            margin=dict(l=20, r=20, t=20, b=60),
            xaxis_tickangle=-45  # Angle the x-axis labels for better readability
        )
        st.plotly_chart(bar, use_container_width=True)
        # ----------------- Table -----------------
    st.markdown("### Recent Reconciliations")
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
    df_table = pd.DataFrame(data, columns=["Memo ID", "Date", "Actual", "Expected", "Variance", "Classification"])
    
    # Add table header
    header_cols = st.columns([2, 2, 1.5, 1.5, 1.5, 1.5])
    headers = ["Memo ID", "Date", "Actual", "Expected", "Variance", "Classification"]
    for col, header in zip(header_cols, headers):
        col.markdown(f"**{header}**")
    st.markdown("---")
    
    # Initialize session state
    if "selected_row" not in st.session_state:
        st.session_state["selected_row"] = None
        
    # Create interactive rows
    for index, row in df_table.iterrows():
        cols = st.columns([2, 2, 1.5, 1.5, 1.5, 1.5])
        # Create a clickable button that looks like text
        if cols[0].button(row["Memo ID"], key=f"row_{index}", use_container_width=True):
            st.session_state["selected_row"] = index
        cols[1].write(row["Date"])
        cols[2].write(row["Actual"])
        cols[3].write(row["Expected"])
        cols[4].write(row["Variance"])
        cols[5].write(row["Classification"])
        st.markdown("---")

    # Show details modal when a row is clicked
    if st.session_state["selected_row"] is not None:
        row = df_table.iloc[st.session_state["selected_row"]]
        
        # Create modal-like container
        with st.container():
            # Header with status
            status_color = {
                "Disputable": "#DC2626",
                "Under-Applied": "#0891B2",
                "Confirmed Valid": "#16A34A",
                "Pending Review": "#EA580C"
            }
            
            st.markdown(f"""
                <div style='background: {status_color.get(row['Classification'], '#64748B')}1A; 
                    color: {status_color.get(row['Classification'], '#64748B')};
                    padding: 8px 16px; 
                    border-radius: 9999px; 
                    display: inline-block;
                    font-weight: 500;
                    margin-bottom: 24px;'>
                    {row['Classification']} • Over-deducted by {row['Variance']}
                </div>
            """, unsafe_allow_html=True)
            
            # Basic Information
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.caption("Memo ID")
                st.code(row['Memo ID'])
            with col2:
                st.caption("Deduction Date")
                st.code(row['Date'])
            with col3:
                st.caption("PO Number")
                st.code(f"PO-{row['Memo ID'].split('-')[-1]}")
            with col4:
                st.caption("Invoice")
                st.code(f"INV-2024-{row['Memo ID'].split('-')[-1]}")
            
            # Financial Analysis Section
            st.markdown("### Financial Analysis")
            cols = st.columns(3)
            with cols[0]:
                st.caption("Expected Deduction")
                st.write(f"**{row['Expected']}**")
                st.caption("Based on contract")
            with cols[1]:
                st.caption("Actual Deduction")
                st.write(f"**{row['Actual']}**")
                st.caption("From Vendor Central")
            with cols[2]:
                st.caption("Variance")
                st.markdown(f"<span style='color: #DC2626; font-weight: bold;'>{row['Variance']}</span>", unsafe_allow_html=True)
                st.markdown("<span style='color: #DC2626;'>30.3% over</span>", unsafe_allow_html=True)
            
            # Why This Happened Section
            st.markdown("### Why This Happened")
            st.warning("Amazon applied 10% deduction on gross sales instead of net shipped amount as specified in contract.")
            
            # Contract Context Section
            st.markdown("### Contract Context")
            col1, col2 = st.columns(2)
            with col1:
                st.caption("Contract Basis")
                st.code("10% on Net Receipts")
            with col2:
                st.caption("Actual Calculation")
                st.code("Calculated on Gross Sales")
            
            # Action Buttons
            col1, col2, col3 = st.columns([6, 1, 1])
            with col2:
                if st.button("Close", key="close_modal"):
                    st.session_state["selected_row"] = None
            with col3:
                st.button("Prepare Dispute", key="prepare_dispute", type="primary")
# ----------------- Footer -----------------
    st.markdown("---")
    st.caption("© Pourri Intelligence • Recovery Dashboard v2.0")

elif nav == "Upload & Map":
    st.title("Upload & Map Data")
    st.caption("Upload your contract, Vendor Central, and NetSuite data to begin reconciliation")
    
    # Journey Header
    st.markdown("""
      <div class="journey-header">
         <div class="journey-icon">📤</div>
         <h2>Data Upload Journey</h2>
      </div>
      """, unsafe_allow_html=True)
    
    # Contract Document Upload
    st.markdown("""
        <div class="upload-section">
            <div class="section-number">1</div>
            <div class="upload-title">Contract Document</div>
            <div class="upload-description">Upload the retailer contract PDF to extract accrual terms</div>
        </div>
        """, unsafe_allow_html=True)
    contract_file = st.file_uploader("Choose Contract File", type=['pdf'], key="contract")

    # Vendor Central Data Upload
    st.markdown("""
        <div class="upload-section">
            <div class="section-number">2</div>
            <div class="upload-title">Vendor Central Data</div>
            <div class="upload-description">Upload Amazon Vendor Central deduction export (CSV/XLSX)</div>
        </div>
        """, unsafe_allow_html=True)
    vendor_file = st.file_uploader("Choose Vendor Central File", type=['csv', 'xlsx'], key="vendor")

    # NetSuite Truth Data Upload
    st.markdown("""
        <div class="upload-section">
            <div class="section-number">3</div>
            <div class="upload-title">NetSuite Truth Data</div>
            <div class="upload-description">Upload NetSuite invoice export as your source of truth</div>
        </div>
        """, unsafe_allow_html=True)
    netsuite_file = st.file_uploader("Choose NetSuite File", type=['csv', 'xlsx'], key="netsuite")