# 🎓 AI Portfolio Manager: Comprehensive Viva & Final Document Guide

This document operates as a complete technical guide for your final project report and viva presentation. It comprehensively covers the models, algorithms, architecture, and design decisions behind the AI Portfolio Manager.

---

## 🏛️ 1. Project Overview & Objective

The **AI Portfolio Manager** is a full-stack, AI-driven financial advisory system designed to democratize high-level, institutional-grade portfolio construction. Its primary objective is to dynamically process user parameters (Age, Income, Risk Appetite, Horizon) and output a highly personalized, backtested investment strategy in individual stocks and SIP (Mutual Funds/ETFs) with zero latency.

### **Core Problem Solved:**
Most retail investors rely on manual searching and generic mutual fund suggestions. 
- **The Solution:** Our system automatically mathematically weights a user's true risk capacity against a heavily curated pool of top-performing assets (The Top 200 Database) to generate custom allocations with predictive compounding visualizations.

---

## 🏗️ 2. Architectural Modules

The system is strictly divided into three modules for zero-overlap processing:

1. **`app.py` (The Entry Router)**
   * Initializes Streamlit's web server context. Configures the UI framework into Dark Mode and Wide View properties.
2. **`ui/dashboard.py` (The Frontend UI & Logic Gateway)**
   * This handles State Management via `st.session_state` (meaning real-time interactions do not cause total page reloads unnecessarily). 
   * It houses the layout definitions (`st.columns`, `.tabs`) and embeds dynamic Plotly visualizations. It filters data natively using pure Pandas array-mask constraints.
3. **`backend/screener_engine.py` (The Offline AI Intelligence Backend)**
   * Operates as a scheduled Python script that downloads raw OHLCV (Open, High, Low, Close, Volume) data from Yahoo Finance across exactly **120 of the most liquid NSE symbols**. 
   * It calculates metrics like historical CAGR and outputs `screener_db.csv`, effectively decoupling the frontend UI from any strict rate-limiting by Yahoo Finance.

---

## 🧱 3. Algorithms & Mathematical Models Implemented

You must be able to explain exactly *how* the AI chooses its assets. The system utilizes three primary proprietary models:

### A. The Weighted Dynamic Risk Algorithm
Instead of just asking a user "Are you Conservative or Growth?", the algorithm mathematically derives your *true* capacity:
* **Age Calculation**: `20 - (Age - 18) * (40/52)`. (Young users get a higher score since they have decades to recover from market crashes).
* **Horizon Modifier**: Modifiers range from `-35` (Emergency funds Needed) to `+30` (Long Term).
* **The Override Rule**: Even if a 20-year-old selects "Growth" appetite, if their Horizon is "Emergency (0-1Y)", the algorithm computes a low final score and forces the user into `Very Low Risk` (e.g., Liquid ETFs and Gold), actively protecting the user from poor financial decisions.

### B. Stable Seeded-Sampling Model (`random.Random`)
- Pure randomization creates chaos (the AI changes its mind on every click). 
- We built a deterministic hashing model where `Seed = Age + Monthly Budget`. This guarantees the specific subset of recommended stocks stays identical for a specific user profile across sessions, producing a highly confident "Professional Advisory" feel.

### C. The Predictive AI Model (Machine Learning via Scikit-Learn)
- Your project incorporates a true Machine Learning model (`LinearRegression` from `sklearn`) inside the **Stock Scanner** tab.
- When you type in a stock symbol, the AI dynamically extracts the historical OHLCV closing prices, trains the scikit-learn model, and generates a **30-day continuous statistical forecast**.
- **Why this model?** Linear Regression was chosen precisely for its ability to filter out pure short-term noise and clearly map the macro structural trend of an asset over the selected timeframe, giving investors a clear directional target.

### D. The Resampling Return Model (The "Insufficient Data" Fix)
- To prevent mathematical crashes on new companies (like those listed 2 years ago) when calculating a 5-year CAGR, the system does not fail. 
- It downloads pure granular `1d` (Daily) candlestick data, and uses Python Pandas to resample it dynamically (`resample('ME')`) into month-end markers. It calculates the True Compounded Return over whatever fraction of years actually exists, rather than hard-crashing.

---

## 📊 4. The Top 200 Curated Assets Criteria

*Question: "Why doesn't the AI search all 2000 NSE stocks?"*
**Answer**: Our app allows *manual* search of all 2000+ stocks in the Scanner, but the AI only automates suggestions from a **curated list of 200**. 
- **Criteria**: We selected strictly Nifty 50 (bluechips), Next 50, and Top Midcap 150 components mapped alongside highly liquid Debt/Commodity ETFs. This guarantees "junk" penny stocks are mathematically incapable of ever being recommended by the AI.

---

## ⚖️ 5. Pros & Cons (Limitations) for Viva Defense

**Pros (Strengths):**
1. **Highly Performant Local Processing**: By using `.csv` caching (`screener_db.csv`) and `st.cache_data`, the UI charts render instantly instead of taking 10+ seconds for API requests per interaction.
2. **Error-Prone Resilency**: The `resolve_ticker()` functionality corrects bad user inputs (e.g., typing "TATA" corrects to `TCS.NS`) which significantly enhances UX.
3. **Open-Source No-Cost Design**: Operates entirely without expensive Data scraping keys (e.g., Bloomberg).

**Cons (Limitations & Future Scope):**
1. **No Live Order Execution**: The app creates a beautiful "Plan" to download via CSV, but the user still has to go to Zerodha/Groww manually to execute the trades. (Future scope: Broker API integration).
2. **Yahoo Finance Dependency**: Web scraping APIs are notoriously unstable. If Yahoo changes its internal DOM structure natively, `yfinance` might fail randomly for certain tickers.
3. **Static Core Database**: The `backend/screener_engine.py` is not continuously scanning the live stock market 24/7; it requires a developer to manually run it periodically to refresh the metrics.
