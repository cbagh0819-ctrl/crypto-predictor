"""Advanced ML Model Engine for 24h Crypto Growth Probability Prediction."""

from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.calibration import CalibratedClassifierCV
from config.settings import MODELS_DIR, PROBABILITY_THRESHOLDS
from src.features.feature_builder import FeatureBuilder
from src.features.market_regime import MarketRegimeEngine
from src.collector.data_fetcher import sanitize_symbol

MODELS_DIR.mkdir(parents=True, exist_ok=True)

class CryptoPredictorEngine:
    """Ensemble Probabilistic Predictor with calibration for 24h positive growth."""

    def __init__(self):
        self.feature_builder = FeatureBuilder()
        self.feature_names = self.feature_builder.get_feature_names()
        self.regime_engine = MarketRegimeEngine()

    def _get_model_path(self, symbol: str) -> Path:
        return MODELS_DIR / f"{sanitize_symbol(symbol)}_model.joblib"

    def train_or_update_model(self, symbol: str, df: pd.DataFrame):
        """Train or update a calibrated probability model using historical candles."""
        if len(df) < 150:
            return None

        features_df = self.feature_builder.calculate_technical_features(df)
        # Drop rows where target is NaN (the last 24 rows) or warmup rows
        valid_df = features_df.dropna(subset=self.feature_names + ['target_growth']).copy()

        if len(valid_df) < 100:
            return None

        X = valid_df[self.feature_names].values
        y = valid_df['target_growth'].values

        # Base classifier: HistGradientBoosting or LightGBM
        base_clf = HistGradientBoostingClassifier(
            max_iter=120,
            learning_rate=0.05,
            max_leaf_nodes=31,
            min_samples_leaf=20,
            random_state=42
        )

        # Calibrate probabilities using sigmoid / isotonic
        cv_splits = min(5, max(2, len(valid_df) // 50))
        calibrated_model = CalibratedClassifierCV(estimator=base_clf, method='sigmoid', cv=cv_splits)
        calibrated_model.fit(X, y)

        model_path = self._get_model_path(symbol)
        joblib.dump(calibrated_model, model_path)
        return calibrated_model

    def predict_growth_probability(self, symbol: str, df: pd.DataFrame) -> dict:
        """Calculate chance of positive price growth in next 24 hours."""
        if df.empty or len(df) < 50:
            return {
                "symbol": symbol,
                "growth_probability": 0.50,
                "confidence": "Low",
                "signal": "Neutral",
                "error": "Insufficient market data"
            }

        features_df = self.feature_builder.calculate_technical_features(df)
        latest_row = features_df.iloc[-1:]
        X_latest = latest_row[self.feature_names].fillna(0).values

        model_path = self._get_model_path(symbol)
        model = None
        if model_path.exists():
            try:
                loaded = joblib.load(model_path)
                # Check feature count compatibility
                if hasattr(loaded, "n_features_in_") and loaded.n_features_in_ == len(self.feature_names):
                    model = loaded
                elif hasattr(loaded, "estimator") and hasattr(loaded.estimator, "n_features_in_") and loaded.estimator.n_features_in_ == len(self.feature_names):
                    model = loaded
            except Exception:
                model = None

        if model is None:
            model = self.train_or_update_model(symbol, df)

        if model is not None:
            probs = model.predict_proba(X_latest)[0]
            # Probability of class 1 (growth > 0)
            p_growth = float(probs[1]) if len(probs) > 1 else float(probs[0])
        else:
            # Fallback heuristic momentum score if model cannot fit
            rsi = latest_row['rsi_14'].values[0] if 'rsi_14' in latest_row else 50
            macd_hist = latest_row['macd_hist'].values[0] if 'macd_hist' in latest_row else 0
            p_growth = 0.50 + (0.15 if rsi < 40 else (-0.15 if rsi > 70 else 0)) + (0.10 if macd_hist > 0 else -0.10)
            p_growth = max(0.05, min(0.95, p_growth))

        # Apply Bitcoin Market Regime Gatekeeper Multiplier
        btc_regime = self.regime_engine.get_btc_regime()
        if symbol != "BTC/USDT":
            multiplier = btc_regime.get("risk_multiplier", 1.0)
            p_growth = p_growth * multiplier
            p_growth = max(0.05, min(0.95, p_growth))

        # Assign signal based on calibrated thresholds
        if p_growth >= PROBABILITY_THRESHOLDS["strong_buy"]:
            signal = "Strong Bullish 🚀"
        elif p_growth >= PROBABILITY_THRESHOLDS["moderate_buy"]:
            signal = "Moderate Bullish 📈"
        elif p_growth >= PROBABILITY_THRESHOLDS["neutral"]:
            signal = "Neutral / Sideways ⚖️"
        else:
            signal = "Bearish / Caution 🔻"

        confidence_score = abs(p_growth - 0.5) * 200 # 0% to 100% confidence divergence

        current_price = float(df['close'].iloc[-1])
        change_24h = float(df['close'].pct_change(min(24, len(df)-1)).iloc[-1] * 100)

        return {
            "symbol": symbol,
            "current_price": current_price,
            "change_24h_pct": round(change_24h, 2),
            "growth_probability": round(p_growth * 100, 1), # as percentage
            "confidence_score": round(confidence_score, 1),
            "signal": signal,
            "btc_regime": btc_regime.get("regime", "NEUTRAL"),
            "btc_warning": btc_regime.get("warning"),
            "timestamp": df['datetime'].iloc[-1].isoformat() if 'datetime' in df else str(pd.Timestamp.now())
        }
