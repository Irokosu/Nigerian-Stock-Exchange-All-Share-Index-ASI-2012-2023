"""
================================================================================
MODULE 06: QUANTITATIVE MODELING & STRATEGY BACKTESTING
Created by: OPEYEMI SAMSON IROKOSU
PURPOSE:
- Algorithmic strategy backtesting against the Nigerian Stock Exchange ASI benchmark.
- Dual Moving Average Trend-Following Strategy (Golden Cross / Death Cross).
- RSI Mean-Reversion Strategy.
- Performance metrics: CAGR, Sharpe Ratio, Sortino Ratio, Max Drawdown, Win Rate.
- Capital growth simulation & drawdown protection comparison.
================================================================================
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np

from backend.data_loader import load_clean_data
from backend.calculations import (
    backtest_ma_crossover,
    backtest_rsi_strategy
)

# ------------------------------------------------------------------------------
# 1. PAGE SETUP
# ------------------------------------------------------------------------------
st.set_page_config(
    page_title="Quantitative Modeling | NSE ASI Hub",
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

    .control-box {
        background: #F8FAFC; border: 1px solid #E2E8F0;
        border-radius: 10px; padding: 18px; margin-bottom: 20px;
    }

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
    st.error(f"Error loading dataset: {e}")
    st.stop()

# ------------------------------------------------------------------------------
# 3. HEADER BANNER
# ------------------------------------------------------------------------------
st.markdown("""
<div class="page-header">
    <div class="page-title"> Quantitative Modeling & Strategy Backtesting</div>
    <div class="page-subtitle">
        Rigorous algorithmic strategy simulation against the Nigerian Stock Exchange (NSE) ASI benchmark.
        Evaluate alpha generation, risk-adjusted Sharpe/Sortino ratios, and downside capital preservation.
    </div>
</div>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# 4. STRATEGY CONFIGURATION CONTROLS
# ------------------------------------------------------------------------------
st.markdown("### Backtest Strategy Controls")

with st.container():
    col_strat, col_p1, col_p2, col_p3 = st.columns([1.3, 1, 1, 1])

    with col_strat:
        strategy_type = st.selectbox(
            "Quantitative Model Architecture",
            ["Dual Moving Average Crossover (Trend Following)", "RSI Mean-Reversion (Oscillator)"]
        )

    with col_p1:
        initial_capital = st.number_input(
            "Initial Capital (NGN)",
            min_value=10_000.0,
            max_value=100_000_000.0,
            value=100_000.0,
            step=50_000.0,
            format="%.0f"
        )

    with col_p2:
        fee_bps = st.number_input(
            "Trading Fee / Slippage (bps)",
            min_value=0.0,
            max_value=100.0,
            value=10.0,
            step=5.0,
            help="10 bps = 0.10% transaction cost per execution"
        )
        fee_pct = fee_bps / 10_000.0

    with col_p3:
        if "Moving Average" in strategy_type:
            fast_win = st.slider("Fast Window (Days)", 10, 100, 50, step=5)
            slow_win = st.slider("Slow Window (Days)", 100, 300, 200, step=10)
        else:
            rsi_period = st.slider("RSI Lookback", 7, 30, 14)
            oversold_th = st.slider("Oversold Entry Level", 20, 45, 35)
            overbought_th = st.slider("Overbought Exit Level", 60, 85, 70)

# Run Backtest
if "Moving Average" in strategy_type:
    bt_result = backtest_ma_crossover(
        df,
        fast_window=fast_win,
        slow_window=slow_win,
        initial_capital=initial_capital,
        fee_pct=fee_pct
    )
    strat_title = f"Dual MA Crossover ({fast_win} / {slow_win} SMA)"
else:
    bt_result = backtest_rsi_strategy(
        df,
        rsi_period=rsi_period,
        oversold=oversold_th,
        overbought=overbought_th,
        initial_capital=initial_capital,
        fee_pct=fee_pct
    )
    strat_title = f"RSI Mean-Reversion ({rsi_period}D, Buy<{oversold_th}, Sell>{overbought_th})"

res_df = bt_result['data']
s_metrics = bt_result['strat_metrics']
b_metrics = bt_result['bench_metrics']
trades_count = bt_result['trades_count']

final_strat_val = res_df['strategy_portfolio'].iloc[-1]
final_bench_val = res_df['benchmark_portfolio'].iloc[-1]

st.write("---")

# ------------------------------------------------------------------------------
# 5. SECTION 1: EXECUTIVE PERFORMANCE COMPARISON
# ------------------------------------------------------------------------------
st.markdown(f"### Strategy Performance vs. Benchmark ({strat_title})")

k1, k2, k3, k4, k5 = st.columns(5)

with k1:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-title">Strategy Ending Capital</div>
        <div class="stat-value">NGN {final_strat_val:,.0f}</div>
        <div class="stat-sub">From NGN {initial_capital:,.0f}</div>
    </div>""", unsafe_allow_html=True)

with k2:
    st.markdown(f"""
    <div class="stat-card gold">
        <div class="stat-title">Benchmark Ending Capital</div>
        <div class="stat-value">NGN {final_bench_val:,.0f}</div>
        <div class="stat-sub">Buy & Hold ASI</div>
    </div>""", unsafe_allow_html=True)

with k3:
    c_diff = s_metrics['cagr'] - b_metrics['cagr']
    diff_color = "#008751" if c_diff >= 0 else "#DC2626"
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-title">Strategy CAGR</div>
        <div class="stat-value" style="color:{diff_color};">{s_metrics['cagr']:+.2f}%</div>
        <div class="stat-sub">Benchmark: {b_metrics['cagr']:+.2f}%</div>
    </div>""", unsafe_allow_html=True)

with k4:
    mdd_prot = abs(b_metrics['mdd']) - abs(s_metrics['mdd'])
    mdd_color = "#008751" if mdd_prot >= 0 else "#DC2626"
    st.markdown(f"""
    <div class="stat-card red">
        <div class="stat-title">Strategy Max Drawdown</div>
        <div class="stat-value" style="color:#DC2626;">{s_metrics['mdd']:.2f}%</div>
        <div class="stat-sub">Benchmark: {b_metrics['mdd']:.2f}%</div>
    </div>""", unsafe_allow_html=True)

with k5:
    st.markdown(f"""
    <div class="stat-card gold">
        <div class="stat-title">Sharpe Ratio</div>
        <div class="stat-value">{s_metrics['sharpe']:.2f}</div>
        <div class="stat-sub">Benchmark: {b_metrics['sharpe']:.2f} | Position changes: {trades_count}</div>
    </div>""", unsafe_allow_html=True)

st.write("---")

# ------------------------------------------------------------------------------
# 6. SECTION 2: WEALTH TRAJECTORY CHART (EQUITY CURVE)
# ------------------------------------------------------------------------------
st.markdown("### Simulated Portfolio Wealth Trajectory (Naira Growth)")
st.caption("Compares hypothetical strategy and index-price growth. Signals use closing data and positions take effect after a one-session execution delay.")
st.info("Illustrative index-price simulation: the ASI is not directly investable, and this backtest excludes dividends, taxes, market impact, financing, and execution constraints. Results are historical and do not establish future performance.")

fig_eq = go.Figure()

# Benchmark Curve
fig_eq.add_trace(go.Scatter(
    x=res_df['date'], y=res_df['benchmark_portfolio'],
    mode='lines', name='Buy & Hold Benchmark (NSE ASI)',
    line=dict(color='#64748B', width=1.8, dash='dot'),
    hovertemplate="<b>Date</b>: %{x|%d %b %Y}<br>Benchmark: NGN %{y:,.0f}<extra></extra>"
))

# Strategy Curve
fig_eq.add_trace(go.Scatter(
    x=res_df['date'], y=res_df['strategy_portfolio'],
    mode='lines', name=f'Quantitative Strategy ({strat_title})',
    line=dict(color='#008751', width=2.4),
    fill='tozeroy',
    fillcolor='rgba(0, 135, 81, 0.08)',
    hovertemplate="<b>Date</b>: %{x|%d %b %Y}<br>Strategy: NGN %{y:,.0f}<extra></extra>"
))

fig_eq.update_layout(
    height=480, template="plotly_white",
    margin=dict(l=20, r=20, t=30, b=20),
    xaxis=dict(showgrid=True, gridcolor="#F1F5F9", rangeslider=dict(visible=True, thickness=0.05)),
    yaxis=dict(title="Portfolio Value (NGN)", showgrid=True, gridcolor="#F1F5F9"),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    hovermode="x unified"
)
st.plotly_chart(fig_eq, width="stretch")

st.write("---")

# ------------------------------------------------------------------------------
# 7. SECTION 3: UNDERWATER DRAWDOWN COMPARISON
# ------------------------------------------------------------------------------
st.markdown("### Downside Capital Preservation (Drawdown Comparison)")
st.caption("Compare historical sample drawdowns. A lower observed drawdown does not establish future capital protection.")

fig_dd = go.Figure()

fig_dd.add_trace(go.Scatter(
    x=res_df['date'], y=res_df['benchmark_dd'],
    mode='lines', name='Benchmark Drawdown (%)',
    line=dict(color='#DC2626', width=1.5, dash='dot'),
    hovertemplate="Benchmark DD: %{y:.2f}%<extra></extra>"
))

fig_dd.add_trace(go.Scatter(
    x=res_df['date'], y=res_df['strategy_dd'],
    mode='lines', name='Strategy Drawdown (%)',
    line=dict(color='#008751', width=2.0),
    fill='tozeroy',
    fillcolor='rgba(0, 135, 81, 0.08)',
    hovertemplate="Strategy DD: %{y:.2f}%<extra></extra>"
))

fig_dd.update_layout(
    height=380, template="plotly_white",
    margin=dict(l=20, r=20, t=30, b=20),
    xaxis=dict(showgrid=True, gridcolor="#F1F5F9"),
    yaxis=dict(title="Drawdown (%)", showgrid=True, gridcolor="#F1F5F9"),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    hovermode="x unified"
)
st.plotly_chart(fig_dd, width="stretch")

st.write("---")

# ------------------------------------------------------------------------------
# 8. SECTION 4: INSTITUTIONAL TEARSHEET METRICS TABLE
# ------------------------------------------------------------------------------
st.markdown("### Comprehensive Quantitative Tearsheet")

tearsheet = pd.DataFrame({
    'Metric': [
        'Total Cumulative Return',
        'Annualized Return (CAGR)',
        'Annualized Volatility',
        'Sharpe Ratio (Rf=0%)',
        'Sortino Ratio (Downside)',
        'Maximum Drawdown (MDD)',
        'Daily Win Rate',
        'Daily Gain/Loss Ratio',
        'Position Changes (Entries / Exits)'
    ],
    'Strategy': [
        f"{s_metrics['total_return']:+.2f}%",
        f"{s_metrics['cagr']:+.2f}%",
        f"{s_metrics['ann_vol']:.2f}%",
        f"{s_metrics['sharpe']:.2f}",
        f"{s_metrics['sortino']:.2f}",
        f"{s_metrics['mdd']:.2f}%",
        f"{s_metrics['win_rate']:.1f}%",
        f"{s_metrics['profit_factor']}",
        f"{trades_count}"
    ],
    'Benchmark (Buy & Hold)': [
        f"{b_metrics['total_return']:+.2f}%",
        f"{b_metrics['cagr']:+.2f}%",
        f"{b_metrics['ann_vol']:.2f}%",
        f"{b_metrics['sharpe']:.2f}",
        f"{b_metrics['sortino']:.2f}",
        f"{b_metrics['mdd']:.2f}%",
        f"{b_metrics['win_rate']:.1f}%",
        f"{b_metrics['profit_factor']}",
        "1 (Passive Buy)"
    ]
})

st.dataframe(tearsheet, hide_index=True, width="stretch")
