"""
================================================================================
MODULE 03: STATISTICAL & DISTRIBUTIONAL PROPERTIES
Created by: OPEYEMI SAMSON IROKOSU
PURPOSE:
- Empirical return distribution profile (skewness, kurtosis, fat tails).
- Normality testing via Jarque-Bera.
- ADF stationarity tests on price vs. returns.
- ACF & PACF market memory and autocorrelation analysis.
================================================================================
"""

import streamlit as st
import plotly.graph_objects as go
import numpy as np
import pandas as pd
from scipy import stats

from backend.data_loader import load_clean_data
from backend.calculations import (
    calculate_descriptive_stats,
    run_adf_test,
    calculate_acf_pacf
)

# ------------------------------------------------------------------------------
# 1. PAGE SETUP
# ------------------------------------------------------------------------------
st.set_page_config(
    page_title="Statistical Properties | NSE ASI Hub",
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
    .stat-value { font-size: 1.4rem; font-weight: 800; color: #064E3B; margin: 4px 0; }
    .stat-sub   { font-size: 0.8rem; color: #64748B; }

    .adf-box {
        background: #F8FAFC; border: 1px solid #E2E8F0;
        border-radius: 10px; padding: 18px; margin-bottom: 14px;
    }
    .adf-title { font-size: 1rem; font-weight: 800; color: #1E293B; margin-bottom: 10px; }
    .verdict-pass { color: #008751; font-weight: 800; font-size: 1.1rem; }
    .verdict-fail { color: #DC2626; font-weight: 800; font-size: 1.1rem; }

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
    <div class="page-title"> Statistical & Distributional Properties</div>
    <div class="page-subtitle">
        Empirical return distribution profiling, Gaussian normality testing, 
        ADF stationarity analysis, and autocorrelation structure (ACF/PACF) 
        of the Nigerian Stock Exchange All-Share Index.
    </div>
</div>
""", unsafe_allow_html=True)

# Pre-compute
desc_stats = calculate_descriptive_stats(df)
adf_result = run_adf_test(df)
acf_data   = calculate_acf_pacf(df, nlags=30)

returns_pct = desc_stats['returns_pct']

# ------------------------------------------------------------------------------
# 4. SECTION 1: DESCRIPTIVE STATISTICS KPI CARDS
# ------------------------------------------------------------------------------
st.markdown("### Distributional Shape Summary")

k1, k2, k3, k4, k5, k6 = st.columns(6)

with k1:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-title">Mean Daily Return</div>
        <div class="stat-value">+{desc_stats['mean']:.4f}%</div>
        <div class="stat-sub">Average daily gain</div>
    </div>""", unsafe_allow_html=True)

with k2:
    st.markdown(f"""
    <div class="stat-card gold">
        <div class="stat-title">Std. Deviation</div>
        <div class="stat-value">{desc_stats['std']:.4f}%</div>
        <div class="stat-sub">Daily return spread</div>
    </div>""", unsafe_allow_html=True)

with k3:
    skew_color = "#008751" if desc_stats['skewness'] > 0 else "#DC2626"
    skew_label = "Right-skewed (positive tail)" if desc_stats['skewness'] > 0 else "Left-skewed (negative tail)"
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-title">Skewness</div>
        <div class="stat-value" style="color:{skew_color};">{desc_stats['skewness']:.4f}</div>
        <div class="stat-sub">{skew_label}</div>
    </div>""", unsafe_allow_html=True)

with k4:
    kurt_label = "Heavy tails (Leptokurtic)" if desc_stats['kurtosis'] > 0 else "Thin tails (Platykurtic)"
    st.markdown(f"""
    <div class="stat-card red">
        <div class="stat-title">Excess Kurtosis</div>
        <div class="stat-value" style="color:#DC2626;">{desc_stats['kurtosis']:.4f}</div>
        <div class="stat-sub">{kurt_label}</div>
    </div>""", unsafe_allow_html=True)

with k5:
    st.markdown(f"""
    <div class="stat-card gold">
        <div class="stat-title">Best Single Day</div>
        <div class="stat-value" style="color:#008751;">+{desc_stats['max']:.2f}%</div>
        <div class="stat-sub">Largest daily gain</div>
    </div>""", unsafe_allow_html=True)

with k6:
    st.markdown(f"""
    <div class="stat-card red">
        <div class="stat-title">Worst Single Day</div>
        <div class="stat-value" style="color:#DC2626;">{desc_stats['min']:.2f}%</div>
        <div class="stat-sub">Largest daily loss</div>
    </div>""", unsafe_allow_html=True)

st.write("---")

# ------------------------------------------------------------------------------
# 5. SECTION 2: RETURN DISTRIBUTION + NORMAL OVERLAY + QQ PLOT
# ------------------------------------------------------------------------------
st.markdown("### Empirical Return Distribution vs. Theoretical Normal")

col_dist1, col_dist2 = st.columns([1.3, 1])

with col_dist1:
    st.markdown("#### Return Histogram with Gaussian Fit")
    st.caption(
        "The NSE ASI daily returns show **positive skewness** (+0.45) and "
        "**excess kurtosis** (+6.08), meaning fatter tails and more extreme events "
        "than a Normal distribution would predict."
    )

    mu    = returns_pct.mean()
    sigma = returns_pct.std()
    x_fit = np.linspace(returns_pct.min(), returns_pct.max(), 400)
    y_fit = stats.norm.pdf(x_fit, mu, sigma)

    fig_hist = go.Figure()
    fig_hist.add_trace(go.Histogram(
        x=returns_pct, nbinsx=80,
        histnorm='probability density',
        name='Empirical Returns',
        marker_color='rgba(0, 135, 81, 0.5)',
        marker_line=dict(color='#008751', width=0.4)
    ))
    fig_hist.add_trace(go.Scatter(
        x=x_fit, y=y_fit, mode='lines',
        name='Normal Distribution',
        line=dict(color='#D4AF37', width=2.5, dash='dash')
    ))

    # Jarque-Bera result annotation
    jb_verdict = " Normal (p > 0.05)" if desc_stats['is_normal'] else " Not Normal (p < 0.05)"
    fig_hist.add_annotation(
        x=0.99, y=0.97, xref="paper", yref="paper",
        text=f"<b>Jarque-Bera Test</b><br>Stat: {desc_stats['jb_stat']:,.2f}<br>p-value: {desc_stats['jb_p']:.2e}<br>{jb_verdict}",
        showarrow=False, align="right",
        bgcolor="#064E3B", bordercolor="#D4AF37",
        font=dict(color="white", size=10), borderwidth=1
    )

    fig_hist.update_layout(
        height=400, template="plotly_white",
        margin=dict(l=20, r=20, t=30, b=20),
        xaxis=dict(title="Daily Return (%)", showgrid=True, gridcolor="#F1F5F9"),
        yaxis=dict(title="Probability Density", showgrid=True, gridcolor="#F1F5F9"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        barmode='overlay'
    )
    st.plotly_chart(fig_hist, width="stretch")

with col_dist2:
    st.markdown("#### Quantile-Quantile (QQ) Plot")
    st.caption(
        "A QQ plot compares actual return quantiles against a perfect Normal distribution. "
        "Deviations at the extremes (S-shaped curve) confirm **fat tails** and **non-normality**."
    )

    # Theoretical and sample quantiles
    (osm, osr), (slope, intercept, r) = stats.probplot(returns_pct, dist="norm")

    fig_qq = go.Figure()

    # QQ Points
    fig_qq.add_trace(go.Scatter(
        x=osm, y=osr, mode='markers',
        name='Return Quantiles',
        marker=dict(color='#008751', size=4, opacity=0.7)
    ))
    # Perfect Normal reference line
    x_line = np.array([min(osm), max(osm)])
    fig_qq.add_trace(go.Scatter(
        x=x_line, y=slope * x_line + intercept,
        mode='lines', name='Normal Reference',
        line=dict(color='#D4AF37', width=2, dash='dash')
    ))

    fig_qq.update_layout(
        height=400, template="plotly_white",
        margin=dict(l=20, r=20, t=30, b=20),
        xaxis=dict(title="Theoretical Normal Quantiles", showgrid=True, gridcolor="#F1F5F9"),
        yaxis=dict(title="Empirical Return Quantiles", showgrid=True, gridcolor="#F1F5F9"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig_qq, width="stretch")

st.write("---")

# ------------------------------------------------------------------------------
# 6. SECTION 3: ADF STATIONARITY TESTS
# ------------------------------------------------------------------------------
st.markdown("### Augmented Dickey-Fuller (ADF) Stationarity Tests")
st.caption(
    "Stationarity is a fundamental requirement for time-series modelling. "
    "A stationary series has constant mean and variance over time. "
    "**H (Null Hypothesis)**: The series has a unit root (non-stationary). "
    "p-value < 0.05 -> Reject H -> **Stationary**."
)

col_adf1, col_adf2 = st.columns(2)

def render_adf_box(label, result):
    verdict_class = "verdict-pass" if result['is_stationary'] else "verdict-fail"
    verdict_text  = "REJECT UNIT-ROOT NULL" if result["is_stationary"] else "FAIL TO REJECT UNIT-ROOT NULL"
    return f"""
    <div class="adf-box">
        <div class="adf-title">{label}</div>
        <table style="width:100%; font-size:0.9rem; border-collapse:collapse;">
            <tr><td style="color:#64748B; padding:3px 0;">ADF Statistic</td>
                <td style="font-weight:700; text-align:right;">{result['adf_stat']:.4f}</td></tr>
            <tr><td style="color:#64748B; padding:3px 0;">p-value</td>
                <td style="font-weight:700; text-align:right;">{result['p_value']:.6f}</td></tr>
            <tr><td style="color:#64748B; padding:3px 0;">Critical Value (1%)</td>
                <td style="font-weight:700; text-align:right;">{result['critical_1']:.4f}</td></tr>
            <tr><td style="color:#64748B; padding:3px 0;">Critical Value (5%)</td>
                <td style="font-weight:700; text-align:right;">{result['critical_5']:.4f}</td></tr>
            <tr><td style="color:#64748B; padding:3px 0;">Critical Value (10%)</td>
                <td style="font-weight:700; text-align:right;">{result['critical_10']:.4f}</td></tr>
        </table>
        <div style="margin-top:12px; padding:8px; background:#F0FDF4; border-radius:6px; text-align:center;">
            <span class="{verdict_class}">{verdict_text}</span>
        </div>
    </div>"""

with col_adf1:
    st.markdown(render_adf_box(" Raw Closing Price Series", adf_result['price']), unsafe_allow_html=True)
    if adf_result['price']['is_stationary']:
        st.info("The ADF test rejects the unit-root null at the 5% level. This does not rule out structural breaks or establish constant variance.")
    else:
        st.info("The ADF test does not reject the unit-root null at the 5% level. This is not proof that a unit root is present; structural breaks and deterministic terms can affect the result.")

with col_adf2:
    st.markdown(render_adf_box(" Daily Returns Series", adf_result['returns']), unsafe_allow_html=True)
    if adf_result['returns']['is_stationary']:
        st.success("The ADF test rejects the unit-root null at the 5% level. This does not establish constant variance or guarantee stationarity under structural breaks.")
    else:
        st.warning("The ADF test does not reject the unit-root null at the 5% level. This test does not by itself identify the cause of non-stationarity.")

st.write("---")

# ------------------------------------------------------------------------------
# 7. SECTION 4: ACF & PACF
# ------------------------------------------------------------------------------
st.markdown("### Autocorrelation (ACF) & Partial Autocorrelation (PACF)")
st.caption(
    "Autocorrelation measures if today's return is correlated with past returns. "
    "Bars outside the approximate **+/-1.96/ band suggest sample autocorrelation. "
    "Scanning many lags raises multiple-testing concerns; this is not proof of a tradable edge."
)

col_acf, col_pacf = st.columns(2)

lags       = acf_data['lags'][1:]   # skip lag 0 (always 1.0)
acf_vals   = acf_data['acf'][1:]
pacf_vals  = acf_data['pacf'][1:]
conf       = acf_data['conf_band']

# ACF Colors: emerald if significant, slate if not
def bar_colors(values, conf):
    return ['#008751' if abs(v) > conf else '#94A3B8' for v in values]

with col_acf:
    st.markdown("#### Autocorrelation Function (ACF)")

    fig_acf = go.Figure()
    fig_acf.add_trace(go.Bar(
        x=lags, y=acf_vals,
        name='ACF',
        marker_color=bar_colors(acf_vals, conf),
        hovertemplate="Lag %{x}: ACF = %{y:.4f}<extra></extra>"
    ))
    # Confidence bands
    fig_acf.add_hline(y=conf,  line_dash="dash", line_color="#D4AF37", line_width=1.5)
    fig_acf.add_hline(y=-conf, line_dash="dash", line_color="#D4AF37", line_width=1.5)
    fig_acf.add_hline(y=0,     line_color="#1E293B", line_width=0.8)

    fig_acf.update_layout(
        height=370, template="plotly_white",
        margin=dict(l=20, r=20, t=30, b=20),
        xaxis=dict(title="Lag (Trading Days)", showgrid=False),
        yaxis=dict(title="Autocorrelation", showgrid=True, gridcolor="#F1F5F9",
                   range=[-0.35, 0.45]),
        showlegend=False
    )
    st.plotly_chart(fig_acf, width="stretch")
    st.caption(
        f"**Lag 1 ACF = {acf_data['acf'][1]:.4f}** - a sample estimate of first-lag autocorrelation; "
        "it does not by itself establish persistent or economically useful predictability."
    )

with col_pacf:
    st.markdown("#### Partial Autocorrelation Function (PACF)")

    fig_pacf = go.Figure()
    fig_pacf.add_trace(go.Bar(
        x=lags, y=pacf_vals,
        name='PACF',
        marker_color=bar_colors(pacf_vals, conf),
        hovertemplate="Lag %{x}: PACF = %{y:.4f}<extra></extra>"
    ))
    fig_pacf.add_hline(y=conf,  line_dash="dash", line_color="#D4AF37", line_width=1.5)
    fig_pacf.add_hline(y=-conf, line_dash="dash", line_color="#D4AF37", line_width=1.5)
    fig_pacf.add_hline(y=0,     line_color="#1E293B", line_width=0.8)

    fig_pacf.update_layout(
        height=370, template="plotly_white",
        margin=dict(l=20, r=20, t=30, b=20),
        xaxis=dict(title="Lag (Trading Days)", showgrid=False),
        yaxis=dict(title="Partial Autocorrelation", showgrid=True, gridcolor="#F1F5F9",
                   range=[-0.35, 0.45]),
        showlegend=False
    )
    st.plotly_chart(fig_pacf, width="stretch")
    st.caption(
        f"**Lag 1 PACF = {acf_data['pacf'][1]:.4f}** - a first-lag partial autocorrelation estimate. "
        "Higher-lag patterns are exploratory and should not be treated as proof of an AR(1) process."
    )
