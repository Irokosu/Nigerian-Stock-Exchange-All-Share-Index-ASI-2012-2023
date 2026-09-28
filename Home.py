"""
================================================================================
NSE ASI FINANCIAL INTELLIGENCE & QUANTITATIVE ANALYTICS PLATFORM
Main Application Entry & Executive Landing Portal
Created by: OPEYEMI SAMSON IROKOSU
================================================================================
"""

import streamlit as st
import plotly.graph_objects as go
from backend.data_loader import load_clean_data, get_market_summary
from backend.calculations import get_max_drawdown_stats

# ------------------------------------------------------------------------------
# 1. PAGE CONFIGURATION
# ------------------------------------------------------------------------------
st.set_page_config(
    page_title="NSE ASI Intelligence Hub | Opeyemi Samson Irokosu",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ------------------------------------------------------------------------------
# 2. CUSTOM CSS STYLING (Emerald & Champagne Gold Theme - No Generic Blue)
# ------------------------------------------------------------------------------
st.markdown("""
<style>
    /* Emerald & Gold Theme Variables */
    :root {
        --nse-emerald: #008751;
        --nse-mint: #10B981;
        --nse-dark-pine: #064E3B;
        --nse-gold: #D4AF37;
        --nse-amber: #F59E0B;
        --nse-slate: #1E293B;
        --nse-light-bg: #F8FAFC;
    }

    /* Hero Banner Card */
    .hero-container {
        background: linear-gradient(135deg, #064E3B 0%, #008751 60%, #0F5132 100%);
        border: 2px solid #D4AF37;
        border-radius: 16px;
        padding: 35px 30px;
        margin-bottom: 25px;
        box-shadow: 0 10px 25px rgba(0, 135, 81, 0.15);
        color: white;
    }

    /* BIG, BOLD Attribution */
    .hero-author-badge {
        display: inline-block;
        background-color: rgba(212, 175, 55, 0.18);
        border: 1.5px solid #D4AF37;
        color: #FDE047;
        padding: 8px 20px;
        border-radius: 30px;
        font-size: 1.25rem;
        font-weight: 800;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-bottom: 15px;
        box-shadow: 0 4px 12px rgba(212, 175, 55, 0.2);
    }

    .hero-title {
        font-size: 2.5rem;
        font-weight: 900;
        color: #FFFFFF;
        margin-bottom: 8px;
        letter-spacing: -0.5px;
    }

    .hero-subtitle {
        font-size: 1.15rem;
        color: #E2E8F0;
        max-width: 900px;
        line-height: 1.6;
    }

    /* KPI Summary Cards */
    .kpi-card {
        background: white;
        border-radius: 12px;
        padding: 20px;
        border-left: 5px solid #008751;
        border-top: 1px solid #E2E8F0;
        border-right: 1px solid #E2E8F0;
        border-bottom: 1px solid #E2E8F0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        margin-bottom: 15px;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .kpi-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 15px rgba(0, 135, 81, 0.1);
    }
    .kpi-title {
        font-size: 0.85rem;
        font-weight: 700;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .kpi-value {
        font-size: 1.85rem;
        font-weight: 800;
        color: #064E3B;
        margin: 5px 0;
    }
    .kpi-sub {
        font-size: 0.82rem;
        color: #10B981;
        font-weight: 600;
    }

    /* Project Directory Module Cards */
    .module-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-top: 4px solid #D4AF37;
        border-radius: 12px;
        padding: 22px;
        height: 100%;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.03);
        transition: all 0.2s ease-in-out;
    }
    .module-card:hover {
        border-top: 4px solid #008751;
        box-shadow: 0 8px 18px rgba(0, 135, 81, 0.12);
        transform: translateY(-3px);
    }
    .module-num {
        font-size: 0.85rem;
        font-weight: 800;
        color: #D4AF37;
        letter-spacing: 1.5px;
        text-transform: uppercase;
    }
    .module-heading {
        font-size: 1.2rem;
        font-weight: 800;
        color: #1E293B;
        margin: 6px 0 10px 0;
    }
    .module-desc {
        font-size: 0.92rem;
        color: #475569;
        line-height: 1.5;
    }

    /* Sidebar Customization */
    [data-testid="stSidebar"] {
        background-color: #064E3B;
    }
    [data-testid="stSidebar"] * {
        color: #FFFFFF !important;
    }
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# 3. LOAD DATA & METRICS
# ------------------------------------------------------------------------------
try:
    df = load_clean_data()
    summary = get_market_summary(df)
    mdd_summary = get_max_drawdown_stats(df)
except Exception as e:
    st.error(f"Error loading dataset: {e}")
    st.stop()

# ------------------------------------------------------------------------------
# 4. HERO SECTION WITH PROMINENT ATTRIBUTION
# ------------------------------------------------------------------------------
st.markdown(f"""
<div class="hero-container">
    <div class="hero-author-badge">
       CREATED BY OPEYEMI SAMSON IROKOSU
    </div>
    <div class="hero-title">Nigerian Stock Exchange (NSE) All-Share Index</div>
    <div class="hero-subtitle">
        ASI Analytics, Econometric Properties & Quantitative Strategy Dashboard 
        tracking <b>{summary['total_trading_days']:,} trading days</b> across nearly 12 years 
        (<b>{summary['start_date'].strftime('%b %d, %Y')} - {summary['end_date'].strftime('%b %d, %Y')}</b>).
    </div>
</div>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# 5. LIFETIME EXECUTIVE MARKET METRICS
# ------------------------------------------------------------------------------
st.markdown("### Lifetime Market Performance Snapshot")

c1, c2, c3, c4, c5 = st.columns(5)

with c1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">Current Index Level</div>
        <div class="kpi-value">{summary['end_close']:,.2f}</div>
        <div class="kpi-sub">Baseline: {summary['start_close']:,.2f}</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="kpi-card" style="border-left-color: #D4AF37;">
        <div class="kpi-title">ASI Price Return</div>
        <div class="kpi-value" style="color: #008751;">+{summary['total_return_pct']}%</div>
        <div class="kpi-sub">Price change over {summary['total_calendar_years']} years; excludes dividends and costs</div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">Annualized Price Growth (CAGR)</div>
        <div class="kpi-value">+{summary['cagr_pct']}%</div>
        <div class="kpi-sub">Compounded Yearly Growth</div>
    </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown(f"""
    <div class="kpi-card" style="border-left-color: #D4AF37;">
        <div class="kpi-title">All-Time Peak (High)</div>
        <div class="kpi-value">{summary['all_time_high']:,.2f}</div>
        <div class="kpi-sub">{summary['ath_date'].strftime('%b %d, %Y')}</div>
    </div>
    """, unsafe_allow_html=True)

with c5:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">All-Time Cycle Low</div>
        <div class="kpi-value">{summary['all_time_low']:,.2f}</div>
        <div class="kpi-sub">{summary['atl_date'].strftime('%b %d, %Y')}</div>
    </div>
    """, unsafe_allow_html=True)

st.write("")

# ------------------------------------------------------------------------------
# 6. EXECUTIVE MACRO TRAJECTORY CHART
# ------------------------------------------------------------------------------
st.markdown("### NSE ASI Macro Trajectory & Historical Regimes (2012 - 2023)")
st.caption("Interactive historical view. Use the range slider below the chart to zoom into specific eras.")

fig = go.Figure()

# Main Index Area Curve (Emerald Green theme)
fig.add_trace(go.Scatter(
    x=df['date'],
    y=df['close'],
    mode='lines',
    name='NSE ASI Close',
    line=dict(color='#008751', width=2.2),
    fill='tozeroy',
    fillcolor='rgba(0, 135, 81, 0.08)',
    hovertemplate="<b>Date</b>: %{x|%b %d, %Y}<br><b>Index Level</b>: %{y:,.2f} pts<extra></extra>"
))

# Markers derived from observed index prices
milestones = [
    (df['date'].iloc[0], summary['start_close'], "2012 Baseline", "top right"),
    (mdd_summary['peak_date'], mdd_summary['peak_val'], "Maximum Drawdown Peak (Close)", "bottom right"),
    (mdd_summary['trough_date'], mdd_summary['trough_val'], "Maximum Drawdown Trough (Close)", "top right"),
    (summary['ath_date'], summary['all_time_high'], "All-Time Intraday High", "top left")
]

for m_date, m_val, m_text, pos in milestones:
    fig.add_annotation(
        x=m_date,
        y=m_val,
        text=f"<b>{m_text}</b>",
        showarrow=True,
        arrowhead=2,
        arrowsize=1,
        arrowwidth=1.5,
        arrowcolor='#D4AF37',
        ax=0,
        ay=-35 if "top" in pos else 35,
        bgcolor="#064E3B",
        bordercolor="#D4AF37",
        borderwidth=1,
        font=dict(color="#FFFFFF", size=10)
    )

fig.update_layout(
    height=480,
    margin=dict(l=20, r=20, t=30, b=20),
    template="plotly_white",
    xaxis=dict(
        title="",
        showgrid=True,
        gridcolor="#F1F5F9",
        rangeslider=dict(visible=True, thickness=0.06, bgcolor="#F8FAFC")
    ),
    yaxis=dict(
        title="Index Points",
        showgrid=True,
        gridcolor="#F1F5F9",
        tickformat=","
    ),
    hovermode="x unified"
)

st.plotly_chart(fig, width="stretch")

st.write("")

# ------------------------------------------------------------------------------
# 7. INTERACTIVE MODULE DIRECTORY
# ------------------------------------------------------------------------------
st.markdown("### Master Analytics Directory")
st.markdown("Select any specialized analytical module from the **sidebar navigation** on the left:")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="module-card">
        <div class="module-num">MODULE 01</div>
        <div class="module-heading"> Return & Performance Analysis</div>
        <div class="module-desc">
            Compound Annual Growth Rate (CAGR), rolling annualized returns, annual calendar return heatmaps, 
            and growth simulation of a hypothetical NGN 100,000 investment over 11 years.
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.write("")
    st.markdown("""
    <div class="module-card">
        <div class="module-num">MODULE 04</div>
        <div class="module-heading"> Time-Series & Technical Analysis</div>
        <div class="module-desc">
            Interactive OHLC candlestick charting, Simple & Exponential Moving Averages (20/50/200), 
            RSI momentum, MACD oscillators, and calendar seasonality patterns.
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="module-card">
        <div class="module-num">MODULE 02</div>
        <div class="module-heading"> Risk & Volatility Analysis</div>
        <div class="module-desc">
            Rolling historical volatility, peak-to-trough underwater drawdown curves, 
            historical and parametric Value at Risk (VaR 95%/99%), and Expected Shortfall (CVaR).
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.write("")
    st.markdown("""
    <div class="module-card">
        <div class="module-num">MODULE 05</div>
        <div class="module-heading"> Price-Volume Dynamics</div>
        <div class="module-desc">
            Market liquidity trends, volume-return elasticity, turnover velocity, 
            and algorithmic detection of high-volume price breakout days.
        </div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="module-card">
        <div class="module-num">MODULE 03</div>
        <div class="module-heading"> Statistical & Distributional Properties</div>
        <div class="module-desc">
            Empirical return distribution vs. theoretical Gaussian curve, skewness, kurtosis 
            (fat-tail risk), Augmented Dickey-Fuller stationarity tests, and autocorrelation (ACF/PACF).
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.write("")
    st.markdown("""
    <div class="module-card">
        <div class="module-num">MODULE 06</div>
        <div class="module-heading"> Quantitative Modeling & Backtesting</div>
        <div class="module-desc">
            Market regime segmentation (Bull, Bear, and Volatile states), algorithmic dual-moving 
            average crossover backtesting, and Sharpe/Sortino performance summaries.
        </div>
    </div>
    """, unsafe_allow_html=True)

st.write("")
st.write("")

# ------------------------------------------------------------------------------
# 8. DATA METHODOLOGY EXPANDER
# ------------------------------------------------------------------------------
with st.expander("Data Provenance, Cleansing Standards & Methodology Summary"):
    st.markdown("""
    - **Source Asset**: Nigerian Stock Exchange (NSE) All-Share Index (ASI).
    - **Total Observations**: 2,948 recorded trading sessions from January 30, 2012, to December 22, 2023.
    - **Data Pipeline Operations**:
        1. *Delimiter Resolution*: Transformed raw semicolon-delimited feed with embedded currency formatting into standard ISO records.
        2. *Currency & Numerical Parsing*: Stripped encoding artifacts (`?`) and thousand comma separators, converting raw strings to standard `float64`.
        3. *Returns & Percentage Parsing*: Converted literal `%` characters to numeric percentages.
        4. *Chronological Sorting*: Reordered from raw reverse-chronological order to strict ascending chronological time-series format.
        5. *Imputation*: Missing opening price artifact on 2014-07-24 mathematically recovered using intraday price ratio formulas.
    """)

# ------------------------------------------------------------------------------
# 9. SIDEBAR METADATA
# ------------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### NSE ASI Hub")
    st.markdown("**Lead Creator:**")
    st.markdown("##### Opeyemi Samson Irokosu")
    st.markdown("---")
    st.markdown("### Dataset Overview")
    st.markdown(f"- **Days**: {summary['total_trading_days']:,} trading sessions")
    st.markdown(f"- **Start**: {summary['start_date'].strftime('%d %b %Y')}")
    st.markdown(f"- **End**: {summary['end_date'].strftime('%d %b %Y')}")
    st.markdown(f"- **CAGR**: +{summary['cagr_pct']}%")
    st.markdown(f"- **Max Gain (1D)**: +{summary['best_single_day']:.2f}%")
    st.markdown(f"- **Max Loss (1D)**: {summary['worst_single_day']:.2f}%")
