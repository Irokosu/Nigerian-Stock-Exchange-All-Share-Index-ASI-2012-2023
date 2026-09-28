"""
================================================================================
BACKEND COMPUTATIONAL ENGINE: Returns, Performance & Time-Series Math
Created by: OPEYEMI SAMSON IROKOSU
PURPOSE:
- Pure computational functions for financial returns, compounding, rolling windows,
  annual aggregations, and extreme period analysis.
- Zero UI code. Pure NumPy and Pandas operations.
================================================================================
"""

import pandas as pd
import numpy as np


# ------------------------------------------------------------------------------
# 1. COMPOUND ANNUAL GROWTH RATE (CAGR)
# ------------------------------------------------------------------------------
def calculate_cagr(start_val: float, end_val: float, years: float) -> float:
    """
    Computes the Compound Annual Growth Rate (CAGR).
    Formula: ((End Value / Start Value) ** (1 / Years)) - 1
    """
    if start_val <= 0 or years <= 0:
        return 0.0
    return (((end_val / start_val) ** (1.0 / years)) - 1.0) * 100.0


# ------------------------------------------------------------------------------
# 2. CUMULATIVE RETURNS & INVESTMENT GROWTH
# ------------------------------------------------------------------------------
def calculate_cumulative_growth(df: pd.DataFrame, initial_capital: float = 100_000.0) -> pd.DataFrame:
    """
    Computes daily returns, cumulative returns, and simulated wealth trajectory 
    for an initial capital allocation (e.g. ₦100,000).
    """
    data = df.copy().sort_values('date').reset_index(drop=True)
    
    # Calculate simple daily percentage return from Close prices
    data['daily_return'] = data['close'].pct_change().fillna(0.0)
    
    # Cumulative compound multiplier
    data['growth_multiplier'] = (1.0 + data['daily_return']).cumprod()
    
    # Cumulative return percentage
    data['cumulative_return_pct'] = (data['growth_multiplier'] - 1.0) * 100.0
    
    # Simulated Portfolio Wealth Value in Naira
    data['portfolio_value'] = initial_capital * data['growth_multiplier']
    
    return data


# ------------------------------------------------------------------------------
# 3. ANNUAL CALENDAR PERFORMANCE
# ------------------------------------------------------------------------------
def calculate_annual_returns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes calendar year performance from 2012 to 2023:
    Start Close, End Close, Annual Return (%), Highest Point, Lowest Point.
    """
    data = df.copy().sort_values('date').reset_index(drop=True)
    data['year'] = data['date'].dt.year
    
    annual_summary = data.groupby('year').agg(
        start_date=('date', 'first'),
        end_date=('date', 'last'),
        start_close=('close', 'first'),
        end_close=('close', 'last'),
        high=('high', 'max'),
        low=('low', 'min')
    ).reset_index()
    
    annual_summary['prior_year_end_close'] = annual_summary['end_close'].shift(1)
    annual_summary['return_basis_close'] = annual_summary['prior_year_end_close'].fillna(annual_summary['start_close'])
    annual_summary['annual_return_pct'] = (annual_summary['end_close'] / annual_summary['return_basis_close'] - 1.0) * 100.0
    
    return annual_summary


# ------------------------------------------------------------------------------
# 4. MONTHLY RETURNS MATRIX (HEATMAP DATA)
# ------------------------------------------------------------------------------
def calculate_monthly_returns_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generates a 2D matrix (Year x Month) of monthly returns percentage for heatmap display.
    """
    data = df.copy().sort_values('date').reset_index(drop=True)
    data['year'] = data['date'].dt.year
    data['month'] = data['date'].dt.month
    
    # Group by Year and Month, taking first and last close
    monthly_agg = data.groupby(['year', 'month']).agg(
        start_close=('close', 'first'),
        end_close=('close', 'last')
    ).reset_index()
    
    monthly_agg['prior_month_end_close'] = monthly_agg['end_close'].shift(1)
    monthly_agg['return_pct'] = (monthly_agg['end_close'] / monthly_agg['prior_month_end_close'] - 1.0) * 100.0
    monthly_agg.loc[monthly_agg.index[0], 'return_pct'] = np.nan
    
    # Pivot into Year (rows) by Month (columns)
    matrix = monthly_agg.pivot(index='year', columns='month', values='return_pct')
    
    # Map month numbers to 3-letter names
    month_names = {
        1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun',
        7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'
    }
    matrix = matrix.rename(columns=month_names)
    return matrix


# ------------------------------------------------------------------------------
# 5. MULTI-HORIZON ROLLING RETURNS
# ------------------------------------------------------------------------------
def calculate_rolling_returns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates rolling performance across standard institutional trading horizons:
    - 1 Month: 21 trading days
    - 3 Months (Quarter): 63 trading days
    - 6 Months: 126 trading days
    - 1 Year (Annual): 252 trading days
    """
    data = df.copy().sort_values('date').reset_index(drop=True)
    
    data['roll_1m_pct'] = data['close'].pct_change(21) * 100.0
    data['roll_3m_pct'] = data['close'].pct_change(63) * 100.0
    data['roll_6m_pct'] = data['close'].pct_change(126) * 100.0
    data['roll_1y_pct'] = data['close'].pct_change(252) * 100.0
    
    return data


# ------------------------------------------------------------------------------
# 6. BEST & WORST TRADING INTERVALS
# ------------------------------------------------------------------------------
def get_best_worst_intervals(df: pd.DataFrame) -> pd.DataFrame:
    """
    Extracts the highest and lowest historical returns across 1D, 1W, 1M, 3M, and 1Y windows.
    """
    data = df.copy().sort_values('date').reset_index(drop=True)
    
    windows = {
        '1 Day (Daily)': 1,
        '1 Week (5 Days)': 5,
        '1 Month (21 Days)': 21,
        '1 Quarter (63 Days)': 63,
        '1 Year (252 Days)': 252
    }
    
    results = []
    
    for label, w in windows.items():
        rolling_series = data['close'].pct_change(w) * 100.0
        
        # Best
        best_idx = rolling_series.idxmax()
        best_val = rolling_series.loc[best_idx]
        best_end_date = data.loc[best_idx, 'date']
        
        # Worst
        worst_idx = rolling_series.idxmin()
        worst_val = rolling_series.loc[worst_idx]
        worst_end_date = data.loc[worst_idx, 'date']
        
        results.append({
            'Horizon': label,
            'Best Return (%)': round(best_val, 2),
            'Best Period End Date': best_end_date.strftime('%d %b %Y'),
            'Worst Return (%)': round(worst_val, 2),
            'Worst Period End Date': worst_end_date.strftime('%d %b %Y')
        })
        
    return pd.DataFrame(results)


# Standalone verification block
if __name__ == '__main__':
    from data_loader import load_clean_data
    test_df = load_clean_data()
    print("=== BACKEND CALCULATIONS VERIFICATION ===")
    annuals = calculate_annual_returns(test_df)
    print("Annual Performance (Sample):")
    print(annuals[['year', 'annual_return_pct']].head(4))
    extremes = get_best_worst_intervals(test_df)
    print("\nBest/Worst Intervals:")
    print(extremes.to_string(index=False))
    print("\nBackend calculation module verified!")

    # ==============================================================================
# MODULE 2: RISK & VOLATILITY CALCULATIONS
# ==============================================================================
from scipy import stats


# ------------------------------------------------------------------------------
# 7. ROLLING HISTORICAL VOLATILITY
# ------------------------------------------------------------------------------
def calculate_rolling_volatility(df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes rolling annualized volatility across standard institutional windows:
    - 21-day  (1 Month)
    - 63-day  (1 Quarter)
    - 252-day (1 Year)
    Annualized by multiplying daily standard deviation by sqrt(252).
    """
    data = df.copy().sort_values('date').reset_index(drop=True)
    data['daily_return'] = data['close'].pct_change()

    data['vol_21d']  = data['daily_return'].rolling(21).std()  * np.sqrt(252) * 100
    data['vol_63d']  = data['daily_return'].rolling(63).std()  * np.sqrt(252) * 100
    data['vol_252d'] = data['daily_return'].rolling(252).std() * np.sqrt(252) * 100

    return data


# ------------------------------------------------------------------------------
# 8. DRAWDOWN CURVE & MAXIMUM DRAWDOWN
# ------------------------------------------------------------------------------
def calculate_drawdown(df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes the rolling peak-to-trough drawdown series and identifies:
    - Maximum Drawdown (MDD): worst peak-to-trough decline in percentage.
    - Peak date (before the trough) and Trough date.
    """
    data = df.copy().sort_values('date').reset_index(drop=True)

    # Rolling maximum (high-water mark)
    data['cum_max'] = data['close'].cummax()

    # Drawdown as percentage below high-water mark
    data['drawdown_pct'] = ((data['close'] - data['cum_max']) / data['cum_max']) * 100.0

    return data


def get_max_drawdown_stats(df: pd.DataFrame) -> dict:
    """
    Returns the maximum drawdown event:
    mdd_pct, trough_date, trough_val, peak_date, peak_val, recovery info.
    """
    dd_df = calculate_drawdown(df)

    trough_idx  = dd_df['drawdown_pct'].idxmin()
    trough_date = dd_df.loc[trough_idx, 'date']
    trough_val  = dd_df.loc[trough_idx, 'close']
    mdd_pct     = dd_df.loc[trough_idx, 'drawdown_pct']

    # Peak is the last all-time-high before the trough
    pre_trough   = dd_df.loc[:trough_idx]
    peak_idx     = pre_trough['close'].idxmax()
    peak_date    = dd_df.loc[peak_idx, 'date']
    peak_val     = dd_df.loc[peak_idx, 'close']

    # Recovery: first date AFTER trough where price closes >= peak (if any)
    post_trough = dd_df.loc[trough_idx:]
    recovered   = post_trough[post_trough['close'] >= peak_val]
    recovery_date = recovered['date'].iloc[0] if not recovered.empty else None

    return {
        'mdd_pct':       round(mdd_pct, 2),
        'peak_val':      round(peak_val, 2),
        'peak_date':     peak_date,
        'trough_val':    round(trough_val, 2),
        'trough_date':   trough_date,
        'recovery_date': recovery_date
    }


# ------------------------------------------------------------------------------
# 9. VALUE AT RISK (VaR) & EXPECTED SHORTFALL (CVaR)
# ------------------------------------------------------------------------------
def calculate_var_cvar(df: pd.DataFrame) -> dict:
    """
    Computes Value at Risk and Conditional VaR (Expected Shortfall) using:
    A) Historical Simulation: directly from the empirical return distribution.
    B) Parametric (Gaussian): using mean and standard deviation.

    All values expressed as positive percentages representing the loss threshold.
    Confidence levels: 95% and 99%.
    """
    data = df.copy()
    data['daily_return'] = data['close'].pct_change()
    returns_pct = data['daily_return'].dropna() * 100.0

    mu    = returns_pct.mean()
    sigma = returns_pct.std()

    # --- Historical Simulation ---
    var_95_hist  = -np.percentile(returns_pct, 5)
    var_99_hist  = -np.percentile(returns_pct, 1)
    cvar_95_hist = -returns_pct[returns_pct <= -var_95_hist].mean()
    cvar_99_hist = -returns_pct[returns_pct <= -var_99_hist].mean()

    # --- Parametric Gaussian ---
    var_95_param = -(mu + stats.norm.ppf(0.05) * sigma)
    var_99_param = -(mu + stats.norm.ppf(0.01) * sigma)

    return {
        'var_95_hist':   round(var_95_hist, 3),
        'var_99_hist':   round(var_99_hist, 3),
        'cvar_95_hist':  round(cvar_95_hist, 3),
        'cvar_99_hist':  round(cvar_99_hist, 3),
        'var_95_param':  round(var_95_param, 3),
        'var_99_param':  round(var_99_param, 3),
        'ann_volatility': round(sigma * np.sqrt(252), 3),
        'returns_pct':   returns_pct
    }


# ==============================================================================
# MODULE 3: STATISTICAL & DISTRIBUTIONAL PROPERTIES
# ==============================================================================
from statsmodels.tsa.stattools import adfuller, acf, pacf


# ------------------------------------------------------------------------------
# 10. DESCRIPTIVE STATISTICS & DISTRIBUTIONAL SHAPE
# ------------------------------------------------------------------------------
def calculate_descriptive_stats(df: pd.DataFrame) -> dict:
    """
    Computes the full statistical profile of the daily return distribution:
    - Mean, Median, Std, Min, Max
    - Skewness: direction and magnitude of distribution asymmetry.
    - Excess Kurtosis: measures how fat the tails are vs. a Normal distribution.
      A value > 0 (leptokurtic) means more extreme events than normal.
    - Jarque-Bera Test: formally tests whether the distribution is Gaussian.
      A p-value < 0.05 rejects normality.
    """
    data = df.copy()
    data['daily_return'] = data['close'].pct_change()
    returns_pct = data['daily_return'].dropna() * 100.0

    jb_stat, jb_p = stats.jarque_bera(returns_pct)

    return {
        'mean':          round(returns_pct.mean(), 4),
        'median':        round(returns_pct.median(), 4),
        'std':           round(returns_pct.std(), 4),
        'min':           round(returns_pct.min(), 4),
        'max':           round(returns_pct.max(), 4),
        'skewness':      round(returns_pct.skew(), 4),
        'kurtosis':      round(returns_pct.kurt(), 4),
        'jb_stat':       round(jb_stat, 2),
        'jb_p':          round(jb_p, 8),
        'is_normal':     jb_p > 0.05,
        'returns_pct':   returns_pct
    }


# ------------------------------------------------------------------------------
# 11. AUGMENTED DICKEY-FULLER (ADF) STATIONARITY TEST
# ------------------------------------------------------------------------------
def run_adf_test(df: pd.DataFrame) -> dict:
    """
    Runs the Augmented Dickey-Fuller (ADF) test on both:
    A) Raw closing price series  → expected to be NON-stationary (has a unit root).
    B) Daily returns series      → expected to be STATIONARY (no unit root).

    H0 (Null Hypothesis): The series has a unit root (non-stationary).
    If p-value < 0.05 → Reject H0 → Series is stationary.
    """
    close_series = df['close'].dropna()

    data = df.copy()
    data['daily_return'] = data['close'].pct_change()
    returns_series = data['daily_return'].dropna() * 100.0

    # ADF on Price
    adf_price = adfuller(close_series, autolag='AIC', result_object=False)
    # ADF on Returns
    adf_ret   = adfuller(returns_series, autolag='AIC', result_object=False)

    def parse_adf(result):
        return {
            'adf_stat':    round(result[0], 4),
            'p_value':     round(result[1], 6),
            'lags_used':   result[2],
            'n_obs':       result[3],
            'critical_1':  round(result[4]['1%'], 4),
            'critical_5':  round(result[4]['5%'], 4),
            'critical_10': round(result[4]['10%'], 4),
            'is_stationary': result[1] < 0.05
        }

    return {
        'price':   parse_adf(adf_price),
        'returns': parse_adf(adf_ret)
    }


# ------------------------------------------------------------------------------
# 12. AUTOCORRELATION (ACF) & PARTIAL AUTOCORRELATION (PACF)
# ------------------------------------------------------------------------------
def calculate_acf_pacf(df: pd.DataFrame, nlags: int = 30) -> dict:
    """
    Computes ACF and PACF of the daily returns series.
    ACF measures how each return correlates with its own lags.
    PACF removes intermediate-lag effects.
    Used to detect: mean-reversion, momentum, or market memory.
    Significant sample autocorrelation is descriptive evidence only and does
    not establish market inefficiency or a tradable predictive edge.
    """
    data = df.copy()
    data['daily_return'] = data['close'].pct_change()
    returns = data['daily_return'].dropna() * 100.0

    acf_vals  = acf(returns, nlags=nlags, alpha=0.05, result_object=False)
    pacf_vals = pacf(returns, nlags=nlags, alpha=0.05)

    # Confidence bands (95%): ±1.96 / sqrt(N)
    conf_band = 1.96 / np.sqrt(len(returns))

    return {
        'lags':       list(range(nlags + 1)),
        'acf':        acf_vals[0].tolist(),
        'acf_lower':  acf_vals[1][:, 0].tolist(),
        'acf_upper':  acf_vals[1][:, 1].tolist(),
        'pacf':       pacf_vals[0].tolist(),
        'pacf_lower': pacf_vals[1][:, 0].tolist(),
        'pacf_upper': pacf_vals[1][:, 1].tolist(),
        'conf_band':  round(conf_band, 4)
    }


# ==============================================================================
# MODULE 4: TECHNICAL & TIME-SERIES ANALYSIS
# ==============================================================================
def calculate_moving_averages(df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes key institutional moving averages:
    - SMA 20 (Short-term trend / 1 month)
    - SMA 50 (Medium-term trend / 1 quarter)
    - SMA 200 (Long-term regime boundary / 1 year)
    - EMA 12 & EMA 26 (Fast and Slow exponential moving averages for MACD)
    """
    data = df.copy().sort_values('date').reset_index(drop=True)
    data['sma_20'] = data['close'].rolling(20).mean()
    data['sma_50'] = data['close'].rolling(50).mean()
    data['sma_200'] = data['close'].rolling(200).mean()
    data['ema_12'] = data['close'].ewm(span=12, adjust=False).mean()
    data['ema_26'] = data['close'].ewm(span=26, adjust=False).mean()
    return data


def calculate_rsi(df: pd.DataFrame, window: int = 14) -> pd.Series:
    """
    Calculates Relative Strength Index (RSI) using Wilder's smoothing.
    Standard thresholds: Overbought >= 70, Oversold <= 30.
    """
    data = df.copy().sort_values('date').reset_index(drop=True)
    delta = data['close'].diff()
    gain = (delta.where(delta > 0, 0.0)).fillna(0.0)
    loss = (-delta.where(delta < 0, 0.0)).fillna(0.0)

    avg_gain = gain.ewm(alpha=1.0 / window, adjust=False, min_periods=window).mean()
    avg_loss = loss.ewm(alpha=1.0 / window, adjust=False, min_periods=window).mean()

    rs = avg_gain / avg_loss.replace(0, np.nan)
    rsi = 100.0 - (100.0 / (1.0 + rs))
    rsi = rsi.mask((avg_loss == 0) & (avg_gain > 0), 100.0)
    rsi = rsi.mask((avg_loss == 0) & (avg_gain == 0), 50.0)
    return rsi


def calculate_macd(df: pd.DataFrame, fast: int = 12, slow: int = 26, signal_span: int = 9) -> pd.DataFrame:
    """
    Computes Moving Average Convergence Divergence (MACD):
    - MACD Line: 12-day EMA - 26-day EMA
    - Signal Line: 9-day EMA of MACD Line
    - Histogram: MACD Line - Signal Line
    """
    data = df.copy().sort_values('date').reset_index(drop=True)
    ema_fast = data['close'].ewm(span=fast, adjust=False).mean()
    ema_slow = data['close'].ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal_span, adjust=False).mean()
    macd_hist = macd_line - signal_line

    result = pd.DataFrame({
        'date': data['date'],
        'macd': macd_line,
        'signal': signal_line,
        'hist': macd_hist
    })
    return result


def calculate_seasonality(df: pd.DataFrame) -> dict:
    """
    Computes calendar seasonality across two dimensions:
    1. Day-of-Week Effect: Average daily return and win rate for Monday - Friday.
    2. Month-of-Year Seasonality: Average month-end close-to-close return and win rate by calendar month.
    """
    data = df.copy().sort_values('date').reset_index(drop=True)
    data['daily_return'] = data['close'].pct_change() * 100.0
    data['day_name'] = data['date'].dt.day_name()
    data['month_name'] = data['date'].dt.strftime('%b')
    data['month_num'] = data['date'].dt.month

    # Day of Week
    days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    dow_stats = []
    for day in days_order:
        subset = data[data['day_name'] == day]['daily_return'].dropna()
        if len(subset) > 0:
            dow_stats.append({
                'Day': day,
                'Avg Return (%)': round(subset.mean(), 3),
                'Median Return (%)': round(subset.median(), 3),
                'Win Rate (%)': round((subset > 0).mean() * 100.0, 1),
                'Trading Days': len(subset)
            })
    dow_df = pd.DataFrame(dow_stats)

    # Monthly Seasonality
    month_ends = data.groupby(data['date'].dt.to_period('M')).agg(
        date=('date', 'last'), end_close=('close', 'last')
    )
    month_ends['monthly_return'] = month_ends['end_close'].pct_change() * 100.0
    month_ends = month_ends.dropna(subset=['monthly_return']).copy()
    month_ends['month_num'] = month_ends['date'].dt.month
    month_ends['month_name'] = month_ends['date'].dt.strftime('%b')
    monthly_agg = month_ends.groupby(['month_num', 'month_name']).agg(
        avg_return=('monthly_return', 'mean'),
        median_return=('monthly_return', 'median'),
        win_rate=('monthly_return', lambda s: (s > 0).mean() * 100.0),
        count=('monthly_return', 'count')
    ).reset_index().sort_values('month_num')

    monthly_agg['avg_return'] = monthly_agg['avg_return'].round(3)
    monthly_agg['win_rate'] = monthly_agg['win_rate'].round(1)

    return {
        'dow_df': dow_df,
        'monthly_df': monthly_agg
    }


# ==============================================================================
# MODULE 5: PRICE-VOLUME DYNAMICS
# ==============================================================================
def get_clean_volume_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Filters to rows with positive recorded volume. Returns and price direction
    are calculated before filtering so the first retained row does not bridge
    the preceding zero-volume period.
    """
    data = df.copy().sort_values('date').reset_index(drop=True)
    data['daily_return'] = data['close'].pct_change()
    data['price_direction'] = data['close'].diff()
    return data[data['volume'] > 0].copy().reset_index(drop=True)


def calculate_volume_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes key trading volume indicators:
    - 20-day Volume SMA (Short-term liquidity benchmark)
    - 50-day Volume SMA (Quarterly liquidity benchmark)
    - Volume Surge Ratio: Current volume vs 20-day SMA
    - Volume Surge Flag (> 2.0x 20-day SMA)
    """
    data = get_clean_volume_data(df)
    data['vol_sma_20'] = data['volume'].rolling(20).mean()
    data['vol_sma_50'] = data['volume'].rolling(50).mean()
    data['vol_surge_ratio'] = data['volume'] / data['vol_sma_20'].replace(0, np.nan)
    data['is_volume_spike'] = data['vol_surge_ratio'] >= 2.0
    return data


def calculate_obv(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates On-Balance Volume (OBV):
    - Volume is added when Close > Prior Close.
    - Volume is subtracted when Close < Prior Close.
    - Volume is unchanged when Close == Prior Close.
    """
    data = get_clean_volume_data(df)
    direction = np.sign(data['price_direction']).fillna(0.0)
    data['obv'] = (direction * data['volume']).cumsum()
    data['obv_sma_20'] = data['obv'].rolling(20).mean()
    return data


def calculate_price_volume_correlation(df: pd.DataFrame, window: int = 63) -> pd.DataFrame:
    """
    Computes rolling correlation between daily returns and trading volume.
    Correlation describes co-movement between returns and recorded volume; it
    does not identify trader types or establish accumulation.
    """
    data = get_clean_volume_data(df)
    data['roll_corr'] = data['daily_return'].rolling(window).corr(data['volume'])
    return data


def get_top_volume_days(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """
    Returns the top N heaviest trading volume days with subsequent price action.
    """
    data = get_clean_volume_data(df)
    data['daily_return_pct'] = data['daily_return'] * 100.0
    top = data.sort_values('volume', ascending=False).head(top_n).copy()
    
    top_display = pd.DataFrame({
        'Date': top['date'].dt.strftime('%d %b %Y'),
        'Close (Pts)': top['close'].apply(lambda x: f"{x:,.2f}"),
        'Volume': top['volume'].apply(lambda x: f"{x:,.0f}"),
        'Daily Change (%)': top['daily_return_pct'].apply(lambda x: f"{x:+.2f}%")
    })
    return top_display


# ==============================================================================
# MODULE 6: QUANTITATIVE MODELING & STRATEGY BACKTESTING
# ==============================================================================
def calculate_strategy_metrics(daily_returns: pd.Series, risk_free_rate: float = 0.0) -> dict:
    """
    Strategy performance metrics:
    - Total Return (%)
    - CAGR (%)
    - Annualized Volatility (%)
    - Sharpe Ratio
    - Sortino Ratio (downside risk only)
    - Maximum Drawdown (%)
    - Win Rate (%)
    - Daily gross gains / gross losses ratio
    `risk_free_rate` is an annual percentage (for example, 2.0 means 2%).
    """
    rets = daily_returns.dropna()
    if len(rets) == 0:
        return {}

    n_days = len(rets)
    years = max(n_days - 1, 1) / 252.0

    cum_growth = (1.0 + rets).cumprod()
    total_return = (cum_growth.iloc[-1] - 1.0) * 100.0 if not cum_growth.empty else 0.0

    cagr = (((1.0 + total_return / 100.0) ** (1.0 / years)) - 1.0) * 100.0 if years > 0 and total_return > -100.0 else 0.0

    ann_vol = rets.std() * np.sqrt(252) * 100.0
    annual_mean = rets.mean() * 252.0 * 100.0
    excess_return = annual_mean - risk_free_rate
    sharpe = excess_return / ann_vol if ann_vol > 0 else 0.0
    daily_target = risk_free_rate / 100.0 / 252.0
    downside = np.minimum(rets - daily_target, 0.0)
    downside_std = np.sqrt(np.mean(np.square(downside))) * np.sqrt(252.0) * 100.0
    sortino = excess_return / downside_std if downside_std > 0 else 0.0

    # Drawdown
    cum_max = cum_growth.cummax()
    drawdown = (cum_growth - cum_max) / cum_max * 100.0
    mdd = drawdown.min()

    # Win rate & Profit factor
    pos_rets = rets[rets > 0]
    neg_rets = rets[rets < 0]
    win_rate = (len(pos_rets) / len(rets[rets != 0])) * 100.0 if len(rets[rets != 0]) > 0 else 0.0
    gross_gains = pos_rets.sum()
    gross_losses = abs(neg_rets.sum())
    profit_factor = gross_gains / gross_losses if gross_losses > 0 else np.nan

    return {
        'total_return': round(total_return, 2),
        'cagr': round(cagr, 2),
        'ann_vol': round(ann_vol, 2),
        'sharpe': round(sharpe, 2),
        'sortino': round(sortino, 2),
        'mdd': round(mdd, 2),
        'win_rate': round(win_rate, 1),
        'profit_factor': round(profit_factor, 2) if not np.isnan(profit_factor) else "N/A"
    }


def backtest_ma_crossover(
    df: pd.DataFrame,
    fast_window: int = 50,
    slow_window: int = 200,
    initial_capital: float = 100_000.0,
    fee_pct: float = 0.001
) -> dict:
    """
    Backtests a Dual Moving Average Trend Following Strategy:
    - Long when Fast MA > Slow MA.
    - Cash when Fast MA <= Slow MA.
    - Execution at next bar close with optional transaction cost.
    """
    data = df.copy().sort_values('date').reset_index(drop=True)
    data['market_ret'] = data['close'].pct_change().fillna(0.0)

    data['fast_ma'] = data['close'].rolling(fast_window).mean()
    data['slow_ma'] = data['close'].rolling(slow_window).mean()

    # Generate Signal (1 = Invested, 0 = In Cash)
    data['signal'] = np.where(data['fast_ma'] > data['slow_ma'], 1, 0)
    # Trade execution on NEXT day
    # Signal uses the current close and fills at the next session close.
    # Exposure begins earning returns only after the fill; costs are booked on
    # the fill date rather than on the first day of the new exposure.
    fill_position = data['signal'].shift(1).fillna(0)
    data['position'] = data['signal'].shift(2).fillna(0)
    trade_executed = fill_position.diff().abs().fillna(0.0).gt(0.0)
    cost = np.where(trade_executed, fee_pct, 0.0)

    # Strategy daily returns
    data['strat_ret'] = (1.0 + data['position'] * data['market_ret']) * (1.0 - cost) - 1.0

    # Cumulative growth
    data['benchmark_portfolio'] = initial_capital * (1.0 + data['market_ret']).cumprod()
    data['strategy_portfolio'] = initial_capital * (1.0 + data['strat_ret']).cumprod()

    # Drawdown
    b_max = data['benchmark_portfolio'].cummax()
    data['benchmark_dd'] = (data['benchmark_portfolio'] - b_max) / b_max * 100.0

    s_max = data['strategy_portfolio'].cummax()
    data['strategy_dd'] = (data['strategy_portfolio'] - s_max) / s_max * 100.0

    # Number of trades
    trades_count = int(trade_executed.sum())

    strat_metrics = calculate_strategy_metrics(data['strat_ret'])
    bench_metrics = calculate_strategy_metrics(data['market_ret'])

    return {
        'data': data,
        'strat_metrics': strat_metrics,
        'bench_metrics': bench_metrics,
        'trades_count': trades_count
    }


def backtest_rsi_strategy(
    df: pd.DataFrame,
    rsi_period: int = 14,
    oversold: float = 35.0,
    overbought: float = 70.0,
    initial_capital: float = 100_000.0,
    fee_pct: float = 0.001
) -> dict:
    """
    Backtests an RSI Mean-Reversion Strategy:
    - Enters Long when RSI drops below `oversold` threshold.
    - Exits to Cash when RSI rises above `overbought` threshold.
    """
    data = df.copy().sort_values('date').reset_index(drop=True)
    data['market_ret'] = data['close'].pct_change().fillna(0.0)
    data['rsi'] = calculate_rsi(data, window=rsi_period)

    # State machine for holding positions
    positions = []
    current_pos = 0
    for r in data['rsi']:
        if pd.isna(r):
            positions.append(0)
        elif r <= oversold:
            current_pos = 1
            positions.append(current_pos)
        elif r >= overbought:
            current_pos = 0
            positions.append(current_pos)
        else:
            positions.append(current_pos)

    data['signal'] = positions
    # Signal uses the current close and fills at the next session close.
    # Exposure begins earning returns only after the fill; costs are booked on
    # the fill date rather than on the first day of the new exposure.
    fill_position = data['signal'].shift(1).fillna(0)
    data['position'] = data['signal'].shift(2).fillna(0)
    trade_executed = fill_position.diff().abs().fillna(0.0).gt(0.0)
    cost = np.where(trade_executed, fee_pct, 0.0)

    data['strat_ret'] = (1.0 + data['position'] * data['market_ret']) * (1.0 - cost) - 1.0
    data['benchmark_portfolio'] = initial_capital * (1.0 + data['market_ret']).cumprod()
    data['strategy_portfolio'] = initial_capital * (1.0 + data['strat_ret']).cumprod()

    b_max = data['benchmark_portfolio'].cummax()
    data['benchmark_dd'] = (data['benchmark_portfolio'] - b_max) / b_max * 100.0

    s_max = data['strategy_portfolio'].cummax()
    data['strategy_dd'] = (data['strategy_portfolio'] - s_max) / s_max * 100.0

    trades_count = int(trade_executed.sum())

    strat_metrics = calculate_strategy_metrics(data['strat_ret'])
    bench_metrics = calculate_strategy_metrics(data['market_ret'])

    return {
        'data': data,
        'strat_metrics': strat_metrics,
        'bench_metrics': bench_metrics,
        'trades_count': trades_count
    }
