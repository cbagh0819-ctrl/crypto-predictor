"""Automated Technical & Momentum Market Analysis Engine."""

import pandas as pd
from src.features.feature_builder import FeatureBuilder

class AutoAnalyzer:
    """Generates detailed market diagnostics and dynamic reasoning for predictions."""

    def __init__(self):
        self.feature_builder = FeatureBuilder()

    def generate_coin_analysis(self, symbol: str, df: pd.DataFrame, prediction_info: dict) -> dict:
        """Produces deep diagnostic analysis for the specified cryptocurrency."""
        if df.empty or len(df) < 30:
            return {
                "symbol": symbol,
                "summary": "Insufficient data to perform auto-analysis.",
                "drivers": []
            }

        features_df = self.feature_builder.calculate_technical_features(df)
        latest = features_df.iloc[-1]

        close = latest['close']
        rsi = latest['rsi_14']
        macd_hist = latest['macd_hist']
        vol_surge = latest['vol_surge_ratio']
        bb_bandwidth = latest['bb_bandwidth']
        bb_pct = latest['bb_pct']

        ema_trend = "Bullish" if latest['dist_ema_50'] > 0 else "Bearish"
        golden_cross = latest['ema_9_21_diff'] > 0

        drivers = []

        # RSI Evaluation
        if rsi < 30:
            drivers.append("⚠️ RSI indicates deeply oversold territory (potential mean-reversion bounce).")
        elif rsi > 70:
            drivers.append("⚠️ RSI indicates overbought territory (high probability of short-term pullback).")
        else:
            drivers.append(f"⚖️ RSI is neutral at {rsi:.1f}.")

        # MACD Momentum
        if macd_hist > 0:
            drivers.append("🟢 Positive MACD histogram confirms expanding upward momentum.")
        else:
            drivers.append("🔴 Negative MACD histogram suggests bearish or fading momentum.")

        # Volume Flow
        if vol_surge > 1.5:
            drivers.append(f"🔥 High volume breakout detected ({vol_surge:.1f}x higher than 24h average).")
        elif vol_surge < 0.6:
            drivers.append("📉 Below-average trading volume (consolidation phase).")

        # Volatility Squeeze
        if bb_bandwidth < 0.04:
            drivers.append("⚡ Extreme Bollinger Band squeeze detected (explosive 24h volatility move imminent).")

        # BTC Relative Strength
        rs_btc = latest.get('relative_strength_btc_24h', 0.0)
        if rs_btc > 0.04:
            drivers.append(f"💪 Strong alpha decoupling: Outperforming Bitcoin by +{rs_btc*100:.1f}% over 24h.")
        elif rs_btc < -0.05:
            drivers.append(f"⚠️ Lagging behind Bitcoin by {abs(rs_btc)*100:.1f}%.")

        btc_warning = prediction_info.get("btc_warning")
        if btc_warning:
            drivers.append(btc_warning)

        # Trend summary
        prob = prediction_info.get("growth_probability", 50.0)
        price_str = f"${close:.8f}" if close < 0.0001 else (f"${close:.4f}" if close < 1 else f"${close:,.2f}")
        summary = (
            f"{symbol} is trading at {price_str} with a 24-hour growth probability of {prob}%. "
            f"Overall trend structure is {ema_trend.upper()} with "
            f"{'bullish EMA cross' if golden_cross else 'bearish EMA pressure'}."
        )

        return {
            "symbol": symbol,
            "trend": ema_trend,
            "rsi": round(float(rsi), 1),
            "volume_surge_ratio": round(float(vol_surge), 2),
            "summary": summary,
            "key_drivers": drivers
        }
