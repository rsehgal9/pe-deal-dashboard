import pandas as pd
import streamlit as st

st.set_page_config(page_title="PE Mini LBO Dashboard", layout="wide")

# -----------------------------
# Load data
# -----------------------------
df = pd.read_excel("deals.xlsx")

# -----------------------------
# Helper functions
# -----------------------------
def classify_company(row):
    if row["Growth"] >= 15 and row["EBITDA_Margin"] >= 20:
        return "High-Quality Compounder"
    elif row["EV_EBITDA"] <= 8.0 and row["Debt_EBITDA"] <= 3.5:
        return "Value Opportunity"
    elif row["Debt_EBITDA"] >= 4.0:
        return "Higher Leverage"
    else:
        return "Core Platform"

def investment_rationale(row):
    reasons = []
    if row["Growth"] >= 15:
        reasons.append("strong topline growth")
    if row["EBITDA_Margin"] >= 20:
        reasons.append("attractive profitability")
    if row["EV_EBITDA"] <= 8.5:
        reasons.append("reasonable entry valuation")
    if row["Debt_EBITDA"] <= 3.0:
        reasons.append("manageable leverage")

    if not reasons:
        return "Mixed profile with no single standout attribute."
    return ", ".join(reasons).capitalize() + "."

def compute_lbo_metrics(row, hold_period, exit_multiple, ebitda_haircut, annual_debt_paydown, margin_expansion_bps):
    entry_ebitda = row["EBITDA"]
    entry_multiple = row["EV_EBITDA"]
    entry_debt_multiple = row["Debt_EBITDA"]
    growth = row["Growth"]

    entry_ev = entry_ebitda * entry_multiple
    entry_debt = entry_ebitda * entry_debt_multiple
    entry_equity = entry_ev - entry_debt

    underwritten_growth = max(growth * (1 - ebitda_haircut / 100), -50)

    projected_ebitda = entry_ebitda
    projected_margin = row["EBITDA_Margin"]

    debt_balance = entry_debt
    yearly_rows = []

    for year in range(1, hold_period + 1):
        projected_ebitda *= (1 + underwritten_growth / 100)
        projected_margin += margin_expansion_bps / 100

        paydown_amount = min(debt_balance, annual_debt_paydown)
        debt_balance -= paydown_amount

        yearly_rows.append({
            "Year": year,
            "Projected EBITDA": projected_ebitda,
            "Projected EBITDA Margin": projected_margin,
            "Debt Balance": debt_balance
        })

    exit_ev = projected_ebitda * exit_multiple
    exit_equity = exit_ev - debt_balance

    moic = exit_equity / entry_equity if entry_equity > 0 else None
    irr = (moic ** (1 / hold_period) - 1) if moic and moic > 0 else None

    return {
        "entry_ev": entry_ev,
        "entry_debt": entry_debt,
        "entry_equity": entry_equity,
        "exit_ebitda": projected_ebitda,
        "exit_ev": exit_ev,
        "exit_debt": debt_balance,
        "exit_equity": exit_equity,
        "moic": moic,
        "irr": irr,
        "yearly_df": pd.DataFrame(yearly_rows)
    }

def build_irr_sensitivity(row, hold_period, ebitda_haircut, annual_debt_paydown, margin_expansion_bps):
    exit_multiples = [8.0, 10.0, 12.0]
    growth_factors = [0.8, 1.0, 1.2]

    grid = []

    for g in growth_factors:
        sensitivity_row = {}
        adjusted_growth_row = row.copy()
        adjusted_growth_row["Growth"] = row["Growth"] * g

        for multiple in exit_multiples:
            result = compute_lbo_metrics(
                adjusted_growth_row,
                hold_period,
                multiple,
                ebitda_haircut,
                annual_debt_paydown,
                margin_expansion_bps
            )
            irr_value = result["irr"]
            label = f"{irr_value * 100:.1f}%" if irr_value is not None else "N/A"
            sensitivity_row[f"{multiple:.1f}x Exit"] = label

        growth_label = f"{g:.1f}x Growth"
        sensitivity_row["Scenario"] = growth_label
        grid.append(sensitivity_row)

    sens_df = pd.DataFrame(grid)
    cols = ["Scenario"] + [c for c in sens_df.columns if c != "Scenario"]
    return sens_df[cols]

# -----------------------------
# Base logic
# -----------------------------
df["Score"] = (
    df["Growth"] * 0.40
    + df["EBITDA_Margin"] * 0.30
    - df["EV_EBITDA"] * 0.20
    - df["Debt_EBITDA"] * 0.10
)

df["Company_Type"] = df.apply(classify_company, axis=1)
df["Investment_Rationale"] = df.apply(investment_rationale, axis=1)

# -----------------------------
# Title
# -----------------------------
st.title("Private Equity Deal Intelligence Dashboard")
st.markdown("Mini LBO version: screen targets and estimate sponsor-style returns under configurable underwriting assumptions.")

# -----------------------------
# Sidebar: screening filters
# -----------------------------
st.sidebar.header("Screening Filters")

industries = ["All"] + sorted(df["Industry"].unique().tolist())
selected_industry = st.sidebar.selectbox("Industry", industries)

min_margin = st.sidebar.slider("Minimum EBITDA Margin (%)", 0, 40, 15)
min_growth = st.sidebar.slider("Minimum Revenue Growth (%)", 0, 30, 5)
max_ev = st.sidebar.slider("Maximum EV / EBITDA", 5.0, 15.0, 12.0)
max_debt_multiple = st.sidebar.slider("Maximum Debt / EBITDA", 1.0, 5.0, 4.5)

# -----------------------------
# Sidebar: LBO assumptions
# -----------------------------
st.sidebar.header("Mini LBO Assumptions")

hold_period = st.sidebar.slider("Hold Period (Years)", 3, 7, 5)
exit_multiple = st.sidebar.slider("Exit EV / EBITDA", 6.0, 16.0, 10.0, 0.5)
ebitda_haircut = st.sidebar.slider("Growth Haircut (%)", 0, 75, 25)
annual_debt_paydown = st.sidebar.slider("Annual Debt Paydown ($M)", 0, 100, 20)
margin_expansion_bps = st.sidebar.slider("Annual Margin Expansion (bps)", 0, 300, 50, 25)

# -----------------------------
# Filter data
# -----------------------------
filtered_df = df.copy()

if selected_industry != "All":
    filtered_df = filtered_df[filtered_df["Industry"] == selected_industry]

filtered_df = filtered_df[
    (filtered_df["EBITDA_Margin"] >= min_margin) &
    (filtered_df["Growth"] >= min_growth) &
    (filtered_df["EV_EBITDA"] <= max_ev) &
    (filtered_df["Debt_EBITDA"] <= max_debt_multiple)
].copy()

# -----------------------------
# Run mini LBO
# -----------------------------
if not filtered_df.empty:
    results = []

    for _, row in filtered_df.iterrows():
        lbo = compute_lbo_metrics(
            row=row,
            hold_period=hold_period,
            exit_multiple=exit_multiple,
            ebitda_haircut=ebitda_haircut,
            annual_debt_paydown=annual_debt_paydown,
            margin_expansion_bps=margin_expansion_bps
        )

        results.append({
            "Company": row["Company"],
            "Industry": row["Industry"],
            "Company_Type": row["Company_Type"],
            "Revenue": row["Revenue"],
            "EBITDA": row["EBITDA"],
            "Growth": row["Growth"],
            "EBITDA_Margin": row["EBITDA_Margin"],
            "EV_EBITDA": row["EV_EBITDA"],
            "Debt_EBITDA": row["Debt_EBITDA"],
            "Score": row["Score"],
            "Entry_EV": lbo["entry_ev"],
            "Entry_Debt": lbo["entry_debt"],
            "Entry_Equity": lbo["entry_equity"],
            "Exit_EBITDA": lbo["exit_ebitda"],
            "Exit_EV": lbo["exit_ev"],
            "Exit_Debt": lbo["exit_debt"],
            "Exit_Equity": lbo["exit_equity"],
            "MOIC": lbo["moic"],
            "IRR": lbo["irr"],
            "Investment_Rationale": row["Investment_Rationale"],
            "Yearly_Detail": lbo["yearly_df"]
        })

    lbo_df = pd.DataFrame(results)

    lbo_df["Adjusted_Score"] = (
        lbo_df["Score"]
        + lbo_df["MOIC"].fillna(0) * 2.0
        + lbo_df["IRR"].fillna(0) * 10.0
    )

    ranked_df = lbo_df.sort_values("Adjusted_Score", ascending=False).reset_index(drop=True)
    ranked_df.index = ranked_df.index + 1
else:
    ranked_df = pd.DataFrame()

# -----------------------------
# KPI section
# -----------------------------
st.subheader("Key Metrics")

k1, k2, k3, k4 = st.columns(4)

if not ranked_df.empty:
    k1.metric("Companies Screened In", len(ranked_df))
    k2.metric("Average EV / EBITDA", f"{ranked_df['EV_EBITDA'].mean():.1f}x")
    k3.metric("Average MOIC", f"{ranked_df['MOIC'].mean():.2f}x")
    k4.metric("Average IRR", f"{ranked_df['IRR'].mean() * 100:.1f}%")
else:
    k1.metric("Companies Screened In", 0)
    k2.metric("Average EV / EBITDA", "N/A")
    k3.metric("Average MOIC", "N/A")
    k4.metric("Average IRR", "N/A")

# -----------------------------
# Charts
# -----------------------------
st.subheader("Deal and Return Profile")

c1, c2 = st.columns(2)

with c1:
    if not ranked_df.empty:
        st.markdown("**MOIC by Company**")
        st.bar_chart(ranked_df.set_index("Company")[["MOIC"]])
    else:
        st.info("No companies match the current filters.")

with c2:
    if not ranked_df.empty:
        st.markdown("**IRR by Company**")
        st.bar_chart(ranked_df.set_index("Company")[["IRR"]])
    else:
        st.info("No companies match the current filters.")

# -----------------------------
# Ranked table
# -----------------------------
st.subheader("Ranked Mini LBO Output")

if not ranked_df.empty:
    display_df = ranked_df[[
        "Company",
        "Industry",
        "Company_Type",
        "Revenue",
        "EBITDA",
        "Growth",
        "EBITDA_Margin",
        "EV_EBITDA",
        "Debt_EBITDA",
        "Entry_EV",
        "Entry_Equity",
        "Exit_EBITDA",
        "Exit_EV",
        "Exit_Equity",
        "MOIC",
        "IRR"
    ]].copy()

    display_df["Revenue"] = display_df["Revenue"].map(lambda x: f"${x:,.0f}M")
    display_df["EBITDA"] = display_df["EBITDA"].map(lambda x: f"${x:,.0f}M")
    display_df["Growth"] = display_df["Growth"].map(lambda x: f"{x:.1f}%")
    display_df["EBITDA_Margin"] = display_df["EBITDA_Margin"].map(lambda x: f"{x:.1f}%")
    display_df["EV_EBITDA"] = display_df["EV_EBITDA"].map(lambda x: f"{x:.1f}x")
    display_df["Debt_EBITDA"] = display_df["Debt_EBITDA"].map(lambda x: f"{x:.1f}x")
    display_df["Entry_EV"] = display_df["Entry_EV"].map(lambda x: f"${x:,.0f}M")
    display_df["Entry_Equity"] = display_df["Entry_Equity"].map(lambda x: f"${x:,.0f}M")
    display_df["Exit_EBITDA"] = display_df["Exit_EBITDA"].map(lambda x: f"${x:,.0f}M")
    display_df["Exit_EV"] = display_df["Exit_EV"].map(lambda x: f"${x:,.0f}M")
    display_df["Exit_Equity"] = display_df["Exit_Equity"].map(lambda x: f"${x:,.0f}M")
    display_df["MOIC"] = display_df["MOIC"].map(lambda x: f"{x:.2f}x" if pd.notnull(x) else "N/A")
    display_df["IRR"] = display_df["IRR"].map(lambda x: f"{x * 100:.1f}%" if pd.notnull(x) else "N/A")

    st.dataframe(display_df, use_container_width=True)

    csv_export = ranked_df.drop(columns=["Yearly_Detail"]).to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download Mini LBO Output",
        data=csv_export,
        file_name="mini_lbo_output.csv",
        mime="text/csv"
    )

    best = ranked_df.iloc[0]

    st.subheader("Top Pick Summary")
    st.write(
        f"""
        **{best['Company']}** ranks as the top target under the current mini LBO assumptions.

        **Business profile**
        - Industry: {best['Industry']}
        - Classification: {best['Company_Type']}
        - Revenue growth: {best['Growth']:.1f}%
        - EBITDA margin: {best['EBITDA_Margin']:.1f}%
        - Entry multiple: {best['EV_EBITDA']:.1f}x
        - Entry leverage: {best['Debt_EBITDA']:.1f}x

        **Mini LBO output**
        - Entry EV: ${best['Entry_EV']:,.0f}M
        - Entry Equity: ${best['Entry_Equity']:,.0f}M
        - Exit EBITDA: ${best['Exit_EBITDA']:,.0f}M
        - Exit EV: ${best['Exit_EV']:,.0f}M
        - Exit Equity: ${best['Exit_Equity']:,.0f}M
        - MOIC: {best['MOIC']:.2f}x
        - IRR: {best['IRR'] * 100:.1f}%

        **Why it works**
        {best['Investment_Rationale']}
        """
    )

    # Detailed yearly build
    st.subheader("Year-by-Year Build for Top Pick")
    yearly_df = best["Yearly_Detail"].copy()
    yearly_df["Projected EBITDA"] = yearly_df["Projected EBITDA"].map(lambda x: f"${x:,.1f}M")
    yearly_df["Projected EBITDA Margin"] = yearly_df["Projected EBITDA Margin"].map(lambda x: f"{x:.1f}%")
    yearly_df["Debt Balance"] = yearly_df["Debt Balance"].map(lambda x: f"${x:,.1f}M")
    st.dataframe(yearly_df, use_container_width=True)

    # Sensitivity table
    st.subheader("IRR Sensitivity")
    sensitivity_df = build_irr_sensitivity(
        row=best,
        hold_period=hold_period,
        ebitda_haircut=ebitda_haircut,
        annual_debt_paydown=annual_debt_paydown,
        margin_expansion_bps=margin_expansion_bps
    )
    st.dataframe(sensitivity_df, use_container_width=True)

else:
    st.warning("No companies match the current filters. Broaden the screen.")