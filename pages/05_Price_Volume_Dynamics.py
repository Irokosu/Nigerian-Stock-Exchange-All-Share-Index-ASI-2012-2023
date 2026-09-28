"""
================================================================================
MODULE 05: PRICE-VOLUME DYNAMICS
Created by: OPEYEMI SAMSON IROKOSU
PURPOSE:
- Dual-axis Price and Volume liquidity tracking.
- Volume Moving Averages (20D, 50D) & Surge ratio detection.
- Cumulative On-Balance Volume (OBV) descriptive participation analysis.
- Volume distribution across up-days vs. down-days.
- Historical top volume spike events.
================================================================================
"""

import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

from backend.data_loader import load_clean_data
from backend.calculations import (
    get_clean_volume_data,
    calculate_volume_metrics,
    calculate_obv,
    calculate_price_volume_correlation,
    get_top_volume_days
)

# ------------------------------------------------------------------------------
# 1. PAGE SETUP
# ------------------------------------------------------------------------------
st.set_page_config(
    page_title="Price-Volume Dynamics | NSE ASI Hub",
    page_icon="",
    layout="wide"
)

st.markdown("""
<style>
    .page-header {
        background: linear-gradient(135deg, #064E3B 0%, #008751 100%);
        border-left: 6px solid #D4AF37;
        padding: 24px; border-radius: 12px;
        color: white; margin-bottom: 25px;
    }
    .page-title   { font-size: 2.2rem; font-weight: 800; margin: 0; }
    .page-subtitle { font-size: 1rem; color: #E2E8F0; margin-top: 6px; }

    .data-notice {
        background: #F8FAFC;
        border: 1.5px solid #94A3B8;
        border-radius: 10px;
        padding: 16px 20px;
        margin-bottom: 22px;
        color: #0F172A;
    }
    .data-notice-title {
        font-weight: 800; color: #064E3B; font-size: 0.95rem; margin-bottom: 4px;
    }

    .stat-card {
        background: white; border: 1px solid #E2E8F0;
        border-radius: 10px; padding: 16px;
        border-left: 4px solid #008751;
        box-shadow: 0 2px 5px rgba(0,0,0,0.04);
        margin-bottom: 12px;
    }
    .stat-card.gold { border-left-color: #D4AF37; }
    .stat-card.red  { border-left-color: #DC2626; }
    .stat-title { font-size: 0.8rem; font-weight: 700; color: #64748B;
                  text-transform: uppercase; letter-spacing: 0.5px; }
    .stat-value { font-size: 1.45rem; font-weight: 800; color: #064E3B; margin: 4px 0; }
    .stat-sub   { font-size: 0.8rem; color: #64748B; }

    [data-testid="stSidebar"] { background-color: #064E3B; }
    [data-testid="stSidebar"] * { color: #FFFFFF !important; }
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# 2. LOAD DATA & COMPUTE
# ------------------------------------------------------------------------------
try:
    df = load_clean_data()
except Exception as e:
    st.error(f"Error loading dataset: {e}")
    st.stop()

v_df = get_clean_volume_data(df)
vol_metrics = calculate_volume_metrics(df)
obv_df = calculate_obv(df)
corr_df = calculate_price_volume_correlation(df, window=63)
top_volume_table = get_top_volume_days(df, top_n=10)

avg_vol_20 = vol_metrics['vol_sma_20'].iloc[-1]
avg_vol_50 = vol_metrics['vol_sma_50'].iloc[-1]
max_vol_row = v_df.loc[v_df['volume'].idxmax()]
current_vol = v_df['volume'].iloc[-1]
current_surge = current_vol / avg_vol_20 if avg_vol_20 > 0 else 1.0

# ------------------------------------------------------------------------------
# 3. HEADER BANNER & DATA NOTICE
# ------------------------------------------------------------------------------
st.markdown("""
<div class="page-header">
    <div class="page-title"> Price-Volume Dynamics</div>
    <div class="page-subtitle">
        Market liquidity analysis, volume participation via On-Balance Volume (OBV), 
        and high-volume surge identification on the Nigerian Stock Exchange.
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="data-notice">
    <div class="data-notice-title">Market Microstructure Note: Volume Data Coverage</div>
    <div>
        Historical trading volume in the archive begins recording systematically from 
        <b>{v_df['date'].iloc[0].strftime('%B %d, %Y')}</b> (pre-mid-2015 data records 0.00 volume in raw records). 
        Analyses use the <b>{len(v_df):,} sessions</b> with recorded positive volume; the file does not document the original volume source or completeness checks.
    </div>
</div>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# 4. SECTION 1: VOLUME KPIS
# ------------------------------------------------------------------------------
st.markdown("### Liquidity & Volume Overview")

c1, c2, c3, c4, c5 = st.columns(5)

with c1:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-title">Latest Day Volume</div>
        <div class="stat-value">{current_vol:,.0f}</div>
        <div class="stat-sub">{v_df['date'].iloc[-1].strftime('%d %b %Y')}</div>
    </div>""", unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="stat-card gold">
        <div class="stat-title">20-Day Avg Volume</div>
        <div class="stat-value">{avg_vol_20:,.0f}</div>
        <div class="stat-sub">Short-term Baseline</div>
    </div>""", unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-title">50-Day Avg Volume</div>
        <div class="stat-value">{avg_vol_50:,.0f}</div>
        <div class="stat-sub">Quarterly Baseline</div>
    </div>""", unsafe_allow_html=True)

with c4:
    surge_color = "#008751" if current_surge >= 1.0 else "#64748B"
    st.markdown(f"""
    <div class="stat-card gold">
        <div class="stat-title">Volume Surge Factor</div>
        <div class="stat-value" style="color:{surge_color};">{current_surge:.2f}x</div>
        <div class="stat-sub">Relative to 20-Day SMA</div>
    </div>""", unsafe_allow_html=True)

with c5:
    st.markdown(f"""
    <div class="stat-card red">
        <div class="stat-title">Record Volume Peak</div>
        <div class="stat-value" style="font-size:1.25rem;">{max_vol_row['volume']:,.0f}</div>
        <div class="stat-sub">{max_vol_row['date'].strftime('%d %b %Y')}</div>
    </div>""", unsafe_allow_html=True)

st.write("---")

# ------------------------------------------------------------------------------
# 5. SECTION 2: DUAL-AXIS PRICE & VOLUME TIMELINE
# ------------------------------------------------------------------------------
st.markdown("### Price Trajectory vs. Trading Volume")
st.caption("Green bars denote positive market days; red bars denote negative market days. Gold line represents the 20-Day Volume SMA.")

fig_pv = make_subplots(
    rows=2, cols=1,
    shared_xaxes=True,
    vertical_spacing=0.04,
    row_heights=[0.65, 0.35],
    subplot_titles=("NSE ASI Close Level", "Trading Volume & 20-Day Liquidity SMA")
)

# Row 1: Price
fig_pv.add_trace(
    go.Scatter(
        x=v_df['date'], y=v_df['close'],
        mode='lines', name='NSE ASI Close',
        line=dict(color='#064E3B', width=2.0),
        hovertemplate="<b>Date</b>: %{x|%d %b %Y}<br><b>Close</b>: %{y:,.2f} pts<extra></extra>"
    ),
    row=1, col=1
)

# Row 2: Volume Bars
v_colors = ['#008751' if ret >= 0 else '#DC2626' for ret in v_df['daily_return'].fillna(0)]
fig_pv.add_trace(
    go.Bar(
        x=v_df['date'], y=v_df['volume'],
        name='Trading Volume',
        marker_color=v_colors, opacity=0.7,
        hovertemplate="<b>Volume</b>: %{y:,.0f}<extra></extra>"
    ),
    row=2, col=1
)

# Row 2: 20-Day Volume SMA
fig_pv.add_trace(
    go.Scatter(
        x=vol_metrics['date'], y=vol_metrics['vol_sma_20'],
        mode='lines', name='20D Volume SMA',
        line=dict(color='#D4AF37', width=1.8),
        hovertemplate="20D Vol SMA: %{y:,.0f}<extra></extra>"
    ),
    row=2, col=1
)

fig_pv.update_layout(
    height=550, template="plotly_white",
    margin=dict(l=20, r=20, t=30, b=20),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    hovermode="x unified"
)
fig_pv.update_yaxes(title_text="Index Points", showgrid=True, gridcolor="#F1F5F9", row=1, col=1)
fig_pv.update_yaxes(title_text="Shares Traded", showgrid=True, gridcolor="#F1F5F9", row=2, col=1)
fig_pv.update_xaxes(showgrid=True, gridcolor="#F1F5F9")

st.plotly_chart(fig_pv, width="stretch")

st.write("---")

# ------------------------------------------------------------------------------
# 6. SECTION 3: ON-BALANCE VOLUME (OBV) & ACCUMULATION
# ------------------------------------------------------------------------------
st.markdown("### On-Balance Volume (OBV) Participation Indicator")
st.caption(
    "OBV measures cumulative buying and selling pressure. "
    "OBV summarizes whether recorded volume occurred on up or down sessions. "
    "It is a descriptive indicator and does not identify institutional traders or establish a cause."
)

fig_obv = go.Figure()

fig_obv.add_trace(go.Scatter(
    x=obv_df['date'], y=obv_df['obv'],
    mode='lines', name='On-Balance Volume (OBV)',
    line=dict(color='#008751', width=2.0),
    hovertemplate="<b>Date</b>: %{x|%d %b %Y}<br><b>OBV</b>: %{y:,.0f}<extra></extra>"
))

fig_obv.add_trace(go.Scatter(
    x=obv_df['date'], y=obv_df['obv_sma_20'],
    mode='lines', name='OBV 20-Day Trend',
    line=dict(color='#D4AF37', width=1.5, dash='dash'),
    hovertemplate="OBV 20D SMA: %{y:,.0f}<extra></extra>"
))

fig_obv.update_layout(
    height=400, template="plotly_white",
    margin=dict(l=20, r=20, t=30, b=20),
    xaxis=dict(showgrid=True, gridcolor="#F1F5F9"),
    yaxis=dict(title="Cumulative OBV", showgrid=True, gridcolor="#F1F5F9"),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    hovermode="x unified"
)
st.plotly_chart(fig_obv, width="stretch")

st.write("---")

# ------------------------------------------------------------------------------
# 7. SECTION 4: VOLUME ON UP-DAYS VS DOWN-DAYS & TOP VOLUME SPIKES
# ------------------------------------------------------------------------------
st.markdown("### Volume Asymmetry & Record Trading Days")

col_asym, col_top = st.columns([1, 1.2])

with col_asym:
    st.markdown("#### Up-Days vs. Down-Days Participation")
    
    v_clean = v_df.copy()
    v_clean['daily_ret'] = v_clean['daily_return']
    up_days = v_clean[v_clean['daily_ret'] > 0]['volume']
    down_days = v_clean[v_clean['daily_ret'] < 0]['volume']

    avg_up_vol = up_days.mean()
    avg_down_vol = down_days.mean()
    ratio = avg_up_vol / avg_down_vol if avg_down_vol > 0 else 1.0

    fig_box = go.Figure()
    fig_box.add_trace(go.Bar(
        x=['Up Days (Gains)', 'Down Days (Losses)'],
        y=[avg_up_vol, avg_down_vol],
        marker_color=['#008751', '#DC2626'],
        text=[f"{avg_up_vol:,.0f}", f"{avg_down_vol:,.0f}"],
        textposition='outside'
    ))
    fig_box.update_layout(
        height=340, template="plotly_white",
        margin=dict(l=20, r=20, t=30, b=20),
        yaxis=dict(title="Average Volume per Session", showgrid=True, gridcolor="#F1F5F9"),
        showlegend=False
    )
    st.plotly_chart(fig_box, width="stretch")

    st.markdown(f"""
    <div style="background:#F8FAFC; border:1px solid #E2E8F0; padding:12px; border-radius:8px; font-size:0.9rem;">
        <b>Up/Down Volume Ratio:</b> <span style="color:#008751; font-weight:800;">{ratio:.2f}x</span><br>
        <span style="color:#64748B;">
        {"Recorded volume averages are higher on advancing sessions." if ratio > 1.0 else "Recorded volume averages are higher on declining sessions."}
        </span>
    </div>
    """, unsafe_allow_html=True)

with col_top:
    st.markdown("#### Top 10 Heaviest Volume Trading Days")
    st.dataframe(top_volume_table, hide_index=True, width="stretch")
    st.caption("Displays the largest recorded volume observations. Aggregate index volume does not identify trader type.")
