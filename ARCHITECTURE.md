# 🏛️ Architecture & System Design
**AI Portfolio Manager** is built on a highly modular, real-time reactive architecture. This document explains the core logic, algorithms, models, and module flows that drive the financial advisory engine.

---

## 📊 1. System Architecture Diagram

```mermaid
graph TD
    %% User Inputs
    User([👨‍💼 User Input]) -->|Age, Income, Risk, Horizon| UI

    %% Modules
    subgraph Streamlit Interface [UI & User Experience Module]
        UI[ui/dashboard.py]
        Tabs[Tabs: Portfolio, Market Picks, Scanner, SIP Planner]
        UI --- Tabs
    end

    subgraph Data Gateway [Backend Data Intelligence Module]
        YF[yfinance API]
        DB[(Offline Screener DB)]
        Fallback[Fallback Curated Universe]
    end

    subgraph Mathematical Engine [Algorithmic Processing Module]
        RiskAlg[Weighted Risk Scoring Alg]
        CAGR[Compounding & Metric Alg]
        Shuffle[Smart Seeded Sampling Alg]
    end

    %% Data Flow
    UI -.-> |Hash State Update| RiskAlg
    RiskAlg --> |Risk Profile (Allowed Tiers)| UI
    
    YF --> |Hist Data & Live CMP| DB
    DB --> |Top Performing Assets| UI
    Fallback --> |Zero-Latency Defaults| UI

    UI --> |Historical Pandas Data| CAGR
    CAGR --> |Future Target / Returns| Tabs
    UI --> |Subset Filtering| Shuffle
    Shuffle --> |Diversified Unique Sets| Tabs
```

---

## 🛠️ 2. Core Modules & Their Functionality

### A. `ui/dashboard.py` (The Pro Interface & Logic Engine)
The central intelligence and layout renderer that serves the frontend UI.
- **Dynamic Risk Profiler**: Translates user inputs into a continuous mathematical score mapping to `Growth`, `Balanced`, or `Conservative` tiers.
- **Strict Asset Segregation**: Enforces filtering constraints (`~Sector.str.contains("ETF")`) to prevent Asset class mixing (guarantees Market Picks are *strictly stocks*).
- **Interactive Visualization**: Uses Plotly (`px.scatter`, `go.Candlestick`, `go.Scatter`) to render highly responsive, dynamic financial charts based on local data slices.

### B. `backend/screener_engine.py` (The AI Offline Brain)
The robust intelligence gatherer designed to protect the system from API rate limits.
- **Data Scraping**: Programmatically cycles through Top 120+ NSE Tickers over a 5-year interval.
- **Indicator Construction**: Calculates institutional-grade metrics (Max Drawdown, Compounded Annual Growth Rate, Volatility).
- **Output Syncing**: Stores cleaned results in `backend/screener_db.csv` for instantaneous, zero-latency reads by the UI.

### C. `app.py`
The streamlined application entry point. Bootstraps Streamlit, enforces dark-mode configuration, and injects styling before handing off to the dashboard.

---

## 🧮 3. Algorithms & Mathematical Models Used

### 1. Weighted Risk Scoring Algorithm
This algorithm determines the exact Risk Profile and Allowed Asset Tiers based on a custom continuous scoring system rather than hard mappings:
- **Base Score**: `Appetite` adds baseline points (+25 Conservative, +55 Balanced, +85 Growth).
- **Age Penalty**: Formula `20 - (Age - 18) * (40/52)`. Younger users receive higher points because they have a longer runway to recover from high-risk drawdowns.
- **Horizon Modifier**: Short horizons deduct extreme points (-35 for Emergency) forcing the final calculation into a safe tier, effectively overriding user "Growth" ambitions if their timeframe is logically too short.

### 2. Defensive CAGR (Compounding) Algorithm
Calculates realistic long-term yield without failing on newly listed stocks (The "NaN/Insufficient Data Hack"):
- Calculates actual available years using `len(df) / 12` rather than dividing blindly by inputted `Horizon`.
- Uses `(Final_Corpus / Invested) ^ (1 / Real_Years) - 1` to project an accurate, defensible yield while dynamically guarding against zero-division loops.

### 3. AI Price Predictive Model (Machine Learning)
To satisfy the requirement of true predictive AI, we integrated a **Machine Learning model using `scikit-learn`**:
- **Algorithm**: `LinearRegression` (Ordinary Least Squares).
- **Function**: Automatically invoked in the Pro Scanner tab. It fits itself onto the historical OHLCV data to project an AI Mathematical Forecast line spanning 30 days into the future. It actively accounts for macro directional trends without manual human charting.

### 4. Seeded Reactivity (Stability Algorithm)
Instead of pure `random.sample()` which would cause recommendations to violently flicker on every browser refresh, we use **Seeded Sampling**. 
- **Hash Function**: `seed = int(Age) + int(InvestmentAmount) + session_state.shuffle_key`
- This ensures the UI feels "stable and highly confident" like a real advisor, only showing new selections when the user explicitly changes their profile settings or presses the `Shuffle Portfolio` button.

---

## 🛡️ 4. Data Models (Variables & Mapping)
- **Live Pandas DataFrames**: Holds transient OHLCV standard format data for real-time charting.
- **Ticker Mapping Resolution (`resolve_ticker`)**: A string processing model that maps human inputs (`NIFTY`) to perfectly qualified Yahoo Finance identifiers (`NIFTYBEES.NS`) using a fast-lookup dictionary and suffix-correction logic to ensure 100% data retrieval reliability.
