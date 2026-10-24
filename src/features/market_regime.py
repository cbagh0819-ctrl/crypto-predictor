"""Market Regime & Bitcoin Beta Correlation Engine (Pillar 1)."""

import pandas as pd
import numpy as np
from src.collector.data_fetcher import CryptoDataFetcher

class MarketRegimeEngine:
    """Evaluates macro Bitcoin health, altcoin beta, and global crypto market regimes."""

    def __init__(self):
        self.fetcher = CryptoDataFetcher()
        self._btc_df = None

    def get_btc_data(self, refresh: bool = False) -> pd.DataFrame:
        """Fetch and cache latest BTC market data."""
        if self._btc_df is None or refresh:
            df = self.fetcher.get_market_data("BTC/USDT", timeframe="1h", limit=500)
            if not df.empty:
                df['close'] = df['close'].astype(float)
                # Compute BTC EMAs
                df['btc_ema_21'] = df['close'].ewm(span=21, adjust=False).mean()
                df['btc_ema_50'] = df['close'].ewm(span=50, adjust=False).mean()
                df['btc_return_1h'] = df['close'].pct_change(1)
                df['btc_return_24h'] = df['close'].pct_change(24)
                
                # BTC RSI
                delta = df['close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
                rs = gain / (loss + 1e-8)
                df['btc_rsi'] = 100 - (100 / (1 + rs))
                self._btc_df = df
        return self._btc_df

    def get_btc_regime(self) -> dict:
        """Classify current overall Bitcoin market regime."""
        btc_df = self.get_btc_data()
        if btc_df is None or btc_df.empty or len(btc_df) < 50:
            return {
                "regime": "NEUTRAL",
                "btc_price": 0.0,
                "btc_24h_change": 0.0,
                "btc_rsi": 50.0,
                "risk_multiplier": 1.0,
                "warning": None
            }

        latest = btc_df.iloc[-1]
        price = float(latest['close'])
        ema_21 = float(latest['btc_ema_21'])
        ema_50 = float(latest['btc_ema_50'])
        ret_24h = float(latest['btc_return_24h'] * 100)
        rsi = float(latest['btc_rsi'])

        # Classify regime
        if price > ema_21 and ema_21 > ema_50 and ret_24h > 1.0:
            regime = "STRONG_BULLISH"
            risk_multiplier = 1.10 # Boost altcoin confidence
            warning = None
        elif price > ema_50:
            regime = "MODERATE_BULLISH"
            risk_multiplier = 1.04
            warning = None
        elif price < ema_21 and ret_24h < -3.0:
            regime = "SEVERE_DOWNTREND"
            risk_multiplier = 0.80 # Dampen altcoin buys during violent BTC selloffs
            warning = "⚠️ Bitcoin is experiencing severe downward pressure. Altcoins carry high liquidation risk."
        elif price < ema_50:
            regime = "BEARISH_PRESSURE"
            risk_multiplier = 0.90
            warning = "⚠️ Bitcoin trading below 50 EMA. Broad market drag detected."
        else:
            regime = "CHOPPY_SIDEWAYS"
            risk_multiplier = 0.98
            warning = None

        return {
            "regime": regime,
            "btc_price": price,
            "btc_24h_change": round(ret_24h, 2),
            "btc_rsi": round(rsi, 1),
            "risk_multiplier": risk_multiplier,
            "warning": warning
        }

    def compute_altcoin_btc_features(self, coin_df: pd.DataFrame) -> pd.DataFrame:
        """Merge Bitcoin market features with an altcoin's OHLCV history."""
        btc_df = self.get_btc_data()
        if btc_df is None or btc_df.empty:
            return coin_df

        data = coin_df.copy()
        # Merge on timestamp or index
        btc_sub = btc_df[['timestamp', 'btc_return_1h', 'btc_return_24h', 'btc_rsi']].copy()
        merged = pd.merge_asof(data.sort_values('timestamp'), btc_sub.sort_values('timestamp'), on='timestamp', direction='backward')

        # Compute Relative Strength to BTC: Coin return minus BTC return
        if 'return_24h' in merged.columns and 'btc_return_24h' in merged.columns:
            merged['relative_strength_btc_24h'] = merged['return_24h'] - merged['btc_return_24h']
        else:
            merged['relative_strength_btc_24h'] = 0.0

        return merged
