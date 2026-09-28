"""
================================================================================
MODULE 02: RISK & VOLATILITY ANALYSIS
Created by: OPEYEMI SAMSON IROKOSU
PURPOSE:
- Rolling historical volatility regimes.
- Peak-to-trough underwater drawdown curves and MDD event summary.
- Historical & Parametric Value at Risk (VaR 95%/99%).
- Expected Shortfall / Conditional VaR (CVaR).
================================================================================
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.figure_factory as ff
import numpy as np
import pandas as pd
from scipy import stats

from backend.data_loader import load_clean_data
from backend.calculations import (
    calculate_rolling_volatility,
    calculate_drawdown,
    get_max_drawdown_stats,
    calculate_var_cvar
)

# ------------------------------------------------------------------------------
# 1. PAGE SETUP
# ------------------------------------------------------------------------------
st.set_page_config(
    page_title="Risk & Volatility | NSE ASI Hub",
    page_icon="",
    layout="wide"
)

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
    .page-title   { font-size: 2.2rem; font-weight: 800; margin: 0; }
    .page-subtitle { font-size: 1rem; color: #E2E8F0; margin-top: 6px; }

    .stat-card {
        background: white;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 16px;
        border-left: 4px solid #008751;
        box-shadow: 0 2px 5px rgba(0,0,0,0.04);
        margin-bottom: 12px;
    }
    .stat-card.gold  { border-left-color: #D4AF37; }
    .stat-card.red   { border-left-color: #DC2626; }
    .stat-title { font-size: 0.8rem; font-weight: 700; color: #64748B;
                  text-transform: uppercase; letter-spacing: 0.5px; }
    .stat-value { font-size: 1.5rem; font-weight: 800; color: #064E3B; margin: 4px 0; }
    .stat-sub   { font-size: 0.8rem; color: #64748B; }

    [data-testid="stSidebar"] { background-color: #064E3B; }
    [data-testid="stSidebar"] * { color: #FFFFFF !important; }
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# 2. LOAD DATA
# ------------------------------------------------------------------------------
try:
    df = load_clean_data()
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

# ------------------------------------------------------------------------------
# 3. HEADER BANNER
# ------------------------------------------------------------------------------
st.markdown("""
<div class="page-header">
    <div class="page-title"> Risk & Volatility Analysis</div>
    <div class="page-subtitle">
        Rolling volatility regimes, maximum drawdown anatomy, Value at Risk (VaR),
        and Expected Shortfall (CVaR) across 11.9 years of Nigerian Stock Exchange trading.
    </div>
</div>
""", unsafe_allow_html=True)

# Pre-compute all risk metrics
vol_df     = calculate_rolling_volatility(df)
dd_df      = calculate_drawdown(df)
mdd_stats  = get_max_drawdown_stats(df)
var_data   = calculate_var_cvar(df)

# ------------------------------------------------------------------------------
# 4. SECTION 1: EXECUTIVE RISK KPI CARDS
# ------------------------------------------------------------------------------
st.markdown("### Core Risk Metrics at a Glance")

k1, k2, k3, k4, k5 = st.columns(5)

with k1:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-title">Annualized Volatility</div>
        <div class="stat-value">{var_data['ann_volatility']:.2f}%</div>
        <div class="stat-sub">Full Period (2012-2023)</div>
    </div>""", unsafe_allow_html=True)

with k2:
    st.markdown(f"""
    <div class="stat-card red">
        <div class="stat-title">Max Drawdown (MDD)</div>
        <div class="stat-value" style="color:#DC2626;">{mdd_stats['mdd_pct']:.2f}%</div>
        <div class="stat-sub">Peak-to-Trough Decline</div>
    </div>""", unsafe_allow_html=True)

with k3:
    st.markdown(f"""
    <div class="stat-card gold">
        <div class="stat-title">Historical VaR (95%)</div>
        <div class="stat-value">{var_data['var_95_hist']:.2f}%</div>
        <div class="stat-sub">Daily Loss Threshold</div>
    </div>""", unsafe_allow_html=True)

with k4:
    st.markdown(f"""
    <div class="stat-card red">
        <div class="stat-title">Historical VaR (99%)</div>
        <div class="stat-value" style="color:#DC2626;">{var_data['var_99_hist']:.2f}%</div>
        <div class="stat-sub">Tail Risk Threshold</div>
    </div>""", unsafe_allow_html=True)

with k5:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-title">CVaR / Exp. Shortfall (95%)</div>
        <div class="stat-value">{var_data['cvar_95_hist']:.2f}%</div>
        <div class="stat-sub">Avg Loss Beyond VaR</div>
    </div>""", unsafe_allow_html=True)

st.write("---")

# ------------------------------------------------------------------------------
# 5. SECTION 2: ROLLING VOLATILITY REGIMES
# ------------------------------------------------------------------------------
st.markdown("### Rolling Annualized Volatility Regimes")
st.caption(
    "Volatility is not constant - it clusters in high-stress regimes (2015-2016 oil shock, "
    "2020 COVID crash) and compresses during bull-market calm periods."
)

fig_vol = go.Figure()

fig_vol.add_trace(go.Scatter(
    x=vol_df['date'], y=vol_df['vol_21d'],
    mode='lines', name='21-Day (1 Month)',
    line=dict(color='#D4AF37', width=1.4),
    hovertemplate="21D Vol: %{y:.2f}%<extra></extra>"
))
fig_vol.add_trace(go.Scatter(
    x=vol_df['date'], y=vol_df['vol_63d'],
    mode='lines', name='63-Day (1 Quarter)',
    line=dict(color='#F97316', width=1.8),
    hovertemplate="63D Vol: %{y:.2f}%<extra></extra>"
))
fig_vol.add_trace(go.Scatter(
    x=vol_df['date'], y=vol_df['vol_252d'],
    mode='lines', name='252-Day (1 Year)',
    line=dict(color='#008751', width=2.4),
    hovertemplate="252D Vol: %{y:.2f}%<extra></extra>"
))

# Add average reference line
avg_vol = vol_df['vol_252d'].mean()
fig_vol.add_hline(
    y=avg_vol, line_dash="dot", line_color="#64748B",
    annotation_text=f"Full-Period Avg: {avg_vol:.1f}%",
    annotation_position="top left"
)

fig_vol.update_layout(
    height=420, template="plotly_white",
    margin=dict(l=20, r=20, t=30, b=20),
    xaxis=dict(showgrid=True, gridcolor="#F1F5F9"),
    yaxis=dict(title="Annualized Volatility (%)", showgrid=True, gridcolor="#F1F5F9"),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    hovermode="x unified"
)
st.plotly_chart(fig_vol, width="stretch")

st.write("---")

# ------------------------------------------------------------------------------
# 6. SECTION 3: DRAWDOWN UNDERWATER CURVE & MDD ANATOMY
# ------------------------------------------------------------------------------
st.markdown("### Drawdown Anatomy & Maximum Drawdown Event")

col_dd1, col_dd2 = st.columns([2, 1])

with col_dd1:
    st.markdown("#### Underwater Drawdown Curve (2012-2023)")
    st.caption("Shows at every point in time how far the market sits below its prior all-time high.")

    fig_dd = go.Figure()

    fig_dd.add_trace(go.Scatter(
        x=dd_df['date'], y=dd_df['drawdown_pct'],
        mode='lines', name='Drawdown (%)',
        line=dict(color='#DC2626', width=1.8),
        fill='tozeroy',
        fillcolor='rgba(220, 38, 38, 0.08)',
        hovertemplate="<b>Date</b>: %{x|%d %b %Y}<br><b>Drawdown</b>: %{y:.2f}%<extra></extra>"
    ))

    # Mark the MDD trough
    fig_dd.add_annotation(
        x=mdd_stats['trough_date'], y=mdd_stats['mdd_pct'],
        text=f"<b>MDD: {mdd_stats['mdd_pct']:.2f}%</b><br>{mdd_stats['trough_date'].strftime('%b %Y')}",
        showarrow=True, arrowhead=2, arrowcolor='#D4AF37',
        ax=60, ay=40,
        bgcolor="#064E3B", bordercolor="#D4AF37",
        font=dict(color="white", size=10)
    )

    fig_dd.update_layout(
        height=380, template="plotly_white",
        margin=dict(l=20, r=20, t=30, b=20),
        xaxis=dict(showgrid=True, gridcolor="#F1F5F9"),
        yaxis=dict(title="Drawdown from Peak (%)", showgrid=True, gridcolor="#F1F5F9"),
        hovermode="x unified"
    )
    st.plotly_chart(fig_dd, width="stretch")

with col_dd2:
    st.markdown("#### MDD Event Summary")
    st.write("")

    recovery_text = (
        mdd_stats['recovery_date'].strftime('%d %b %Y')
        if mdd_stats['recovery_date'] else "Not yet recovered"
    )

    st.markdown(f"""
    <div class="stat-card red">
        <div class="stat-title">Maximum Drawdown</div>
        <div class="stat-value" style="color:#DC2626;">{mdd_stats['mdd_pct']:.2f}%</div>
        <div class="stat-sub">Worst Peak-to-Trough Decline</div>
    </div>
    <div class="stat-card gold">
        <div class="stat-title">Pre-Crash Peak</div>
        <div class="stat-value">{mdd_stats['peak_val']:,.2f}</div>
        <div class="stat-sub">{mdd_stats['peak_date'].strftime('%d %b %Y')}</div>
    </div>
    <div class="stat-card red">
        <div class="stat-title">Crash Trough</div>
        <div class="stat-value" style="color:#DC2626;">{mdd_stats['trough_val']:,.2f}</div>
        <div class="stat-sub">{mdd_stats['trough_date'].strftime('%d %b %Y')}</div>
    </div>
    <div class="stat-card">
        <div class="stat-title">Recovery Date</div>
        <div class="stat-value" style="font-size:1.1rem;">{recovery_text}</div>
        <div class="stat-sub">First Close >= Pre-Crash Peak</div>
    </div>
    """, unsafe_allow_html=True)

st.write("---")

# ------------------------------------------------------------------------------
# 7. SECTION 4: VaR & CVaR ANALYSIS
# ------------------------------------------------------------------------------
st.markdown("### Value at Risk (VaR) & Expected Shortfall (CVaR)")
st.caption(
    "Historical Simulation uses the actual empirical return distribution. "
    "Parametric assumes a Gaussian (Normal) distribution. "
    "CVaR is the average loss in the worst-case tail beyond the VaR threshold."
)

col_v1, col_v2 = st.columns([1, 1.4])

with col_v1:
    st.markdown("#### VaR & CVaR Risk Table")

    var_table = pd.DataFrame({
        'Method': [
            'Historical (95%)', 'Historical (99%)',
            'Parametric (95%)', 'Parametric (99%)'
        ],
        'VaR (Daily Loss %)': [
            var_data['var_95_hist'], var_data['var_99_hist'],
            var_data['var_95_param'], var_data['var_99_param']
        ],
        'CVaR / Exp. Shortfall (%)': [
            var_data['cvar_95_hist'], var_data['cvar_99_hist'],
            np.nan, np.nan
        ]
    })
    st.dataframe(var_table, width="stretch", hide_index=True)

    st.info(
        "**Historical sample estimate**: The 5th-percentile close-to-close return corresponds to an estimated loss of "
        f"**{var_data['var_95_hist']:.2f}%** (95% historical VaR). The average loss in the sample tail beyond that threshold is "
        f"**{var_data['cvar_95_hist']:.2f}%** (historical CVaR). These estimates are not future loss guarantees."
    )

with col_v2:
    st.markdown("#### Empirical Return Distribution vs. Normal Curve")

    returns_pct = var_data['returns_pct']
    mu    = returns_pct.mean()
    sigma = returns_pct.std()
    x_range = np.linspace(returns_pct.min(), returns_pct.max(), 300)
    normal_curve = stats.norm.pdf(x_range, mu, sigma)

    fig_dist = go.Figure()

    # Histogram of actual returns
    fig_dist.add_trace(go.Histogram(
        x=returns_pct,
        nbinsx=80,
        histnorm='probability density',
        name='Empirical Returns',
        marker_color='rgba(0, 135, 81, 0.55)',
        marker_line=dict(color='#008751', width=0.5),
        hovertemplate="Return: %{x:.2f}%<extra></extra>"
    ))

    # Fitted Normal distribution overlay
    fig_dist.add_trace(go.Scatter(
        x=x_range, y=normal_curve,
        mode='lines', name='Normal Distribution',
        line=dict(color='#D4AF37', width=2.5, dash='dash'),
        hoverinfo='skip'
    ))

    # VaR 95% threshold line
    fig_dist.add_vline(
        x=-var_data['var_95_hist'],
        line_dash="dot", line_color="#DC2626",
        annotation_text="VaR 95%",
        annotation_position="top right",
        annotation_font=dict(color="#DC2626", size=10)
    )
    fig_dist.add_vline(
        x=-var_data['var_99_hist'],
        line_dash="dot", line_color="#7F1D1D",
        annotation_text="VaR 99%",
        annotation_position="top right",
        annotation_font=dict(color="#7F1D1D", size=10)
    )

    fig_dist.update_layout(
        height=380, template="plotly_white",
        margin=dict(l=20, r=20, t=30, b=20),
        xaxis=dict(title="Daily Return (%)", showgrid=True, gridcolor="#F1F5F9"),
        yaxis=dict(title="Probability Density", showgrid=True, gridcolor="#F1F5F9"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        barmode='overlay'
    )
    st.plotly_chart(fig_dist, width="stretch")
