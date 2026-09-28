"""
================================================================================
MODULE 04: TECHNICAL & TIME-SERIES ANALYSIS
Created by: OPEYEMI SAMSON IROKOSU
PURPOSE:
- Multi-horizon Moving Averages (SMA 20, 50, 200, EMA 12, 26).
- Momentum Indicators: Relative Strength Index (RSI-14) with overbought/oversold bands.
- Moving Average Convergence Divergence (MACD) with signal line & histogram.
- Day-of-Week & Month-of-Year Calendar Seasonality.
================================================================================
"""

import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

from backend.data_loader import load_clean_data
from backend.calculations import (
    calculate_moving_averages,
    calculate_rsi,
    calculate_macd,
    calculate_seasonality
)

# ------------------------------------------------------------------------------
# 1. PAGE SETUP
# ------------------------------------------------------------------------------
st.set_page_config(
    page_title="Technical Analysis | NSE ASI Hub",
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

ma_df = calculate_moving_averages(df)
rsi_series = calculate_rsi(df, window=14)
macd_df = calculate_macd(df)
seasonality = calculate_seasonality(df)

latest_close = df['close'].iloc[-1]
latest_sma20 = ma_df['sma_20'].iloc[-1]
latest_sma50 = ma_df['sma_50'].iloc[-1]
latest_sma200 = ma_df['sma_200'].iloc[-1]
latest_rsi = rsi_series.iloc[-1]
latest_macd = macd_df['macd'].iloc[-1]
latest_signal = macd_df['signal'].iloc[-1]
latest_hist = macd_df['hist'].iloc[-1]

# ------------------------------------------------------------------------------
# 3. HEADER BANNER
# ------------------------------------------------------------------------------
st.markdown("""
<div class="page-header">
    <div class="page-title"> Time-Series & Technical Analysis</div>
    <div class="page-subtitle">
        Moving-average and momentum indicators (RSI, MACD), with descriptive calendar-seasonality summaries for the ASI.
    </div>
</div>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# 4. SECTION 1: TECHNICAL STATUS SNAPSHOT
# ------------------------------------------------------------------------------
st.markdown("### Technical Indicator Status (Current Regime)")

c1, c2, c3, c4, c5 = st.columns(5)

with c1:
    vs_200 = ((latest_close - latest_sma200) / latest_sma200) * 100.0
    c_color = "#008751" if vs_200 >= 0 else "#DC2626"
    c_label = "Bullish Regime" if vs_200 >= 0 else "Bearish Regime"
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-title">Trend vs SMA 200</div>
        <div class="stat-value" style="color:{c_color};">{vs_200:+.2f}%</div>
        <div class="stat-sub">{c_label}</div>
    </div>""", unsafe_allow_html=True)

with c2:
    vs_50 = ((latest_close - latest_sma50) / latest_sma50) * 100.0
    st.markdown(f"""
    <div class="stat-card gold">
        <div class="stat-title">Close vs SMA 50</div>
        <div class="stat-value">{vs_50:+.2f}%</div>
        <div class="stat-sub">Medium-term Momentum</div>
    </div>""", unsafe_allow_html=True)

with c3:
    cross_label = "Golden Cross (Bullish)" if latest_sma50 > latest_sma200 else "Death Cross (Bearish)"
    cross_color = "#008751" if latest_sma50 > latest_sma200 else "#DC2626"
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-title">50 / 200 Cross</div>
        <div class="stat-value" style="color:{cross_color}; font-size:1.15rem;">{cross_label}</div>
        <div class="stat-sub">50 SMA: {latest_sma50:,.0f} | 200: {latest_sma200:,.0f}</div>
    </div>""", unsafe_allow_html=True)

with c4:
    rsi_state = "Overbought" if latest_rsi >= 70 else ("Oversold" if latest_rsi <= 30 else "Neutral")
    rsi_color = "#DC2626" if latest_rsi >= 70 else ("#008751" if latest_rsi <= 30 else "#D4AF37")
    st.markdown(f"""
    <div class="stat-card gold">
        <div class="stat-title">RSI (14-Day)</div>
        <div class="stat-value" style="color:{rsi_color};">{latest_rsi:.1f}</div>
        <div class="stat-sub">Condition: {rsi_state}</div>
    </div>""", unsafe_allow_html=True)

with c5:
    macd_bias = "Bullish Momentum" if latest_hist > 0 else "Bearish Momentum"
    macd_color = "#008751" if latest_hist > 0 else "#DC2626"
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-title">MACD Histogram</div>
        <div class="stat-value" style="color:{macd_color}; font-size:1.25rem;">{latest_hist:+.2f}</div>
        <div class="stat-sub">{macd_bias}</div>
    </div>""", unsafe_allow_html=True)

st.write("---")

# ------------------------------------------------------------------------------
# 5. SECTION 2: INTERACTIVE PRICE & MOVING AVERAGES CHART
# ------------------------------------------------------------------------------
st.markdown("### Price Trend with Moving Average Envelopes")
st.caption("Toggle moving average traces via the interactive legend to inspect specific market regimes.")

fig_ma = go.Figure()

# Closing price
fig_ma.add_trace(go.Scatter(
    x=df['date'], y=df['close'],
    mode='lines', name='NSE ASI Close',
    line=dict(color='#064E3B', width=2.0),
    hovertemplate="<b>Date</b>: %{x|%d %b %Y}<br><b>Close</b>: %{y:,.2f} pts<extra></extra>"
))

# SMA 20
fig_ma.add_trace(go.Scatter(
    x=df['date'], y=ma_df['sma_20'],
    mode='lines', name='SMA 20 (Short-term)',
    line=dict(color='#F59E0B', width=1.5),
    hovertemplate="SMA 20: %{y:,.2f}<extra></extra>"
))

# SMA 50
fig_ma.add_trace(go.Scatter(
    x=df['date'], y=ma_df['sma_50'],
    mode='lines', name='SMA 50 (Medium-term)',
    line=dict(color='#10B981', width=1.8),
    hovertemplate="SMA 50: %{y:,.2f}<extra></extra>"
))

# SMA 200
fig_ma.add_trace(go.Scatter(
    x=df['date'], y=ma_df['sma_200'],
    mode='lines', name='SMA 200 (Long-term / Trend Filter)',
    line=dict(color='#D4AF37', width=2.2),
    hovertemplate="SMA 200: %{y:,.2f}<extra></extra>"
))

fig_ma.update_layout(
    height=480, template="plotly_white",
    margin=dict(l=20, r=20, t=30, b=20),
    xaxis=dict(showgrid=True, gridcolor="#F1F5F9", rangeslider=dict(visible=True, thickness=0.05)),
    yaxis=dict(title="Index Points", showgrid=True, gridcolor="#F1F5F9"),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    hovermode="x unified"
)

st.plotly_chart(fig_ma, width="stretch")

st.write("---")

# ------------------------------------------------------------------------------
# 6. SECTION 3: MOMENTUM OSCILLATORS (RSI & MACD)
# ------------------------------------------------------------------------------
st.markdown("### Momentum Oscillators: RSI (14) & MACD")

col_osc1, col_osc2 = st.columns(2)

with col_osc1:
    st.markdown("#### Relative Strength Index (RSI-14)")
    st.caption("Overbought line at 70 (red), Oversold line at 30 (green), Centerline at 50.")

    fig_rsi = go.Figure()
    fig_rsi.add_trace(go.Scatter(
        x=df['date'], y=rsi_series,
        mode='lines', name='RSI 14',
        line=dict(color='#008751', width=1.6),
        hovertemplate="RSI 14: %{y:.1f}<extra></extra>"
    ))
    fig_rsi.add_hline(y=70, line_dash="dash", line_color="#DC2626", annotation_text="Overbought (70)")
    fig_rsi.add_hline(y=30, line_dash="dash", line_color="#008751", annotation_text="Oversold (30)")
    fig_rsi.add_hline(y=50, line_dash="dot", line_color="#64748B")

    fig_rsi.update_layout(
        height=350, template="plotly_white",
        margin=dict(l=20, r=20, t=25, b=20),
        xaxis=dict(showgrid=True, gridcolor="#F1F5F9"),
        yaxis=dict(title="RSI Level", range=[10, 95], showgrid=True, gridcolor="#F1F5F9"),
        showlegend=False
    )
    st.plotly_chart(fig_rsi, width="stretch")

with col_osc2:
    st.markdown("#### MACD (12, 26, 9)")
    st.caption("MACD Line (Gold), Signal Line (Slate), Histogram (Green/Red bars).")

    fig_macd = go.Figure()

    # Histogram
    hist_colors = ['#008751' if val >= 0 else '#DC2626' for val in macd_df['hist']]
    fig_macd.add_trace(go.Bar(
        x=macd_df['date'], y=macd_df['hist'],
        name='Histogram', marker_color=hist_colors,
        hovertemplate="Histogram: %{y:+.2f}<extra></extra>"
    ))
    # MACD Line
    fig_macd.add_trace(go.Scatter(
        x=macd_df['date'], y=macd_df['macd'],
        mode='lines', name='MACD (12,26)',
        line=dict(color='#D4AF37', width=1.6),
        hovertemplate="MACD: %{y:,.2f}<extra></extra>"
    ))
    # Signal Line
    fig_macd.add_trace(go.Scatter(
        x=macd_df['date'], y=macd_df['signal'],
        mode='lines', name='Signal (9)',
        line=dict(color='#1E293B', width=1.4, dash='dot'),
        hovertemplate="Signal: %{y:,.2f}<extra></extra>"
    ))

    fig_macd.update_layout(
        height=350, template="plotly_white",
        margin=dict(l=20, r=20, t=25, b=20),
        xaxis=dict(showgrid=True, gridcolor="#F1F5F9"),
        yaxis=dict(title="Value", showgrid=True, gridcolor="#F1F5F9"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig_macd, width="stretch")

st.write("---")

# ------------------------------------------------------------------------------
# 7. SECTION 4: CALENDAR SEASONALITY & MARKET ANOMALIES
# ------------------------------------------------------------------------------
st.markdown("### Calendar Seasonality & Market Anomalies")
st.caption(
    "Descriptive summaries of daily returns by weekday and monthly close-to-close returns by calendar month. "
    "Historical averages do not establish a repeatable trading edge."
)

col_cal1, col_cal2 = st.columns([1, 1.2])

with col_cal1:
    st.markdown("#### Day-of-the-Week Effect")
    dow_df = seasonality['dow_df']

    fig_dow = go.Figure()
    bar_cols = ['#008751' if r >= 0 else '#DC2626' for r in dow_df['Avg Return (%)']]
    fig_dow.add_trace(go.Bar(
        x=dow_df['Day'], y=dow_df['Avg Return (%)'],
        marker_color=bar_cols,
        text=dow_df['Avg Return (%)'].apply(lambda x: f"{x:+.3f}%"),
        textposition='outside',
        hovertemplate="<b>%{x}</b><br>Avg Return: %{y:+.3f}%<extra></extra>"
    ))
    fig_dow.update_layout(
        height=330, template="plotly_white",
        margin=dict(l=20, r=20, t=25, b=20),
        xaxis=dict(title="Day of Week", showgrid=False),
        yaxis=dict(title="Mean Return (%)", showgrid=True, gridcolor="#F1F5F9"),
        showlegend=False
    )
    st.plotly_chart(fig_dow, width="stretch")

    st.dataframe(dow_df, hide_index=True, width="stretch")

with col_cal2:
    st.markdown("#### Monthly Seasonality (Mean Calendar-Month Return by Month)")
    m_df = seasonality['monthly_df']

    fig_m = go.Figure()
    m_cols = ['#008751' if r >= 0 else '#DC2626' for r in m_df['avg_return']]
    fig_m.add_trace(go.Bar(
        x=m_df['month_name'], y=m_df['avg_return'],
        marker_color=m_cols,
        text=m_df['avg_return'].apply(lambda x: f"{x:+.2f}%"),
        textposition='outside',
        hovertemplate="<b>%{x}</b><br>Avg Return: %{y:+.3f}%<br>Win Rate: %{customdata:.1f}%<extra></extra>",
        customdata=m_df['win_rate']
    ))
    fig_m.update_layout(
        height=330, template="plotly_white",
        margin=dict(l=20, r=20, t=25, b=20),
        xaxis=dict(title="Month of Year", showgrid=False),
        yaxis=dict(title="Mean Return (%)", showgrid=True, gridcolor="#F1F5F9"),
        showlegend=False
    )
    st.plotly_chart(fig_m, width="stretch")
    st.caption("Each observation is a month-end close-to-close return. January 2012 is excluded because the prior month-end is outside the dataset; these historical averages are descriptive, not a forecast.")

    st.dataframe(
        m_df.rename(columns={
            'month_name': 'Month',
            'avg_return': 'Avg Return (%)',
            'median_return': 'Median (%)',
            'win_rate': 'Win Rate (%)',
            'count': 'Observations'
        })[['Month', 'Avg Return (%)', 'Median (%)', 'Win Rate (%)', 'Observations']],
        hide_index=True,
        width="stretch"
    )
