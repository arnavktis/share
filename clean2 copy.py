import pandas as pd
import numpy as np
from collections import Counter

# Load Excel file and sheets
f = pd.ExcelFile("AMZN_NETSUITE_POs_SOs_Mapping 1.xlsx")

# Load Amazon PO sheet
df1 = pd.read_excel(
    f,
    sheet_name="AmzaonPO",
    dtype={'Purchase Order': str, 'UPC': str}
)

# Load Custom Sales Order Register
df2 = pd.read_excel(
    f,
    sheet_name="CustomSalesOrderRegisterM",
    skiprows=6,
    dtype={'Reference Number': str, 'Item: UPC Code': str, 'SPS UPC': str}
)

df3 = pd.read_excel(
    f,
    sheet_name="Mapping",
    skiprows=1,
    dtype={'Reference Number': str, 'SO Item: UPC Code': str}
)

control = pd.read_excel(
    f,
    sheet_name="Control",
    skiprows=2,
    dtype={'UPC': str, 'SO Item: UPC Code': str}
)

df1 = df1.groupby(["Purchase Order", "UPC"], as_index=False).agg({
    'Amazon Invoice ID': 'first',           # or use a custom function if needed
    'Receive Date': 'min',                  # earliest receive date
    'Quantity': 'sum',
    'Net Receipts': 'sum'
})

upc_map = dict(zip(control["UPC"], control["SO Item: UPC Code"]))

df1["SO Reference Number"] = df1["Purchase Order"].where(
    df1["Purchase Order"].isin(df2["Reference Number"])
)

df1["SO Item: UPC Code"] = df1["UPC"].map(upc_map)


df1["SO Total Revenue"] = df1.apply(
    lambda row: df2.loc[
        (df2["Reference Number"] == row["SO Reference Number"]) &
        (df2["Item: UPC Code"] == row["SO Item: UPC Code"]),
        "Total Revenue"
    ].sum(),
    axis=1
)


df1['Variance'] = (df1['Net Receipts'] - df1['SO Total Revenue'])/10
df1.loc[df1["SO Item: UPC Code"].isna() | (df1["SO Item: UPC Code"] == ""), "Variance"] = 0

df1['Actual Deductions'] = df1['Net Receipts']/10 
df1['Expected Deductions'] = df1['SO Total Revenue']/10
df1['Classification'] = df1['Variance'].apply(
    lambda x: 'Disputable' if x > 0 else ('Under-Applied' if x < 0 else 'Confirmed Valid')
)

print(df1["Variance"].sum())