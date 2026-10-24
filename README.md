# 🚀 Advanced AI Crypto 24-Hour Growth Predictor

An automated, machine-learning-driven cryptocurrency prediction engine designed to calculate the **probability of price growth over the next 24 hours** with continuous auto-analysis and scheduled real-time data updates.

---

## 📁 System Architecture & Directory Layout

```
crypto predictor/
├── .venv/                   # Isolated Python 3.12 virtual environment
├── config/                  # Configuration & Target asset lists
│   ├── coins.json           # Your 20 selected cryptocurrencies
│   └── settings.py          # Lookback, thresholds, update intervals
├── data/                    # Market data caches
│   ├── raw/                 # Historical OHLCV candle records
│   └── processed/           # Normalized features & indicator matrices
├── models/                  # ML/AI models & calibrated probability engines
│   └── saved_models/        # Serialized LightGBM/XGBoost model artifacts
├── src/
│   ├── collector/           # Real-time exchange data fetchers (CCXT / Binance / yfinance)
│   ├── features/            # High-signal multi-factor & technical indicator pipelines
│   ├── models/              # Probability calibrators & gradient-boosted ensembles
│   ├── analyzer/            # Automated technical & momentum market reasoning
│   ├── scheduler/           # Periodic auto-update daemon & notification dispatch
│   ├── dashboard/           # Modern Streamlit / Plotly visual analytics interface
│   └── utils/               # Logging, formatting, and mathematical utilities
├── logs/                    # Automated background execution logs
├── requirements.txt         # State-of-the-art Python dependencies
└── README.md
```

---

## ⚙️ Core Capabilities

1. **24-Hour Growth Probability Engine**:
   - Computes $P(\text{Price}_{t+24\text{h}} > \text{Price}_t)$ using an ensemble of gradient-boosted trees (LightGBM/XGBoost) with isotonic probability calibration.
   - Evaluates momentum, volatility, volume flow, exponential moving average convergences, RSI divergence, and Bollinger Band compressions.

2. **Automated Analysis Generator**:
   - Generates automated signals (Strong Buy, Moderate Buy, Neutral, Bearish).
   - Details the key drivers behind each prediction (e.g. Volume surge, Golden Cross, Oversold bounce, Volatility breakout).

3. **Auto-Update Scheduler**:
   - Periodically pulls fresh market data at configured intervals (e.g., every 15-30 mins).
   - Re-calculates predictions, updates cached stats, and logs real-time changes automatically.
