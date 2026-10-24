# ⚡ AI Crypto 24-Hour Growth Predictor & Watchlist

[![Live Website](https://img.shields.io/badge/Live%20Website-GitHub%20Pages-brightgreen?style=for-the-badge&logo=github)](https://cbagh0819-ctrl.github.io/crypto-predictor/)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Python 3.12](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

> **Live Production Website:**  
> 👉 **[https://cbagh0819-ctrl.github.io/crypto-predictor/](https://cbagh0819-ctrl.github.io/crypto-predictor/)**

An institutional-grade, quantitative cryptocurrency prediction system designed to calculate the **calibrated probability of price growth over the next 24 hours** using gradient-boosted decision trees, Bitcoin macro regime gatekeeping, derivatives funding rates, and scheduled 10-minute automated updates.

---

## 🔑 Operator Access Credentials

Access the restricted terminal via the web interface:

| Field | Value |
|---|---|
| **Operator ID** | `Admin` |
| **Security Key** | `Admin@123` |

---

## 🌐 Live Website Features

1. **5-Second High-Tech Loading Screen**:
   - Neural model booting diagnostics with an animated 0% to 100% progress countdown.
2. **Restricted Operator Login Portal**:
   - High-contrast black & white luxury interface with password reveal toggle and input validation.
3. **`WELCOME BOSS CHARLO !` Executive Dashboard**:
   - Real-time live ticking clock (`hh:mm:ss AM/PM`) and dynamic calendar date.
   - **10-Minute Auto-Sync Countdown** (`AUTO-SYNC: MM:SS`) with background re-analysis.
   - **Price (INR)**: Converted Rupee valuations with up to 8-decimal precision for micro-coins.
   - **Chance of Rise (24 Hrs)**: Color-coded probability badges (High, Medium, Low).
   - **Tradable Signals (`Invest?`)**: High-conviction `YES` (solid white) vs `NO` (dark outline).
   - **Suggested Holding Windows**: Dynamic holding recommendations (`1-2 Hrs`, `2-4 Hrs`, `4-6 Hrs`, `6-12 Hrs`, `-`).
   - **Interactive AI Diagnostic Drawers**: Click any coin row to inspect real-time RSI, MACD, Volume Surge ratios, Futures Funding Rates, and Long/Short positioning.

---

## 🧠 7-Pillar Quantitative Machine Learning Engine

| # | Pillar | Description |
|:---:|---|---|
| **1** | **Bitcoin Beta & Macro Regime Gatekeeper** | Tracks BTC 24h trend and EMA cross status; dynamically dampens altcoin signals during BTC market downturns to protect capital. |
| **2** | **Binance Futures Funding Rates & Long/Short Ratio** | Directly pulls exchange derivatives metrics to detect short squeeze opportunities ($< -0.01\%$) and long liquidation traps. |
| **3** | **Multi-Timeframe Confluence (1h + 4h)** | Evaluates 4-hour macro trend direction (above/below 50 EMA) alongside 1-hour micro entry timing. |
| **4** | **Crypto Fear & Greed Index Integration** | Adjusts mean-reversion and momentum sensitivities based on macro market psychology (Alternative.me API). |
| **5** | **Volatility-Adjusted Target Barriers** | Utilizes Normalized ATR (Average True Range) barrier hurdles instead of noisy $\pm 0.01\%$ price ticks. |
| **6** | **Prediction Accountability Ledger & Win-Rate Tracker** | Logs every prediction and verifies real-world outcomes 24 hours later to compute an audited rolling win rate. |
| **7** | **Meme & Volume Anomaly Surge Detector** | Specialized anomaly detector flagging volume explosions $> 2.5\times$ normal baseline across tokens like PEPE, BONK, BOME, TURBO, and SHIB. |

---

## 📁 System Architecture & Directory Layout

```
crypto-predictor/
├── docs/                        # Public GitHub Pages website build
│   ├── index.html               # Frontend multi-screen SPA
│   ├── style.css                # Luxury Black & White monochrome stylesheet
│   ├── app.js                   # Client controller & price resolution engine
│   └── data/                    # Live predictions JSON feed
├── config/
│   ├── coins.json               # Configured portfolio assets & sector tags
│   └── settings.py              # Update intervals, lookbacks, thresholds
├── data/
│   ├── raw/                     # Cached OHLCV historical candle records
│   └── processed/               # Predictions snapshot & audit ledger
├── models/
│   └── saved_models/            # 23-factor calibrated LightGBM/GradientBoosting artifacts
├── src/
│   ├── collector/               # Binance REST, CCXT, yfinance, and derivatives fetchers
│   ├── features/                # Technical indicators, BTC beta, sentiment engines
│   ├── models/                  # Calibrated probability predictor & audit tracker
│   ├── analyzer/                # Automated market reasoning & catalyst generator
│   ├── scheduler/               # 10-minute auto-update background worker
│   ├── dashboard/               # FastAPI server & Streamlit alternative UI
│   └── utils/                   # Structured logging with file rotation
├── main.py                      # Unified CLI & server launcher
├── Run_Crypto_Predictor.bat     # One-click desktop launcher (starts server & opens browser)
├── Run_Silent_Background.vbs    # Hidden background runner
├── Stop_Crypto_Predictor.bat    # One-click process stopper
├── Dockerfile                   # Container deployment configuration
├── Procfile                     # Cloud hosting (Render / Railway) configuration
├── requirements.txt             # Locked Python dependencies
└── README.md
```

---

## 🖱️ Local Execution (Zero Terminal Needed)

1. **One-Click Quick Launcher**:
   - Double-click [`Run_Crypto_Predictor.bat`](Run_Crypto_Predictor.bat).
   - Automatically starts the FastAPI engine and opens your browser to `http://localhost:8000`.

2. **Completely Silent Background Launcher**:
   - Double-click [`Run_Silent_Background.vbs`](Run_Silent_Background.vbs).
   - Starts the AI engine in the background and opens the website with zero terminal windows visible.

3. **Stop Server**:
   - Double-click [`Stop_Crypto_Predictor.bat`](Stop_Crypto_Predictor.bat).

---

## 💻 CLI Commands

Run manually from the terminal using the virtual environment:

```powershell
# Launch the web interface on port 8000
.\.venv\Scripts\python.exe main.py --ui --port 8000

# Run a single prediction & auto-analysis cycle
.\.venv\Scripts\python.exe main.py --update

# Show list of tracked cryptocurrencies
.\.venv\Scripts\python.exe main.py --list

# Launch alternative Streamlit dashboard
.\.venv\Scripts\python.exe main.py --dashboard
```

---

## 📡 REST API Documentation

When running locally or self-hosted, access the interactive Swagger OpenAPI documentation at:
👉 **`http://localhost:8000/docs`**

- `GET /api/predictions`: Returns current rankings, INR/USD prices, signals, and macro scores.
- `POST /api/login`: Validates operator credentials (`Admin` / `Admin@123`).
- `GET /api/health`: Health-check endpoint for uptime monitors.
- `POST /api/update`: Triggers an immediate re-fetch and model inference cycle.
- `GET /api/export/csv`: Downloads live prediction matrix as a CSV file.

---

## 📄 License
This project is open-source and available under the [MIT License](LICENSE).
