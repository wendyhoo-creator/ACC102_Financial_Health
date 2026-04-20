import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import io
import csv
from wrds_utils import fetch_company_data, get_latest_data_date

st.set_page_config(page_title="Financial Health Dashboard", layout="wide")

# ---------- Title and subtitle ----------
st.title("🏥 Corporate Financial Health Dashboard")
st.markdown("**Helping investors identify financial risks and opportunities** – analyze a company's latest fiscal year using WRDS Compustat data.")

# ---------- Predefined company list ----------
company_list = {
    "Apple Inc.": "001690",
    "Microsoft Corp.": "012141",
    "Alphabet Inc. (Google)": "160329",
}

# ---------- Safe formatting functions ----------
def fmt_num(x, decimals=2):
    if pd.isna(x) or np.isinf(x):
        return "N/A"
    return f"{x:.{decimals}f}"

def fmt_pct(x, decimals=2):
    if pd.isna(x) or np.isinf(x):
        return "N/A"
    return f"{x:.{decimals}%}"

# ---------- Load industry benchmark ----------
@st.cache_data
def load_industry_benchmark():
    try:
        df = pd.read_csv('industry_benchmarks.csv')
        df['industry_code'] = df['industry_code'].astype(str).str.strip()
        return df
    except FileNotFoundError:
        return None

industry_bench = load_industry_benchmark()

# ---------- Generate CSV report ----------
def generate_csv_report(latest, industry_row, gvkey, year):
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Financial Health Report"])
    writer.writerow(["GVKEY", gvkey])
    writer.writerow(["Latest Fiscal Year", year])
    writer.writerow([])
    writer.writerow(["Metric", "Company Value"])
    writer.writerow(["Current Ratio", fmt_num(latest.get('current_ratio'))])
    writer.writerow(["Debt Ratio", fmt_pct(latest.get('debt_ratio'))])
    writer.writerow(["ROE", fmt_pct(latest.get('roe'))])
    writer.writerow(["Quick Ratio", fmt_num(latest.get('quick_ratio'))])
    writer.writerow(["Gross Margin", fmt_pct(latest.get('gross_margin'))])
    writer.writerow(["Net Margin", fmt_pct(latest.get('net_margin'))])
    writer.writerow(["Inventory Turnover", fmt_num(latest.get('inventory_turnover'), 1)])
    writer.writerow(["Receivables Turnover", fmt_num(latest.get('receivables_turnover'), 1)])
    if industry_row is not None:
        writer.writerow([])
        writer.writerow(["Industry Comparison", "Company", "Industry Median"])
        writer.writerow(["Current Ratio", fmt_num(latest.get('current_ratio')), fmt_num(industry_row['current_ratio'])])
        writer.writerow(["Debt Ratio", fmt_pct(latest.get('debt_ratio')), fmt_pct(industry_row['debt_ratio'])])
        writer.writerow(["ROE", fmt_pct(latest.get('roe')), fmt_pct(industry_row['roe'])])
        writer.writerow(["Gross Margin", fmt_pct(latest.get('gross_margin')), fmt_pct(industry_row['gross_margin'])])
        writer.writerow(["Net Margin", fmt_pct(latest.get('net_margin')), fmt_pct(industry_row['net_margin'])])
    return output.getvalue()

# ---------- Dynamic analysis summary ----------
def generate_analysis(latest, industry_row, company_name=""):
    text = ""
    cr = latest.get('current_ratio')
    dr = latest.get('debt_ratio')
    roe = latest.get('roe')
    gm = latest.get('gross_margin')
    nm = latest.get('net_margin')
    
    # Profitability
    if pd.notna(roe):
        if roe > 0.15:
            text += "✅ **High profitability**: ROE is excellent (>15%), indicating strong returns for shareholders. "
            if roe > 1.0 and company_name == "Apple Inc.":
                text += "Apple's extremely high ROE (>100%) is largely driven by massive share buybacks, which reduce the equity base, not solely by operating profit. "
            elif roe > 1.0:
                text += "Such extremely high ROE often results from significant share buybacks, reducing equity base. "
        elif roe < 0.05:
            text += "⚠️ **Low profitability**: ROE is below 5%, suggesting weak earnings relative to equity. "
    # Liquidity
    if pd.notna(cr):
        if cr < 1:
            text += "🔴 **Liquidity concern**: Current ratio below 1 means short-term liabilities exceed short-term assets, which may lead to solvency pressure. "
        elif cr > 2:
            text += "✅ **Strong liquidity**: Current ratio above 2 indicates comfortable coverage of short-term obligations. "
    # Leverage
    if pd.notna(dr):
        if dr > 0.6:
            text += "⚠️ **High leverage**: Debt ratio exceeds 60%, increasing financial risk. "
        elif dr < 0.4:
            text += "✅ **Conservative leverage**: Debt ratio below 40%, low financial risk. "
    # Operating efficiency
    if pd.notna(gm) and pd.notna(nm):
        if nm / gm < 0.3:
            text += "📉 **Operating efficiency gap**: Net margin is low relative to gross margin, suggesting high operating expenses or non-operating costs. "
    
    # Industry comparison
    if industry_row is not None:
        ind_cr = industry_row['current_ratio']
        ind_roe = industry_row['roe']
        if pd.notna(cr) and pd.notna(ind_cr):
            if cr > ind_cr * 1.2:
                text += f"📊 **Industry comparison**: Current ratio ({fmt_num(cr)}) is significantly higher than industry median ({fmt_num(ind_cr)}), indicating better short-term liquidity. "
            elif cr < ind_cr * 0.8:
                text += f"📊 **Industry comparison**: Current ratio ({fmt_num(cr)}) is notably lower than industry median ({fmt_num(ind_cr)}), posing a relative liquidity disadvantage. "
        if pd.notna(roe) and pd.notna(ind_roe):
            if roe > ind_roe * 1.5:
                text += f"💹 **Industry leadership**: ROE ({fmt_pct(roe)}) far exceeds industry median ({fmt_pct(ind_roe)}), demonstrating exceptional profitability. "
    if text == "":
        text = "No significant financial risks or advantages detected based on the selected metrics."
    return text

# ---------- Key insight card ----------
def key_insight(latest, industry_row):
    insights = []
    cr = latest.get('current_ratio')
    dr = latest.get('debt_ratio')
    roe = latest.get('roe')
    if pd.notna(roe) and roe > 0.20:
        insights.append(f"💡 **Key Insight**: ROE is {fmt_pct(roe)} – excellent profitability.")
    if pd.notna(cr) and cr < 1:
        insights.append(f"⚠️ **Key Insight**: Current ratio is {fmt_num(cr)} – potential short-term liquidity risk.")
    if industry_row is not None:
        ind_roe = industry_row['roe']
        if pd.notna(roe) and pd.notna(ind_roe) and roe > ind_roe * 1.5:
            insights.append(f"🏆 **Key Insight**: ROE outperforms industry median by a wide margin.")
    if not insights:
        insights.append("ℹ️ **Key Insight**: No extreme strengths or weaknesses identified.")
    return insights[0]

# ---------- Sidebar ----------
st.sidebar.subheader("Company Selection")
selected_company = st.sidebar.selectbox("Choose a company", list(company_list.keys()) + ["Other (enter GVKEY below)"])
if selected_company != "Other (enter GVKEY below)":
    default_gvkey = company_list[selected_company]
else:
    default_gvkey = "001690"

gvkey_input = st.sidebar.text_input("Or enter GVKEY manually", value=default_gvkey)

# GVKEY help information
st.sidebar.markdown("""
<details>
<summary>❓ What is a GVKEY?</summary>
GVKEY is a permanent identifier for companies in the WRDS Compustat database. 
You can find GVKEYs by searching company names on WRDS or using the pre-defined list above.
</details>
""", unsafe_allow_html=True)

if st.sidebar.button("Start Diagnosis"):
    if not gvkey_input:
        st.error("Please enter a GVKEY")
    else:
        with st.spinner("Fetching data from WRDS..."):
            df = fetch_company_data(gvkey_input)

        if df is None or df.empty:
            st.error("No data found for this GVKEY. Please check the input or ensure the company has financial statements.")
        else:
            # Sort by year
            df = df.sort_values('year').reset_index(drop=True)
            latest = df.iloc[-1]
            latest_year = int(latest['year'])
            data_date = get_latest_data_date(gvkey_input)

            st.info(f"📅 Latest fiscal year: {latest_year} (Data as of {data_date} – WRDS may have reporting lag)")

            # Core metric cards
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Current Ratio", fmt_num(latest.get('current_ratio')))
                st.caption(":grey[?] Current assets / Current liabilities. >2 indicates strong short-term solvency.")
            with col2:
                st.metric("Debt Ratio", fmt_pct(latest.get('debt_ratio')))
                st.caption(":grey[?] Total liabilities / Total assets. <50% is considered safe.")
            with col3:
                st.metric("ROE", fmt_pct(latest.get('roe')))
                st.caption(":grey[?] Net income / Shareholders' equity. >15% is excellent.")

            # Detailed ratios table
            st.subheader("📊 Detailed Financial Ratios")
            metrics_data = {
                "Metric": ["Quick Ratio", "Gross Margin", "Net Margin", "Inventory Turnover", "Receivables Turnover"],
                "Value": [
                    fmt_num(latest.get('quick_ratio')),
                    fmt_pct(latest.get('gross_margin')),
                    fmt_pct(latest.get('net_margin')),
                    f"{fmt_num(latest.get('inventory_turnover'), 1)} times" if pd.notna(latest.get('inventory_turnover')) else "N/A",
                    f"{fmt_num(latest.get('receivables_turnover'), 1)} times" if pd.notna(latest.get('receivables_turnover')) else "N/A"
                ]
            }
            st.dataframe(pd.DataFrame(metrics_data), use_container_width=True)

            # Risk alerts
            st.subheader("⚠️ Risk Alerts")
            risks = []
            cr = latest.get('current_ratio')
            dr = latest.get('debt_ratio')
            roe = latest.get('roe')
            if pd.notna(cr) and cr < 1:
                risks.append("🔴 Current ratio below 1: short-term solvency pressure")
            if pd.notna(dr) and dr > 0.6:
                risks.append("🔴 Debt ratio high (>60%): significant financial leverage")
            if pd.notna(roe) and roe < 0.05:
                risks.append("🟡 ROE low: profitability needs improvement")
            if not risks:
                risks.append("✅ No major financial risks detected")
            for r in risks:
                st.write(r)

            # Industry comparison
            industry_row = None
            sic_str = None
            if industry_bench is not None:
                sic_val = latest.get('sic')
                if pd.notna(sic_val):
                    try:
                        sic_int = int(float(sic_val))
                        sic_str = f"{sic_int:02d}"[:2]
                    except (ValueError, TypeError):
                        sic_str = None
                    if sic_str:
                        industry_row_df = industry_bench[industry_bench['industry_code'] == sic_str]
                        if not industry_row_df.empty:
                            industry_row = industry_row_df.iloc[0]
                            st.subheader("🏭 Industry Comparison")
                            comp_data = {
                                "Metric": ["Current Ratio", "Debt Ratio", "ROE", "Gross Margin", "Net Margin"],
                                "Company": [
                                    fmt_num(latest.get('current_ratio')),
                                    fmt_pct(latest.get('debt_ratio')),
                                    fmt_pct(latest.get('roe')),
                                    fmt_pct(latest.get('gross_margin')),
                                    fmt_pct(latest.get('net_margin'))
                                ],
                                "Industry Median": [
                                    fmt_num(industry_row['current_ratio']),
                                    fmt_pct(industry_row['debt_ratio']),
                                    fmt_pct(industry_row['roe']),
                                    fmt_pct(industry_row['gross_margin']),
                                    fmt_pct(industry_row['net_margin'])
                                ]
                            }
                            st.dataframe(pd.DataFrame(comp_data), use_container_width=True)
                        else:
                            st.info(f"No industry benchmark found for SIC code {sic_str}.")
                    else:
                        st.info("Invalid SIC code format.")
                else:
                    st.info("Company missing SIC code; cannot perform industry comparison.")
            else:
                st.warning("Industry benchmark file not found.")

            # Radar chart
            st.subheader("📡 Radar Chart: Company vs Industry Median")
            if industry_row is not None:
                st.markdown("💡 **Interpretation**: A larger filled area indicates better relative health. 'Debt Ratio (inverse)' = 1 - Debt Ratio, so higher is better.")
                categories = ['Current Ratio', 'Debt Ratio (inverse)', 'ROE', 'Gross Margin', 'Net Margin']
                company_values = [
                    latest.get('current_ratio'),
                    1 - latest.get('debt_ratio'),
                    latest.get('roe'),
                    latest.get('gross_margin'),
                    latest.get('net_margin')
                ]
                industry_values = [
                    industry_row['current_ratio'],
                    1 - industry_row['debt_ratio'],
                    industry_row['roe'],
                    industry_row['gross_margin'],
                    industry_row['net_margin']
                ]
                fig_radar = go.Figure()
                fig_radar.add_trace(go.Scatterpolar(
                    r=company_values, theta=categories, fill='toself', name='Company', line_color='blue'
                ))
                fig_radar.add_trace(go.Scatterpolar(
                    r=industry_values, theta=categories, fill='toself', name='Industry Median', line_color='red'
                ))
                fig_radar.update_layout(
                    polar=dict(radialaxis=dict(visible=True)),
                    showlegend=True
                )
                st.plotly_chart(fig_radar, use_container_width=True)
            else:
                st.info("Industry benchmark data not available for radar chart.")

            # Historical trends
            st.subheader("📈 Historical Trends (Last 5 Years)")
            df_yearly = df.groupby('year').agg({
                'current_ratio': 'last',
                'roe': 'last',
                'gross_margin': 'last'
            }).reset_index()
            df_yearly['year'] = df_yearly['year'].astype(int)
            df_yearly = df_yearly.sort_values('year')
            df_trend = df_yearly.tail(5)
            if len(df_trend) >= 2:
                fig_trend = go.Figure()
                fig_trend.add_trace(go.Scatter(
                    x=df_trend['year'], y=df_trend['current_ratio'],
                    mode='lines+markers', name='Current Ratio',
                    yaxis='y1'
                ))
                roe_pct = df_trend['roe'] * 100
                gm_pct = df_trend['gross_margin'] * 100
                fig_trend.add_trace(go.Scatter(
                    x=df_trend['year'], y=roe_pct,
                    mode='lines+markers', name='ROE (%)',
                    yaxis='y2'
                ))
                fig_trend.add_trace(go.Scatter(
                    x=df_trend['year'], y=gm_pct,
                    mode='lines+markers', name='Gross Margin (%)',
                    yaxis='y2'
                ))
                fig_trend.update_layout(
                    title="Historical Trends (Left: Current Ratio, Right: ROE & Gross Margin %)",
                    xaxis_title="Year",
                    yaxis=dict(title="Current Ratio", side="left"),
                    yaxis2=dict(title="Percentage (%)", overlaying="y", side="right"),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5)
                )
                fig_trend.update_xaxes(tickformat='d', dtick=1)
                st.plotly_chart(fig_trend, use_container_width=True)
            else:
                st.info("Not enough years of data to show trend.")

            # Key insight card
            st.subheader("💎 Key Insight")
            insight = key_insight(latest, industry_row)
            st.info(insight)

            # Financial analysis summary
            st.subheader("📝 Financial Analysis Summary")
            company_name = selected_company if selected_company in company_list else "Selected Company"
            analysis_text = generate_analysis(latest, industry_row, company_name)
            st.write(analysis_text)

            # Download report CSV
            csv_data = generate_csv_report(latest, industry_row, gvkey_input, latest_year)
            st.download_button(
                label="📥 Download Report as CSV",
                data=csv_data,
                file_name=f"financial_health_{gvkey_input}_{latest_year}.csv",
                mime="text/csv"
            )

            # Footer
            st.markdown("---")
            st.caption("Data source: WRDS Compustat (accessed April 2026). Financial ratios are calculated from reported figures. This tool is for educational purposes only.")