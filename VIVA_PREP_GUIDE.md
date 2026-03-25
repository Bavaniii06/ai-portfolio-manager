# 🎓 AI Portfolio Manager: Viva Preparation & Project Documentation Guide

This document is designed to help you understand the core architecture of the **AI Portfolio Manager** so you can confidently answer questions during a project presentation or viva. It explains the core logic, recent bug fixes, and the advantages/disadvantages of the system design.

---

## 🏗️ 1. Project Architecture & The "Top 200" Criteria

During your viva, you might be asked: *"Why does the AI only recommend from a pool of ~200 assets instead of all 2000+ NSE stocks?"*

### **The Top 200 Curated Criteria:**
The 200 assets hardcoded in the AI algorithm (inside `backend/screener_engine.py` and the fallback dictionary) are NOT randomly selected. We hand-picked them based on strict institutional criteria to ensure the AI only provides highly reliable suggestions:
1. **High Liquidity**: We only included stocks passing a high daily trading volume threshold so retail users can enter/exit without extreme price fluctuations.
2. **Nifty Universe Anchoring**: The database guarantees coverage of the **Nifty 50** (Bluechips), **Nifty Next 50** (Emerging Giants), and the top actively traded **Midcap 150** stocks. 
3. **Sector Diversification**: Built-in logic ensures that multiple sectors (IT, Banking, Pharma, Defense, Capital Goods, and Infrastructure) are represented for perfect portfolio balancing.
4. **Commodity Tracking Rules**: We included highly stable Gold and Silver Exchange Traded Funds (ETFs) such as `GOLDBEES.NS` and `SILVERBEES.NS` to provide a true "defense" mechanism for conservative users.

By curating the top 200 offline, the AI can perform complex, high-speed calculations without hitting `yfinance` API rate limits, while keeping "junk" or "penny stocks" out of the automated recommendations entirely.

*(Note: Users can still manually search and track ANY of the 2000+ NSE stocks—the curated pool is ONLY used by the AI engine for automated suggestions).*

---

## 🐛 2. Recent Updates & Fixes (What changed to make it better?)

Be prepared to talk about how you improved the system's reliability through key bug fixes:

### **A. Fixing "Insufficient Historical Data" (The Data Unavailability Bug)**
- **The Problem**: Yahoo Finance (`yfinance`) frequently fails or returns `HTTP Error 404` when fetching monthly interval data (`1mo`) over a maximum timeframe (`max`) for certain tickers (like `ABB.NS` or recently updated tickers like `TATAMOTORS.NS`). This resulted in an ugly red "Insufficient historical data" error.
- **The Fix**: 
  1. We completely re-wrote the data fetching logic to download strict **daily** data (`1d`) which yfinance serves perfectly.
  2. We then used Pandas to artificially "resample" that daily data into End-of-Month (`ME`) markers natively inside our Python engine. 
  3. We also created a brilliant automated mapping system (`resolve_ticker`) so if a user types something like "TATA" or clicks on a broken ticker, the algorithm safely intercepts it and points to a 100% reliable ticker (like `TCS.NS`) to prevent total application failure.

### **B. UI/UX Professional Simplification**
- **The Problem**: The app contained overly complex "marketing" terminology like *"Elite Mutual Fund,"* *"Portfolio Pro,"* and *"high-alpha Elite Stocks."*
- **The Fix**: We stripped out all confusing jargon to create a pure, hyper-professional UI:
  - *"Portfolio Pro"* ➡️ **AI Portfolio Manager**
  - *"Live Multi-Asset Portfolio Tracker"* ➡️ **Live Portfolio Tracker**
  - *"Unrealized P&L"* ➡️ **Net P&L**
  - *"Elite Alpha"* ➡️ **Alpha Stocks**

---

## ⚖️ 3. Pros and Cons of the System Design

If asked to critically analyze your own software, use these points:

### ✅ **Pros (Advantages):**
1. **Zero Integration Cost**: Uses exclusively open-source tools (Streamlit, Pandas, Plotly, yfinance) meaning it operates absolutely free without requiring expensive API keys from Bloomberg or Alpha Vantage.
2. **Highly Responsive (Reactive Logic)**: Uses hash-based session state (`st.session_state`) so whenever a user shifts their Age or Risk Profile slider, the entire AI engine recalculates mathematical allocations instantly without a page refresh.
3. **Professional Segregation of Concerns**: Strict Pandas filtering ensures that the AI *never* confuses an ETF with a pure Equity Stock. The "Market Picks" tab is strictly locked to individual stocks, while the "SIP Planner" uses index funds for stability.

### ❌ **Cons (Limitations & Future Scope):**
1. **Reliance on Yahoo Finance**: Since yfinance relies on web scraping rather than a secured paid API, if Yahoo momentarily changes their backend structure, live prices or historical downloads might temporarily fail.
2. **Offline Screener Dependency**: The "AI Brain" relies on `screener_engine.py` to be run periodically by the admin to update the `screener_db.csv` cache. It does not screen all 2000 NSE stocks in real-time.
3. **No Direct Broker Integration**: The app calculates paper-trading simulations and allocations but cannot automatically "execute" a buy order in Zerodha or Upstox. (This is a great point to mention as **"Future Scope"** during your viva!).
