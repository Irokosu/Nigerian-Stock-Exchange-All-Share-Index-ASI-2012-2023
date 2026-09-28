"""
================================================================================
MODULE 01: RETURN & PERFORMANCE ANALYSIS
Created by: OPEYEMI SAMSON IROKOSU
PURPOSE:
- Compound Annual Growth Rates (CAGR), rolling returns, cumulative growth,
  annual calendar performance, and best/worst trading intervals over 11 years.
================================================================================
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

from backend.data_loader import load_clean_data
from backend.calculations import (
    calculate_cumulative_growth,
    calculate_annual_returns,
    calculate_monthly_returns_matrix,
    calculate_rolling_returns,
    get_best_worst_intervals,
    calculate_cagr
)

# ------------------------------------------------------------------------------
# 1. PAGE SETUP
# ------------------------------------------------------------------------------
st.set_page_config(
    page_title="Return & Performance | NSE ASI Hub",
    page_icon="",
    layout="wide"
)

# Custom Styling (Emerald & Champagne Gold Theme)
st.markdown("""
<style>
    .page-header {
        background: linear-gradient(135deg, #064E3B 0%, #008751 100%);
        border-left: 6px solid #D4AF37;
        padding: 24px;
        border-radius: 12px;
        color: white;
        margin-bottom: 25px;
    }
    .page-title {
        font-size: 2.2rem;
        font-weight: 800;
        margin: 0;
    }
    .page-subtitle {
        font-size: 1rem;
        color: #E2E8F0;
        margin-top: 6px;
    }
    .stat-card {
        background: white;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 16px;
        border-left: 4px solid #008751;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.04);
        margin-bottom: 12px;
    }
    .stat-title {
        font-size: 0.8rem;
        font-weight: 700;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .stat-value {
        font-size: 1.5rem;
        font-weight: 800;
        color: #064E3B;
        margin: 4px 0;
    }
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# 2. LOAD DATA
# ------------------------------------------------------------------------------
try:
    df = load_clean_data()
except Exception as e:
    st.error(f"Error loading clean dataset: {e}")
    st.stop()

# ------------------------------------------------------------------------------
# 3. HEADER BANNER
# ------------------------------------------------------------------------------
st.markdown("""
<div class="page-header">
    <div class="page-title"> Return & Performance Analysis</div>
    <div class="page-subtitle">
        Evaluating the wealth-generation dynamics, compounded growth, calendar returns, 
        and rolling momentum of the Nigerian Stock Exchange (NSE) All-Share Index across 11.9 years.
    </div>
</div>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# 4. SECTION 1: INVESTMENT WEALTH ACCUMULATION SIMULATOR
# ------------------------------------------------------------------------------
st.markdown("### Hypothetical Investment Wealth Simulator")
st.caption("Illustrate close-to-close ASI price growth over a selected period. Dividends, fees, taxes, and tracking differences are excluded.")

# Simulator Controls
c_input1, c_input2 = st.columns([1, 2])

with c_input1:
    initial_capital = st.number_input(
        "Initial Capital Investment (NGN):",
        min_value=1_000,
        max_value=100_000_000,
        value=100_000,
        step=10_000,
        format="%d"
    )

with c_input2:
    date_range = st.date_input(
        "Select Investment Time Window:",
        value=(df['date'].min().date(), df['date'].max().date()),
        min_value=df['date'].min().date(),
        max_value=df['date'].max().date()
    )

# Filter dataset to selected range
if len(date_range) == 2:
    start_dt, end_dt = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
    filtered_df = df[(df['date'] >= start_dt) & (df['date'] <= end_dt)].copy()
else:
    filtered_df = df.copy()

if filtered_df.empty:
    st.warning("No data points available for the selected dates.")
    st.stop()

# Compute growth trajectory
growth_df = calculate_cumulative_growth(filtered_df, initial_capital=initial_capital)

start_close = filtered_df['close'].iloc[0]
end_close = filtered_df['close'].iloc[-1]
final_wealth = growth_df['portfolio_value'].iloc[-1]
net_profit = final_wealth - initial_capital
total_gain_pct = ((end_close - start_close) / start_close) * 100.0

time_span_years = (filtered_df['date'].iloc[-1] - filtered_df['date'].iloc[0]).days / 365.25
cagr_val = calculate_cagr(start_close, end_close, time_span_years)

# Display Simulator KPI Cards
m1, m2, m3, m4 = st.columns(4)
with m1:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-title">Initial Investment</div>
        <div class="stat-value">NGN {initial_capital:,.0f}</div>
        <span style="color:#64748B; font-size:0.8rem;">{filtered_df['date'].iloc[0].strftime('%d %b %Y')}</span>
    </div>
    """, unsafe_allow_html=True)

with m2:
    st.markdown(f"""
    <div class="stat-card" style="border-left-color: #D4AF37;">
        <div class="stat-title">Terminal Wealth</div>
        <div class="stat-value">NGN {final_wealth:,.2f}</div>
        <span style="color:#10B981; font-size:0.8rem; font-weight:700;">+NGN {net_profit:,.2f} Profit</span>
    </div>
    """, unsafe_allow_html=True)

with m3:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-title">ASI Price Return</div>
        <div class="stat-value" style="color: {'#008751' if total_gain_pct >= 0 else '#EF4444'};">
            {'+' if total_gain_pct >= 0 else ''}{total_gain_pct:.2f}%
        </div>
        <span style="color:#64748B; font-size:0.8rem;">Across {len(filtered_df):,} trading days</span>
    </div>
    """, unsafe_allow_html=True)

with m4:
    st.markdown(f"""
    <div class="stat-card" style="border-left-color: #D4AF37;">
        <div class="stat-title">Period CAGR</div>
        <div class="stat-value">+{cagr_val:.2f}%</div>
        <span style="color:#64748B; font-size:0.8rem;">Annualized Compound Growth</span>
    </div>
    """, unsafe_allow_html=True)

# Plot Cumulative Portfolio Wealth Trajectory
fig_growth = go.Figure()

fig_growth.add_trace(go.Scatter(
    x=growth_df['date'],
    y=growth_df['portfolio_value'],
    mode='lines',
    name='Portfolio Value (NGN)',
    line=dict(color='#008751', width=2.5),
    fill='tozeroy',
    fillcolor='rgba(0, 135, 81, 0.08)',
    hovertemplate="<b>Date</b>: %{x|%d %b %Y}<br><b>Portfolio Value</b>: NGN %{y:,.2f}<extra></extra>"
))

fig_growth.add_hline(
    y=initial_capital,
    line_dash="dash",
    line_color="#D4AF37",
    annotation_text=f"Capital Baseline (NGN {initial_capital:,.0f})",
    annotation_position="bottom right"
)

fig_growth.update_layout(
    title="Cumulative Wealth Growth Trajectory (NGN)",
    height=420,
    margin=dict(l=20, r=20, t=40, b=20),
    template="plotly_white",
    xaxis=dict(showgrid=True, gridcolor="#F1F5F9"),
    yaxis=dict(title="Portfolio Value (NGN)", tickprefix="NGN ", tickformat=",.0f", showgrid=True, gridcolor="#F1F5F9"),
    hovermode="x unified"
)
st.plotly_chart(fig_growth, width="stretch")

st.write("---")

# ------------------------------------------------------------------------------
# 5. SECTION 2: ANNUAL CALENDAR RETURNS & MONTHLY SEASONALITY MATRIX
# ------------------------------------------------------------------------------
st.markdown("### Annual Returns & Monthly Seasonality Heatmap")

col_ann1, col_ann2 = st.columns([1, 1.2])

annual_df = calculate_annual_returns(df)

with col_ann1:
    st.markdown("#### Annual Performance by Year (%)")
    
    # Color code bars: Emerald for positive, Crimson for negative
    bar_colors = ['#008751' if r >= 0 else '#EF4444' for r in annual_df['annual_return_pct']]
    
    fig_annual = go.Figure(go.Bar(
        x=annual_df['year'],
        y=annual_df['annual_return_pct'],
        marker_color=bar_colors,
        text=[f"{r:+.1f}%" for r in annual_df['annual_return_pct']],
        textposition='outside',
        hovertemplate="<b>Year %{x}</b>: %{y:+.2f}%<extra></extra>"
    ))
    
    fig_annual.update_layout(
        height=400,
        margin=dict(l=20, r=20, t=30, b=20),
        template="plotly_white",
        xaxis=dict(tickmode='linear', tick0=2012, dtick=1, showgrid=False),
        yaxis=dict(title="Annual Return (%)", showgrid=True, gridcolor="#F1F5F9", zerolinecolor="#1E293B"),
    )
    st.plotly_chart(fig_annual, width="stretch")

with col_ann2:
    st.markdown("#### Monthly Return Distribution Heatmap (%)")
    
    monthly_matrix = calculate_monthly_returns_matrix(df)
    
    # Custom color scale for monthly returns (Red -> Neutral -> Emerald Green)
    fig_heat = px.imshow(
        monthly_matrix,
        labels=dict(x="Month", y="Year", color="Return (%)"),
        x=monthly_matrix.columns,
        y=monthly_matrix.index,
        color_continuous_scale=[[0.0, '#DC2626'], [0.5, '#F8FAFC'], [1.0, '#008751']],
        color_continuous_midpoint=0.0,
        text_auto=".1f",
        aspect="auto"
    )
    fig_heat.update_layout(
        height=400,
        margin=dict(l=20, r=20, t=30, b=20),
        coloraxis_colorbar=dict(title="Return (%)", thickness=12)
    )
    st.plotly_chart(fig_heat, width="stretch")

st.write("---")

# ------------------------------------------------------------------------------
# 6. SECTION 3: ROLLING RETURNS MOMENTUM
# ------------------------------------------------------------------------------
st.markdown("### Multi-Horizon Rolling Returns Dynamics")
st.caption("Rolling annualized windows uncover true market cycles and cyclical regimes beyond arbitrary calendar cutoffs.")

rolling_df = calculate_rolling_returns(df)

fig_rolling = go.Figure()

fig_rolling.add_trace(go.Scatter(
    x=rolling_df['date'],
    y=rolling_df['roll_3m_pct'],
    mode='lines',
    name='3-Month Rolling Return',
    line=dict(color='#D4AF37', width=1.5),
    hovertemplate="3M Rolling: %{y:+.2f}%<extra></extra>"
))

fig_rolling.add_trace(go.Scatter(
    x=rolling_df['date'],
    y=rolling_df['roll_1y_pct'],
    mode='lines',
    name='1-Year (252D) Rolling Return',
    line=dict(color='#008751', width=2.2),
    hovertemplate="1Y Rolling: %{y:+.2f}%<extra></extra>"
))

fig_rolling.add_hline(y=0, line_dash="dash", line_color="#94A3B8", line_width=1)

fig_rolling.update_layout(
    height=420,
    margin=dict(l=20, r=20, t=30, b=20),
    template="plotly_white",
    xaxis=dict(showgrid=True, gridcolor="#F1F5F9"),
    yaxis=dict(title="Rolling Return (%)", showgrid=True, gridcolor="#F1F5F9"),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    hovermode="x unified"
)
st.plotly_chart(fig_rolling, width="stretch")

st.write("---")

# ------------------------------------------------------------------------------
# 7. SECTION 4: BEST & WORST TRADING INTERVALS
# ------------------------------------------------------------------------------
st.markdown("### Extreme Performance Horizons: Best vs. Worst Historical Windows")
st.caption("A stress test of upside velocity versus peak downside shocks across 11 years of trading.")

extremes_table = get_best_worst_intervals(df)

st.dataframe(
    extremes_table.style.format({
        'Best Return (%)': '+{:.2f}%',
        'Worst Return (%)': '{:.2f}%'
    }).map(
        lambda v: 'color: #008751; font-weight: bold;' if '+' in str(v) else ('color: #DC2626; font-weight: bold;' if '-' in str(v) else ''),
        subset=['Best Return (%)', 'Worst Return (%)']
    ),
    width="stretch",
    hide_index=True
)
