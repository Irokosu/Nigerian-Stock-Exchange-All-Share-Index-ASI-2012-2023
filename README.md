#  Nigerian Stock Exchange (NSE) All-Share Index (ASI)
## Exploratory Analytics, Econometric Properties & Quantitative Strategy Dashboard (2012 - 2023)

**Lead Creator & Quantitative Architect:** Opeyemi Samson Irokosu  
**Asset Class:** Nigerian Sovereign Equities Benchmark - NSE All-Share Index (ASI)  
**Time Horizon:** January 30, 2012 - December 22, 2023 (2,948 recorded sessions | 11.9 Calendar Years)  
**Technology Stack:** Python 3, Streamlit, Plotly, Pandas, NumPy, SciPy, Statsmodels  
**Visual Theme:** Emerald Capital & Champagne Gold Institutional Palette  

---

##  Executive Summary & The Market Story

The Nigerian Stock Exchange (NSE) All-Share Index is the premier performance benchmark tracking the total market capitalization of all quoted equities on Sub-Saharan Africa's largest economy. 

The dataset covers ASI levels from January 2012 through December 2023:
- **Starting Level (Jan 30, 2012):** 20,731.72 points (first recorded close)
- **Ending Level (Dec 22, 2023):** 74,023.27 points
- **ASI Price Return:** **+257.05%** (close-to-close price change; excludes dividends and costs)
- **Annualized Price Growth:** **+11.29%** using exact calendar time between observations
- **All-Time Intraday High:** 74,430.47 points (December 22, 2023)
- **All-Time Intraday Low:** 20,007.19 points (February 29, 2012)
- **2016 Period Close Low:** 22,456.32 points

### Observed Index Phases
1. **2012-2016:** The index rose and then declined; this chart description does not identify the cause of the movement.
2. **2017-2020:** The index recovered and later fell to a sample maximum drawdown of **-54.16%** from a prior closing peak to a closing trough of 20,669 points.
3. **The 2020-2023 Rally:** The index recovered from its 2020 trough and reached a new high by the end of the sample. This description is based on index levels; the dataset alone cannot establish the causes of the rally or investor flows.

This platform provides an exploratory econometric engine and interactive dashboard for describing the Nigerian equity market across this period. Results depend on the supplied index series and stated assumptions.

---

##  The Data Engineering Feat

Raw emerging market financial archives frequently contain severe formatting anomalies. Before any modeling could occur, the raw dataset underwent a comprehensive cleansing pipeline:

1. **Delimiter & Locale Normalization:** Resolved raw semicolon (`;`) delimited feeds with localized thousands separators and stripped currency artifact encodings (`?`).
2. **Numerical Type Casting:** Cleaned literal `%` characters from return columns and cast raw strings to high-precision IEEE 754 `float64`.
3. **Chronological Inversion:** The raw source stored records in reverse chronological order; the pipeline inverted the time index into a monotonic, ascending time-series (`2012-01-30` to `2023-12-22`).
4. **Microstructure Anomaly Imputation:** On **July 24, 2014**, the recorded opening price was `0.00`. Using the recorded close (`42,612.36`) and intraday percentage return (`+0.16%`), the true opening value was mathematically reconstructed as **42,542.51 points**.
5. **Volume Availability Profiling:** The cleaned file has positive volume on 1,651 sessions; earlier rows contain zero volume. Volume analysis uses recorded-volume sessions and does not alter the index price-return series.
6. **High-Performance Memory Caching:** The central data loader utilizes Streamlit's `@st.cache_data` in memory, ensuring that multi-page transitions load in milliseconds.

**Data provenance:** The project contains a raw CSV and a cleaning notebook, but does not record a source URL, retrieval date, or license. Those details should be added from the original provider before external or commercial reuse; they cannot be inferred from the files in this repository.

**Return-field validation:** The supplied `daily_change_pct` field does not reconcile with adjacent closes: among 2,947 consecutive observations, the maximum absolute difference is about 12.05 percentage points (April 1, 2015). Summary extremes and analysis returns are therefore derived from close-to-close changes; the raw field is retained only as supplied.

**Methods and scope:** Daily returns are close-to-close ASI price returns. Calendar-year and calendar-month returns use the previous period-end close; 2012 is a partial year and January 2012 is excluded from monthly seasonality because the prior month-end is unavailable. Volatility uses daily sample standard deviation annualized by √252. The backtest uses a one-session close-based execution delay, proportional costs on position changes, an Rf=0% Sharpe/Sortino assumption, and a 252-session year for annualization. It remains a hypothetical index simulation and omits dividends, taxes, market impact, financing, and instrument availability.

---

##  Platform Architecture & Directory Structure

```
Nigerian Stock Exchange All Share Index ASI 2012-2023/

 Home.py                          # Executive Landing Portal & Macro Trajectory Hub
 requirements.txt                 # Production dependencies
 README.md                        # Project Story, Architecture & Engineering Documentation
 USER_GUIDE.txt                   # User & Stakeholder Operational Manual

 backend/                         # PURE COMPUTATIONAL ENGINE (NumPy, SciPy, Statsmodels)
    __init__.py                  # Python package marker
    data_loader.py               # Memory-cached ingestion & macro summary metrics
    calculations.py              # Quantitative mathematical modules (returns, risk, stats, backtests)

 pages/                           # INTERACTIVE STREAMLIT APPLICATION MODULES
    01_Return_&_Performance.py   # Module 1: Investment Simulator, CAGR, Calendar Matrix
    02_Risk_&_Volatility.py      # Module 2: Rolling Volatility, Drawdowns, VaR / CVaR
    03_Statistical_Properties.py # Module 3: Distribution Fit, ADF Stationarity, ACF / PACF
    04_Technical_Analysis.py     # Module 4: MA Envelopes, RSI, MACD, Calendar Seasonality
    05_Price_Volume_Dynamics.py  # Module 5: Liquidity Trends, OBV, Up/Down Day Asymmetry
    06_Quantitative_Modeling.py  # Module 6: Algorithmic Strategy Backtesting & Tearsheet

 data/                            # DATA LAKE
     clean_Nigerian Stock Exchange All Share Index ASI 2012-2023.csv
     Nigerian Stock Exchange All Share Index ASI 2012-2023.csv
```

---

##  In-Depth Analytical Modules

### 0. Executive Landing Portal (`Home.py`)
- **Executive Attribution:** High-visibility author banner celebrating lead architect Opeyemi Samson Irokosu.
- **Macro Performance Snapshot:** 5 summary indicators (Current Close, ASI Price Return, annualized price growth, All-Time High, All-Time Low).
- **Macro Historical Chart:** Plotly interactive area trajectory with range slider and data-derived markers (2012 Baseline, maximum-drawdown close peak and trough, all-time intraday high).
- **Master Directory:** Visual module cards directing users across all 6 specialized suites.

### 1. Return & Performance Analysis (`pages/01_Return_&_Performance.py`)
- **Interactive Investment Simulator:** Illustrates how an arbitrary Naira amount would have tracked ASI price growth over selected dates, excluding dividends and costs.
- **Calendar Performance:** Color-coded calendar-year close-to-close returns; 2012 is a partial period because the series begins on January 30.
- **Monthly Heatmap Matrix:** Year-by-month close-to-close returns against the prior month-end close; the first observed month is blank because its prior month-end is unavailable.
- **Multi-Horizon Rolling Returns:** 1-month (21D), 3-month (63D), 6-month (126D), and 1-year (252D) rolling return trajectories.
- **Extreme Intervals Table:** Empirical best and worst historical trading windows.

### 2. Risk & Volatility Analysis (`pages/02_Risk_&_Volatility.py`)
- **Rolling Volatility Regimes:** 21D, 63D, and 252D rolling annualized volatility curves highlighting high-stress market crises.
- **Full Period Annualized Volatility:** 15.26%.
- **Maximum Drawdown (MDD) Anatomy:** Detailed breakdown of the catastrophic **-54.16%** bear decline from the January 19, 2018 peak (45,092.83 pts) to the April 6, 2020 trough (20,669.38 pts), tracking its recovery timeline.
- **Value at Risk (VaR):** Empirical daily 95% and 99% historical loss thresholds, estimated from this sample.
- **Expected Shortfall (CVaR):** Historical average loss beyond the sample VaR thresholds; these are estimates, not future loss limits.

### 3. Statistical & Distributional Properties (`pages/03_Statistical_Properties.py`)
- **Distribution Profile:** Empirical daily-return mean, standard deviation, skewness, and excess kurtosis, calculated from close-to-close price returns.
- **Jarque-Bera Normality Test:** The test evaluates Gaussian normality; rejection indicates that a normal distribution is a poor fit under this sample and test, not a complete model of tail risk.
- **Quantile-Quantile (QQ) Plot:** Demonstrates departure from normality at the outer tails.
- **ADF Stationarity Tests:** 
  - Raw price and daily return series are tested separately. Interpret ADF results as evidence relative to the unit-root null under selected test settings, not proof of stationarity or constant variance.
- **Market Memory (ACF & PACF):** Sample autocorrelation estimates are shown with approximate confidence bands; they do not establish market inefficiency or a tradable edge.

### 4. Time-Series & Technical Analysis (`pages/04_Technical_Analysis.py`)
- **Moving Average Envelopes:** SMA 20, SMA 50, SMA 200, and EMA 12/26 overlays with interactive range selector.
- **Cross Signals:** Golden Cross (SMA 50 > SMA 200) vs Death Cross trend state detection.
- **Momentum Indicators:** Relative Strength Index (RSI-14 with overbought >70 and oversold <30 thresholds) and MACD (12, 26, 9) signal line and histogram.
- **Empirical Calendar Anomalies:**
  - *Day-of-Week Effect:* Descriptive close-to-close daily-return summaries grouped by the date of the ending session; historical patterns are not forecasts.
  - *Monthly Seasonality:* Summarizes historical calendar-month close-to-close returns; it does not establish dividend or election effects.

### 5. Price-Volume Dynamics (`pages/05_Price_Volume_Dynamics.py`)
- **Volume Coverage Callout:** Discloses that positive volume values begin in the supplied file in 2015; provenance and completeness are not documented.
- **Dual-Axis Volume Chart:** Price trajectory accompanied by up/down color-coded recorded-volume bars and a 20-recorded-session volume average.
- **On-Balance Volume (OBV):** Cumulative volume signed by daily price direction; aggregate index volume cannot identify institutional traders.
- **Up-Day vs Down-Day Participation:** Quantifies whether volume expands during market rallies or market sell-offs.
- **Top 10 Historical Volume Spike Days:** Detailed table of historical high-volume events.

### 6. Quantitative Modeling & Strategy Backtesting (`pages/06_Quantitative_Modeling.py`)
- **Algorithmic Strategies:**
  - *Dual Moving Average Trend Following:* Long when Fast MA > Slow MA; cash otherwise. Includes a one-session execution delay and configurable proportional costs.
  - *RSI Mean-Reversion:* Buys on oversold dips and sells on overbought strength.
- **Comparative Wealth Curves:** Visualizes Strategy Portfolio growth against the Buy & Hold benchmark.
- **Downside Comparison:** Compares strategy and benchmark drawdowns in a hypothetical close-based simulation.
- **Performance Summary:** Compares CAGR, annualized volatility, Sharpe and Sortino ratios, maximum drawdown, daily win rate, and daily gain/loss ratio.

---

##  Visual Identity & Styling Standard

The application adheres strictly to the **Emerald Capital & Champagne Gold** aesthetic:
- **Primary Sovereign Emerald:** `#008751`
- **Dark Pine Sidebar:** `#064E3B`
- **Champagne Gold Accents:** `#D4AF37`
- **Amber Highlights:** `#F59E0B`
- **Bearish / Drawdown Red:** `#DC2626`
- **Backgrounds:** Clean institutional white (`#FFFFFF`) and slate (`#F8FAFC`)

*The emerald and gold palette provides a consistent visual theme.*

---

##  Installation & How to Run

1. **Clone the repository:**
   ```bash
   git clone <repo-url>
   cd "Nigerian Stock Exchange All Share Index ASI 2012-2023"
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Launch the platform:**
   ```bash
   streamlit run Home.py
   ```

4. **Access the web interface:**
   Open your browser at `http://localhost:8501`. Use the sidebar on the left to navigate seamlessly across all analytical pages.

---

##  Author & Attribution

**Opeyemi Samson Irokosu**  
*Quantitative Financial Analyst & Software Engineer*  
- Engineered the entire analytical pipeline, data cleansing architecture, econometric modeling engines, and interactive multi-page Streamlit portal.
- The project combines data preparation, descriptive calculations, and an interactive presentation; interpret outputs with the documented method and data limitations.
