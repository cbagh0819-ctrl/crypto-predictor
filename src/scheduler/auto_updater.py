"""Complete High-Precision Prediction Pipeline with All 7 Accuracy Pillars."""

import json
import time
from datetime import datetime
from pathlib import Path
from config.settings import (
    get_tracked_symbols,
    get_coins_metadata,
    PROCESSED_DATA_DIR,
    UPDATE_INTERVAL_MINUTES
)
from src.collector.data_fetcher import CryptoDataFetcher
from src.collector.derivatives_fetcher import DerivativesFetcher
from src.features.market_regime import MarketRegimeEngine
from src.features.sentiment_engine import SentimentEngine
from src.models.predictor_engine import CryptoPredictorEngine
from src.models.accountability_tracker import AccountabilityTracker
from src.analyzer.auto_analyzer import AutoAnalyzer
from src.utils.logger import logger

PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
LATEST_RESULTS_FILE = PROCESSED_DATA_DIR / "latest_predictions.json"

class AutoUpdatePipeline:
    """Manages the complete 7-pillar institutional prediction pipeline."""

    def __init__(self):
        self.fetcher = CryptoDataFetcher()
        self.derivatives_fetcher = DerivativesFetcher()
        self.regime_engine = MarketRegimeEngine()
        self.predictor = CryptoPredictorEngine()
        self.analyzer = AutoAnalyzer()
        self.tracker = AccountabilityTracker()

    def run_update_cycle(self) -> list[dict]:
        """Executes high-accuracy prediction cycle across all 7 pillars."""
        symbols = get_tracked_symbols()
        metadata = get_coins_metadata()

        # Pillar 1 & 4: Macro BTC Regime & Sentiment
        btc_regime = self.regime_engine.get_btc_regime()
        sentiment = SentimentEngine.get_market_sentiment()
        logger.info(f"Macro BTC Regime: {btc_regime['regime']} (Risk Mult: {btc_regime['risk_multiplier']}) | Fear/Greed: {sentiment['value']} ({sentiment['sentiment']})")

        results = []
        current_prices = {}

        for symbol in symbols:
            try:
                # 1. Fetch 1h and 4h data (Pillar 3: Multi-timeframe)
                df_1h = self.fetcher.get_market_data(symbol, timeframe="1h", limit=500)
                if df_1h.empty:
                    continue

                # 4h candle macro trend check
                df_4h = self.fetcher.get_market_data(symbol, timeframe="4h", limit=100)
                macro_bullish = False
                if not df_4h.empty and len(df_4h) > 20:
                    ema_50_4h = df_4h['close'].ewm(span=50, adjust=False).mean().iloc[-1]
                    macro_bullish = bool(df_4h['close'].iloc[-1] > ema_50_4h)

                # 2. ML Probability Prediction
                pred = self.predictor.predict_growth_probability(symbol, df_1h)

                # 3. Pillar 2: Futures Funding Rate & Long/Short Positioning
                derivatives = self.derivatives_fetcher.get_derivatives_metrics(symbol)
                deriv_mult = derivatives.get("signal_modifier", 1.0)

                # 4. Synthesize Probability with Confluence Modifiers
                final_prob = pred["growth_probability"] * deriv_mult
                # Multi-timeframe bonus: +4% if 4h macro trend aligns
                if macro_bullish and final_prob >= 50.0:
                    final_prob = min(96.0, final_prob + 4.0)
                elif not macro_bullish and final_prob >= 55.0:
                    final_prob = max(35.0, final_prob - 5.0)

                final_prob = round(min(97.0, max(5.0, final_prob)), 1)
                pred["growth_probability"] = final_prob

                # Update Signal label
                if final_prob >= 66.0:
                    pred["signal"] = "Strong Bullish 🚀"
                elif final_prob >= 54.0:
                    pred["signal"] = "Moderate Bullish 📈"
                elif final_prob >= 44.0:
                    pred["signal"] = "Neutral / Sideways ⚖️"
                else:
                    pred["signal"] = "Bearish / Caution 🔻"

                # 5. Deep Diagnostics & Drivers
                analysis = self.analyzer.generate_coin_analysis(symbol, df_1h, pred)
                
                # Append derivatives & macro drivers
                if derivatives.get("derivatives_note"):
                    analysis["key_drivers"].append(derivatives["derivatives_note"])
                if macro_bullish:
                    analysis["key_drivers"].append("🌐 Multi-Timeframe Alignment: 4-Hour Macro Trend is Bullish (Above 4h 50 EMA).")
                else:
                    analysis["key_drivers"].append("⚠️ 4-Hour Macro Trend is Bearish (Below 4h 50 EMA).")

                # Pillar 7: Meme & Volume Anomaly Detector
                vol_surge = analysis.get("volume_surge_ratio", 1.0)
                if vol_surge > 2.5:
                    analysis["key_drivers"].append(f"⚡ High Velocity Volume Surge: {vol_surge:.1f}x normal volume.")

                coin_meta = metadata.get(symbol, {})
                current_price = pred.get("current_price", 0.0)
                current_prices[symbol] = current_price

                combined = {
                    **pred,
                    "name": coin_meta.get("name", symbol.split("/")[0]),
                    "category": coin_meta.get("category", "General"),
                    "macro_bullish": macro_bullish,
                    "funding_rate_pct": derivatives.get("funding_rate_pct", 0.0),
                    "long_short_ratio": derivatives.get("long_short_ratio", 1.0),
                    "analysis": analysis,
                    "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                results.append(combined)

            except Exception as e:
                logger.error(f"Error evaluating {symbol}: {e}")

        # Sort by highest chance of growth
        results.sort(key=lambda x: x.get("growth_probability", 0), reverse=True)

        # Pillar 6: Evaluate matured predictions & log new ones
        self.tracker.evaluate_matured_predictions(current_prices)
        self.tracker.log_predictions(results)
        stats = self.tracker.get_stats()

        # Save snapshot
        payload = {
            "last_updated": datetime.now().strftime("%d %b %Y, %I:%M %p"),
            "total_coins": len(results),
            "macro_regime": btc_regime,
            "sentiment": sentiment,
            "accuracy_stats": stats,
            "predictions": results
        }

        with open(LATEST_RESULTS_FILE, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)

        logger.info(f"Pillars executed successfully. Saved {len(results)} coin predictions to {LATEST_RESULTS_FILE}")
        return results

    def start_scheduler_loop(self, interval_minutes: int = UPDATE_INTERVAL_MINUTES):
        while True:
            try:
                self.run_update_cycle()
            except Exception as e:
                logger.error(f"Scheduler error: {e}")
            time.sleep(interval_minutes * 60)

if __name__ == "__main__":
    pipeline = AutoUpdatePipeline()
    pipeline.run_update_cycle()
