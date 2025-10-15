import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from io import BytesIO

# ----------------- Page Config -----------------
st.set_page_config(page_title="Recovery Dashboard", layout="wide")

# ----------------- Custom CSS (unchanged from your version) -----------------
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

# ----------------- Data Load -----------------
REQUIRED_SHEETS = ["AmzaonPO", "CustomSalesOrderRegisterM", "Mapping", "Control"]

@st.cache_data(show_spinner=False)
def load_and_prepare(workbook_bytes: bytes):
    f = pd.ExcelFile(BytesIO(workbook_bytes))
    missing = [s for s in REQUIRED_SHEETS if s not in f.sheet_names]
    if missing:
        raise ValueError(f"Workbook missing required sheet(s): {', '.join(missing)}")

    po_df = pd.read_excel(f, sheet_name="AmzaonPO", dtype={'Purchase Order': str, 'UPC': str})
    so_reg = pd.read_excel(f, sheet_name="CustomSalesOrderRegisterM", skiprows=6,
                           dtype={'Reference Number': str, 'Item: UPC Code': str, 'SPS UPC': str})
    control_df = pd.read_excel(f, sheet_name="Control", skiprows=2, dtype={'UPC': str, 'SO Item: UPC Code': str})

    agg_df = po_df.groupby(["Purchase Order", "UPC"], as_index=False).agg({
        'Amazon Invoice ID': 'first',
        'Receive Date': 'min',
        'Quantity': 'sum',
        'Net Receipts': 'sum'
    })

    upc_map = dict(zip(control_df.get("UPC", []), control_df.get("SO Item: UPC Code", [])))
    agg_df["SO Reference Number"] = agg_df["Purchase Order"].where(
        agg_df["Purchase Order"].isin(so_reg["Reference Number"])
    )
    agg_df["SO Item: UPC Code"] = agg_df["UPC"].map(upc_map)

    def compute_so_total(row):
        mask = (
            (so_reg["Reference Number"] == row["SO Reference Number"]) &
            (so_reg["Item: UPC Code"] == row["SO Item: UPC Code"])
        )
        return so_reg.loc[mask, "Total Revenue"].sum()

    agg_df["SO Total Revenue"] = agg_df.apply(compute_so_total, axis=1)
    agg_df['Variance'] = (agg_df['Net Receipts'] - agg_df['SO Total Revenue']) / 10
    agg_df.loc[agg_df["SO Item: UPC Code"].isna(), "Variance"] = 0
    agg_df['Actual Deductions'] = agg_df['Net Receipts'] / 10
    agg_df['Expected Deductions'] = agg_df['SO Total Revenue'] / 10
    agg_df['Classification'] = agg_df['Variance'].apply(
        lambda x: 'Disputable' if x > 0 else ('Under-Applied' if x < 0 else 'Confirmed Valid')
    )
    return agg_df

# ----------------- Upload -----------------
st.sidebar.title("Pourri Intelligence")
uploaded_file = st.sidebar.file_uploader("Upload Deduction Workbook (Excel)", type=["xlsx", "xls"])

if uploaded_file is None:
    st.title("Recovery Dashboard")
    st.write("Please upload the Excel workbook containing the required sheets.")
    st.stop()

df = load_and_prepare(uploaded_file.getvalue())

# ----------------- Helpers -----------------
def safe_money(val):
    try:
        if val is None or isinstance(val, type) or callable(val):
            return "$0"
        if hasattr(val, 'item'): val = val.item()
        return f"${float(val):,.0f}"
    except Exception:
        return "$0"

def safe_pct(numer, denom):
    try:
        if isinstance(numer, type) or isinstance(denom, type):
            return "0.0%"
        numer, denom = float(numer), float(denom)
        if denom == 0: return "0.0%"
        return f"{(numer/denom)*100:.1f}%"
    except Exception:
        return "0.0%"

def format_currency(val):
    if val >= 1_000_000: return f"${val/1_000_000:.1f}M"
    elif val >= 1_000: return f"${val/1_000:.0f}K"
    else: return f"${val:.0f}"

def render_kpi_card(icon, icon_color, label, value, subtext=None):
    sub = f"<div class='metric-subtext'>{subtext}</div>" if subtext else ""
    st.markdown(f"""
    <div class="metric-card">
      <div class="metric-icon {icon_color}">{icon}</div>
      <div class="metric-label">{label}</div>
      <div class="metric-value">{value}</div>
      {sub}
    </div>
    """, unsafe_allow_html=True)

# ----------------- KPIs -----------------
st.title("Recovery Dashboard")
st.caption("Turn complex data into calm confidence")

df['Receive Date'] = pd.to_datetime(df['Receive Date'])
df['Month'] = df['Receive Date'].dt.to_period('M').dt.to_timestamp()
total_deductions = df['Actual Deductions'].sum()
recoverable_amount = df.loc[df['Variance'] > 0, 'Variance'].sum()
disputes_active = df.loc[df['Classification'] == 'Disputable'].shape[0]

col1, col2, col3, col4 = st.columns(4)
with col1: render_kpi_card("💲", "icon-green", "Total Deductions", format_currency(total_deductions))
with col2: render_kpi_card("⚠️", "icon-red", "Recoverable Amount", format_currency(recoverable_amount))
with col3: render_kpi_card("📄", "icon-blue", "Active Disputes", disputes_active)
with col4: render_kpi_card("📈", "icon-yellow", "Recovery Rate", "87.3%", "vs 82% target")

# ----------------- Charts -----------------
def create_line_chart(df, x, ys, title):
    fig = px.line(df, x=x, y=ys, markers=True, template="plotly_white")
    fig.update_traces(line=dict(width=3))
    fig.update_layout(height=350, plot_bgcolor="white", paper_bgcolor="white",
                      legend=dict(orientation="h", y=-0.25, x=0.15),
                      yaxis=dict(title="Amount ($)", tickformat="$,.0f"),
                      title=title, title_x=0.5)
    return fig

def create_bar_chart(df, x, y, color_col, title):
    fig = px.bar(df, x=x, y=y, text=[format_currency(v) for v in df[y]],
                 color=color_col, template="plotly_white",
                 color_discrete_sequence=px.colors.qualitative.Set2)
    fig.update_traces(textposition='auto')
    fig.update_layout(height=350, showlegend=False,
                      yaxis=dict(title="Amount ($)", tickformat="$,.0f"),
                      title=title, title_x=0.5)
    return fig

monthly_agg = df.groupby('Month').agg({
    'Actual Deductions': 'sum',
    'Expected Deductions': 'sum'
}).reset_index()

line_fig = create_line_chart(monthly_agg, 'Month',
                             ['Actual Deductions', 'Expected Deductions'],
                             "Monthly Deduction Trends")

confirmed_valid = df[df['Classification'] == 'Confirmed Valid']
disputable = df[df['Classification'] == 'Disputable']
under_applied = df[df['Classification'] == 'Under-Applied']
values = {
    "Confirmed Valid": confirmed_valid['Actual Deductions'].sum(),
    "Disputable": disputable['Variance'].sum(),
    "Under-Applied": -under_applied['Variance'].sum(),
}
chart_df = pd.DataFrame(list(values.items()), columns=["Classification", "Amount"])
bar_fig = create_bar_chart(chart_df, "Classification", "Amount", "Classification", "Variance by Classification")

colA, colB = st.columns(2)
with colA: st.plotly_chart(line_fig, use_container_width=True)
with colB: st.plotly_chart(bar_fig, use_container_width=True)

# ----------------- Reconciliations -----------------
grouped = df.groupby('Amazon Invoice ID').agg({
    'Receive Date': 'max',
    'Actual Deductions': 'sum',
    'Expected Deductions': 'sum',
    'Variance': 'sum'
}).reset_index()
grouped.rename(columns={'Amazon Invoice ID':'Invoice ID','Receive Date':'Date','Actual Deductions':'Actual','Expected Deductions':'Expected'}, inplace=True)
for c in ['Actual','Expected','Variance']: grouped[c] = grouped[c].apply(lambda v: 0 if isinstance(v,type) else v)

grouped['Classification'] = grouped['Variance'].apply(lambda x: 'Disputable' if x>0 else ('Under-Applied' if x<0 else 'Confirmed Valid'))
grouped['Date'] = pd.to_datetime(grouped['Date']).dt.strftime('%b %d, %Y')

if 'show_modal' not in st.session_state: st.session_state['show_modal']=False
if 'active_invoice' not in st.session_state: st.session_state['active_invoice']=None

def reason_text(r):
    if r['Classification'] == 'Disputable': return f"Amazon applied a deduction resulting in an over-deduction of {safe_money(abs(r['Variance']))}."
    if r['Classification'] == 'Under-Applied': return "Deduction taken was below expected; potential missed recovery opportunity."
    return "Deduction aligns with contract terms."

def render_modal(inv_id):
    r = grouped.loc[grouped['Invoice ID']==inv_id].iloc[0]
    cls = r['Classification']
    badge_class = {'Disputable':'status-disputable','Under-Applied':'status-under-applied','Confirmed Valid':'status-confirmed-valid'}.get(cls,'status-pending-review')
    variance_num = float(r['Variance']) if not isinstance(r['Variance'], type) else 0
    st.markdown(f"""
    <div class='modal-backdrop'></div>
    <div class='deduction-modal'>
      <div style='display:flex;justify-content:space-between;align-items:center;'>
        <h3>Deduction Details</h3>
        <span style='cursor:pointer;font-size:20px;'>✕</span>
      </div>
      <div class='status-badge {badge_class}'>{cls}</div>
      <div style='color:#dc2626;font-size:14px;margin-bottom:12px;'>Variance: {safe_money(variance_num)}</div>
      <div class='detail-grid'>
        <div class='detail-item'><div class='detail-label'>Expected</div><div class='detail-value'>{safe_money(r['Expected'])}</div></div>
        <div class='detail-item'><div class='detail-label'>Actual</div><div class='detail-value'>{safe_money(r['Actual'])}</div></div>
        <div class='detail-item'><div class='detail-label'>Variance %</div><div class='detail-value'>{safe_pct(r['Variance'],r['Expected'])}</div></div>
      </div>
      <div style='background:#FFF7ED;padding:12px;border-radius:10px;margin-bottom:16px;font-size:13px;color:#7a5a2b;'>{reason_text(r)}</div>
      <div style='display:flex;justify-content:flex-end;gap:10px;'>
        <button style='background:#e2e8f0;border:none;padding:10px 16px;border-radius:8px;cursor:pointer;'>Close</button>
        <button style='background:#047857;color:white;border:none;padding:10px 16px;border-radius:8px;cursor:pointer;'>Prepare Dispute</button>
      </div>
    </div>
    """, unsafe_allow_html=True)

# ----------------- Invoice Table -----------------
st.markdown("### Reconciliations")
cols = st.columns([1.3,1,1,1,1,1])
for h,c in zip(["Invoice ID","Date","Actual","Expected","Variance","Classification"],cols): c.markdown(f"**{h}**")

badge_colors={'Disputable':('#DC2626','#FEF2F2'),'Under-Applied':('#0891B2','#ECFEFF'),'Confirmed Valid':('#16A34A','#F0FDF4')}
for _,row in grouped.iterrows():
    c1,c2,c3,c4,c5,c6 = st.columns([1.3,1,1,1,1,1])
    if c1.button(str(row['Invoice ID']), key=f"inv_{row['Invoice ID']}"):
        st.session_state['active_invoice']=row['Invoice ID']; st.session_state['show_modal']=True
    c2.write(row['Date'])
    c3.write(safe_money(row['Actual']))
    c4.write(safe_money(row['Expected']))
    c5.write(safe_money(row['Variance']))
    fg,bg=badge_colors.get(row['Classification'],('#334155','#E2E8F0'))
    c6.markdown(f"<span style='background:{bg};color:{fg};padding:4px 10px;border-radius:999px;font-size:12px;font-weight:500;'>{row['Classification']}</span>",unsafe_allow_html=True)

if st.session_state['show_modal'] and st.session_state['active_invoice']:
    render_modal(st.session_state['active_invoice'])
    if st.button("Close Modal"):
        st.session_state['show_modal']=False; st.session_state['active_invoice']=None; st.rerun()

st.markdown("---")
st.caption("© Pourri Intelligence • Recovery")
