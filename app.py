import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from clean2 import df1

# ----------------- Page Config -----------------
st.set_page_config(page_title="Recovery Dashboard", layout="wide")

# ----------------- Custom CSS -----------------
st.markdown("""
<style>
/* --- MODAL STYLES --- */
.modal-backdrop {
   position: fixed;
   top: 0; left: 0; right: 0; bottom: 0;
   background: rgba(0,0,0,0.45);
   z-index: 998;
}
.deduction-modal {
   position: fixed;
   top: 50%; left: 50%;
   transform: translate(-50%, -50%);
   background: white;
   padding: 24px;
   border-radius: 12px;
   width: 90%;
   max-width: 800px;
   max-height: 90vh;
   overflow-y: auto;
   z-index: 999;
   box-shadow: 0 20px 25px rgba(0,0,0,0.1);
}
/* Status Colors */
.status-badge {
   display: inline-block;
   padding: 6px 12px;
   border-radius: 9999px;
   font-size: 14px;
   font-weight: 500;
   margin-bottom: 16px;
}
.status-disputable { background: #FEF2F2; color: #DC2626; }
.status-under-applied { background: #ECFEFF; color: #0891B2; }
.status-confirmed-valid { background: #F0FDF4; color: #16A34A; }
.status-pending-review { background: #FFF7ED; color: #EA580C; }
.detail-grid {
   display: grid;
   grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
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
/* GLOBAL APP STYLING */
body, .stApp {
  background-color: #ffffff !important;
  font-family: 'Inter', sans-serif !important;
  color: #1e293b !important;
}
h1, h2, h3, h4, h5 {
  color: #0f172a !important;
  font-weight: 600 !important;
}
/* SIDEBAR */
section[data-testid="stSidebar"] {
  background-color: #ffffff !important;
  border-right: 1px solid #e2e8f0;
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
.metric-label { color: #64748b; font-size: 1rem; margin-bottom: 0.5rem; }
.metric-value { font-size: 2rem; font-weight: 700; color: #1e293b; }
.metric-subtext { font-size: 0.9rem; color: #059669; font-weight: 500; }
.chart-container {
  background-color: #ffffff;
  border-radius: 16px;
  padding: 1rem;
  box-shadow: 0 2px 6px rgba(0,0,0,0.05);
  margin-bottom: 2rem;
}
/* TABLE INTERACTION */
[data-testid="stDataFrame"] table { cursor: pointer; }
[data-testid="stDataFrame"] tbody tr:hover {
   background-color: #F8FAFC !important;
}
</style>
""", unsafe_allow_html=True)

# ----------------- Sidebar -----------------
st.sidebar.title("Pourri Intelligence")
st.sidebar.caption("Deduction Recovery")
st.sidebar.markdown("---")
nav = st.sidebar.radio("Navigation", ["Dashboard", "Upload & Map"])
st.sidebar.markdown("---")
st.sidebar.write("**Pourri Team**  \nRecovery Intelligence")

# ----------------- Helper functions -----------------
def format_currency(val):
    if val >= 1_000_000_000:
        return f"${val/1_000_000_000:.1f}B"
    elif val >= 1_000_000:
        return f"${val/1_000_000:.1f}M"
    elif val >= 1_000:
        return f"${val/1_000:.0f}K"
    else:
        return f"${val:.0f}"

def render_kpi_card(icon, icon_color, label, value, subtext=None):
    subtext_html = f"<div class='metric-subtext'>{subtext}</div>" if subtext else ""
    st.markdown(f"""
    <div class="metric-card">
    <div class="metric-icon {icon_color}">{icon}</div>
    <div class="metric-label">{label}</div>
    <div class="metric-value">{value}</div>
    {subtext_html}
    </div>
    """, unsafe_allow_html=True)

def create_line_chart(df, x, ys, title, height=350):
    fig = px.line(
        df,
        x=x,
        y=ys,
        markers=True,
        template="plotly_white"
    )
    fig.update_traces(line=dict(width=3))
    fig.update_layout(
        height=height,
        plot_bgcolor="white",
        paper_bgcolor="white",
        legend=dict(orientation="h", y=-0.25, x=0.15),
        yaxis=dict(title="Amount ($)", tickformat="$,.0f", hoverformat="$.2f"),
        margin=dict(l=20, r=20, t=30, b=70),
        title=title,
        title_x=0.5,
    )
    return fig

def create_bar_chart(df, x, y, color_col, title, height=350):
    fig = px.bar(
        df,
        x=x,
        y=y,
        text=[format_currency(val) for val in df[y]],
        template="plotly_white",
        color=color_col,
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    fig.update_layout(
        height=height,
        showlegend=False,
        yaxis=dict(title="Amount ($)", tickformat="$,.0f", hoverformat="$.2f"),
        title=title,
        title_x=0.5,
        margin=dict(l=20, r=20, t=30, b=20)
    )
    fig.update_traces(textposition='auto')
    return fig

# ----------------- Dashboard Page -----------------
if nav == "Dashboard":
    st.title("Recovery Dashboard")
    st.caption("Turn complex data into calm confidence")

    # --- Data preprocessing ---
    df = df1.copy()
    df['Receive Date'] = pd.to_datetime(df['Receive Date'])
    df['Month'] = df['Receive Date'].dt.to_period('M').dt.to_timestamp()

    # Calculate KPIs
    total_deductions = df['Actual Deductions'].sum()
    recoverable_amount = df.loc[df['Variance'] > 0, 'Variance'].sum()
    disputes_active = df.loc[df['Classification'] == 'Disputable'].shape[0]

    # KPI cards in columns
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        render_kpi_card("💲", "icon-green", "Total Deductions", format_currency(total_deductions), "+8.2% vs prior period")
    with col2:
        pct_of_total = recoverable_amount / total_deductions if total_deductions else 0
        render_kpi_card("⚠️", "icon-red", "Recoverable Amount", format_currency(recoverable_amount), f"{pct_of_total:.1%} of total")
    with col3:
        # You can add real active disputes logic if available
        render_kpi_card("📄", "icon-blue", "Active Disputes", disputes_active, "In progress")
    with col4:
        # You can calculate real recovery rate if available
        render_kpi_card("📈", "icon-yellow", "Recovery Rate", "87.3%", "vs 82% target")

    st.markdown("<br>", unsafe_allow_html=True)

    # --- Monthly trends ---
    monthly_agg = df.groupby('Month').agg({
        'Actual Deductions': 'sum',
        'Expected Deductions': 'sum'
    }).reset_index()

    # Interactive metric selector
    selected_metrics = st.multiselect(
        "Select metrics to display", 
        ['Actual Deductions', 'Expected Deductions'], 
        default=['Actual Deductions', 'Expected Deductions']
    )
    if selected_metrics:
        st.plotly_chart(create_line_chart(monthly_agg, 'Month', selected_metrics, "Monthly Deduction Trends"), use_container_width=True)

    # --- Variance by Classification ---
    confirmed_valid = df.loc[df['Classification'] == 'Confirmed Valid']
    disputable = df.loc[df['Classification'] == 'Disputable']
    under_applied = df.loc[df['Classification'] == 'Under-Applied']

    values = {
        "Confirmed Valid": confirmed_valid.loc[confirmed_valid['Variance'] == 0, 'Actual Deductions'].sum(),
        "Disputable": disputable.loc[disputable['Variance'] > 0, 'Variance'].sum(),
        "Under-Applied": -under_applied.loc[under_applied['Variance'] < 0, 'Variance'].sum(),
    }
    chart_df = pd.DataFrame(list(values.items()), columns=["Classification", "Amount"])

    st.plotly_chart(create_bar_chart(chart_df, "Classification", "Amount", "Classification", "Variance by Classification"), use_container_width=True)

    # --- Table grouped by Invoice ID ---
    st.markdown("### Reconciliations Grouped by Invoice ID")


    grouped = df.groupby('Amazon Invoice ID').agg({
        'Receive Date': 'max',
        'Actual Deductions': 'sum',
        'Expected Deductions': 'sum',
        'Variance': 'sum'
    }).reset_index()

    grouped = grouped.rename(columns={
        'Amazon Invoice ID': 'Invoice ID',
        'Receive Date': 'Date',
        'Actual Deductions': 'Actual',
        'Expected Deductions': 'Expected',
        'Variance': 'Variance'
    })

    # Classification based on summed variance
    def classify(row):
        if row['Variance'] > 0:
            return 'Disputable'
        elif row['Variance'] == 0:
            return 'Confirmed Valid'
        else:
            return 'Under-Applied'
    grouped['Classification'] = grouped.apply(classify, axis=1)

    # For Under-Applied, show variance as positive
    grouped['Variance'] = grouped.apply(lambda r: abs(r['Variance']) if r['Classification']=='Under-Applied' else r['Variance'], axis=1)

    grouped['Date'] = pd.to_datetime(grouped['Date']).dt.strftime('%b %d, %Y')

    table_data = grouped[['Invoice ID', 'Date', 'Actual', 'Expected', 'Variance', 'Classification']].copy()
    table_data['Actual'] = table_data['Actual'].apply(lambda x: f"${x:,.0f}")
    table_data['Expected'] = table_data['Expected'].apply(lambda x: f"${x:,.0f}")
    table_data['Variance'] = table_data['Variance'].apply(lambda x: f"${x:,.0f}")

    def color_variance(val):
        num = float(val.replace('$','').replace(',',''))
        if num > 0:
            return 'crimson'
        elif num < 0:
            return 'seagreen'
        else:
            return 'gray'
    variance_colors = [color_variance(v) for v in table_data['Variance']]

    classification_colors = {
        "Disputable": "#fcdada",
        "Under-Applied": "#fff4d9",
        "Confirmed Valid": "#d9f1ef",
        "Pending Review": "#e3e8f0"
    }
    classification_bg_colors = [classification_colors.get(cls, '#ddd') for cls in table_data['Classification']]
    action_icons = ["🔗" for _ in range(len(table_data))]

    fig_table = go.Figure(data=[go.Table(
        columnwidth=[110, 90, 90, 90, 90, 130, 50],
        header=dict(
            values=["<b>Invoice ID</b>", "<b>Date</b>", "<b>Actual</b>", "<b>Expected</b>", "<b>Variance</b>", "<b>Classification</b>", "<b>Action</b>"],
            fill_color='white',
            line_color='rgba(0,0,0,0.1)',
            font=dict(color='black', size=14, family='Inter, sans-serif'),
            height=40,
            align='left'
        ),
        cells=dict(
            values=[
                table_data['Invoice ID'],
                table_data['Date'],
                table_data['Actual'],
                table_data['Expected'],
                table_data['Variance'],
                table_data['Classification'],
                action_icons
            ],
            fill_color=[
                ['white', '#f9fafb'] * (len(table_data)//2 + 1),
                ['white', '#f9fafb'] * (len(table_data)//2 + 1),
                ['white', '#f9fafb'] * (len(table_data)//2 + 1),
                ['white', '#f9fafb'] * (len(table_data)//2 + 1),
                ['white', '#f9fafb'] * (len(table_data)//2 + 1),
                classification_bg_colors,
                ['white', '#f9fafb'] * (len(table_data)//2 + 1),
            ],
            line_color='rgba(0,0,0,0.05)',
            font=dict(
                color=[
                    ['black'] * len(table_data),
                    ['black'] * len(table_data),
                    ['black'] * len(table_data),
                    ['black'] * len(table_data),
                    variance_colors,
                    ['black'] * len(table_data),
                    ['black'] * len(table_data)
                ],
                size=13,
                family='Inter, sans-serif'
            ),
            height=36,
            align='left',
            format=['', '', '', '', '', None, ''],
        )
    )])

    fig_table.update_layout(
        margin=dict(l=0, r=0, t=20, b=20),
        paper_bgcolor='white',
        plot_bgcolor='white',
        height=450,
        width=None
    )

    st.plotly_chart(fig_table, use_container_width=True)

    st.markdown("---")
    st.caption("© Pourri Intelligence • Recovery")

# ----------------- Upload Page -----------------
elif nav == "Upload & Map":
    st.title("Upload & Map Data")
    st.caption("Upload your contract, Vendor Central, and NetSuite data to begin reconciliation")
    st.markdown("""
    <div style="display:flex;align-items:center;gap:1rem;">
        <div style="background:#ecfdf5;border-radius:12px;padding:0.75rem;color:#10b981;font-size:1.5rem;">📤</div>
        <h2>Data Upload Journey</h2>
    </div>
    """, unsafe_allow_html=True)

    contract_file = st.file_uploader("📄 Upload Contract (PDF)", type=['pdf'])
    vendor_file = st.file_uploader("🧾 Upload Vendor Central Export (CSV/XLSX)", type=['csv','xlsx'])
    netsuite_file = st.file_uploader("💼 Upload NetSuite Data (CSV/XLSX)", type=['csv','xlsx'])
