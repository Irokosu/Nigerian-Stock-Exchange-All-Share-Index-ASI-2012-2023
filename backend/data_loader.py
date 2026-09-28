"""
================================================================================
BACKEND MODULE: Central Data Loader & Market Summary Engine
PURPOSE:
- Ingests the cleaned NSE ASI dataset (2012-2023).
- Caches data in memory using Streamlit's @st.cache_data for instant page loads.
- Computes macro-level lifetime summary statistics for the executive landing portal.
================================================================================
"""

import os
from pathlib import Path
import pandas as pd
import numpy as np

# Gracefully enable Streamlit caching if running inside Streamlit, or pass through if run standalone
try:
    import streamlit as st
    cache_decorator = st.cache_data
except ImportError:
    def cache_decorator(func):
        return func


def get_data_path() -> Path:
    """
    Resolves the absolute path to the clean CSV regardless of where the script is executed.
    """
    # Look for the data directory relative to this file's root or current working directory
    current_file_dir = Path(__file__).resolve().parent.parent
    candidate_path = current_file_dir / "data" / "clean_Nigerian Stock Exchange All Share Index ASI 2012-2023.csv"
    
    if candidate_path.exists():
        return candidate_path
    
    # Fallback to local data folder in current working directory
    fallback = Path("data") / "clean_Nigerian Stock Exchange All Share Index ASI 2012-2023.csv"
    if fallback.exists():
        return fallback.resolve()
        
    raise FileNotFoundError(f"Cleaned dataset not found at {candidate_path} or {fallback}")


@cache_decorator
def load_clean_data() -> pd.DataFrame:
    """
    Loads and caches the cleaned NSE ASI dataset.
    Returns:
        pd.DataFrame: Cleaned data with datetime index and sorted chronologically.
    """
    csv_path = get_data_path()
    df = pd.read_csv(csv_path, parse_dates=['date'])
    
    # Ensure chronological order and clean indexing
    df = df.sort_values(by='date', ascending=True).reset_index(drop=True)
    return df


def get_market_summary(df: pd.DataFrame) -> dict:
    """
    Calculates executive lifetime macro metrics for the landing page hero cards.
    
    Returns:
        dict: High-level market indicators (CAGR, total return, all-time high/low, etc.)
    """
    start_date = df['date'].iloc[0]
    end_date = df['date'].iloc[-1]
    
    start_close = df['close'].iloc[0]
    end_close = df['close'].iloc[-1]
    
    total_trading_days = len(df)
    total_calendar_years = (end_date - start_date).days / 365.25
    
    # Total cumulative return & CAGR
    total_return_pct = ((end_close - start_close) / start_close) * 100
    cagr_pct = (((end_close / start_close) ** (1 / total_calendar_years)) - 1) * 100
    
    # All-Time High & Low
    ath_val = df['high'].max()
    ath_row = df.loc[df['high'] == ath_val].iloc[0]
    
    atl_val = df['low'].min()
    atl_row = df.loc[df['low'] == atl_val].iloc[0]
    
    # Derive daily moves from the close series. The supplied daily_change_pct
    # field does not consistently reconcile to adjacent closes.
    close_returns_pct = df['close'].pct_change() * 100.0
    best_idx = close_returns_pct.idxmax()
    worst_idx = close_returns_pct.idxmin()
    best_day_val = close_returns_pct.loc[best_idx]
    best_day_row = df.loc[best_idx]
    worst_day_val = close_returns_pct.loc[worst_idx]
    worst_day_row = df.loc[worst_idx]
    
    return {
        "start_date": start_date,
        "end_date": end_date,
        "start_close": start_close,
        "end_close": end_close,
        "total_trading_days": total_trading_days,
        "total_calendar_years": round(total_calendar_years, 2),
        "total_return_pct": round(total_return_pct, 2),
        "cagr_pct": round(cagr_pct, 2),
        "all_time_high": ath_val,
        "ath_date": ath_row['date'],
        "all_time_low": atl_val,
        "atl_date": atl_row['date'],
        "best_single_day": best_day_val,
        "best_single_day_date": best_day_row['date'],
        "worst_single_day": worst_day_val,
        "worst_single_day_date": worst_day_row['date']
    }


# Standalone verification block
if __name__ == '__main__':
    data = load_clean_data()
    summary = get_market_summary(data)
    print("=== NSE ASI DATA LOADER VERIFICATION ===")
    print(f"Dataset Rows: {len(data):,} trading days")
    print(f"Date Span: {summary['start_date'].date()} to {summary['end_date'].date()}")
    print(f"Starting Index: {summary['start_close']:,.2f} -> Ending Index: {summary['end_close']:,.2f}")
    print(f"Total ASI Price Return: +{summary['total_return_pct']}% (Annualized Price Growth: {summary['cagr_pct']}%)")
    print(f"All-Time High: {summary['all_time_high']:,.2f} on {summary['ath_date'].date()}")
    print(f"All-Time Low: {summary['all_time_low']:,.2f} on {summary['atl_date'].date()}")
    print("Data loader module verified successfully!")
