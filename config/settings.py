"""Configuration settings for the Crypto 24h Growth Predictor."""

import os
from pathlib import Path
import json
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
MODELS_DIR = BASE_DIR / "models" / "saved_models"
LOGS_DIR = BASE_DIR / "logs"
CONFIG_DIR = BASE_DIR / "config"

COINS_CONFIG_PATH = CONFIG_DIR / "coins.json"

def get_coins_metadata() -> dict:
    """Return dictionary of symbol -> {name, category}."""
    if COINS_CONFIG_PATH.exists():
        try:
            with open(COINS_CONFIG_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                coins = data.get("coins", [])
                return {c["symbol"]: c for c in coins}
        except Exception:
            pass
    return {}

def get_tracked_symbols() -> list[str]:
    """Load the configured list of cryptocurrencies."""
    if COINS_CONFIG_PATH.exists():
        try:
            with open(COINS_CONFIG_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("symbols", [])
        except Exception:
            pass
    return [
        "ARB/USDT", "ADA/USDT", "POL/USDT", "HBAR/USDT", "XLM/USDT",
        "FET/USDT", "JUP/USDT", "RAY/USDT", "SEI/USDT", "ROSE/USDT",
        "VIRTUAL/USDT", "PEPE/USDT", "BONK/USDT", "SHIB/USDT", "BOME/USDT", "TURBO/USDT"
    ]

# Timeframe & Horizon Configurations
DEFAULT_TIMEFRAME = os.getenv("DEFAULT_TIMEFRAME", "1h")
PREDICTION_HORIZON_HOURS = int(os.getenv("PREDICTION_HORIZON_HOURS", "24"))
LOOKBACK_CANDLES = int(os.getenv("LOOKBACK_CANDLES", "1000"))
UPDATE_INTERVAL_MINUTES = int(os.getenv("UPDATE_INTERVAL_MINUTES", "10"))  # Exactly 10 minutes auto-update
SERVER_PORT = int(os.getenv("PORT", "8000"))

# Probability threshold labels
PROBABILITY_THRESHOLDS = {
    "strong_buy": 0.66,
    "moderate_buy": 0.54,
    "neutral": 0.44,
    "bearish": 0.00
}
