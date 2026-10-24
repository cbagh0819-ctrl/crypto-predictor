"""Feature Engineering for 24h Crypto Growth Prediction."""

import numpy as np
import pandas as pd
from config.settings import PREDICTION_HORIZON_HOURS

class FeatureBuilder:
    """Calculates quantitative features and prepares training / inference datasets."""

    def __init__(self, horizon: int = PREDICTION_HORIZON_HOURS):
        self.horizon = horizon

    def calculate_technical_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Compute advanced technical indicators and momentum signals."""
        data = df.copy()
        data.sort_values('datetime', inplace=True)
        data.reset_index(drop=True, inplace=True)

        close = data['close']
        high = data['high']
        low = data['low']
        volume = data['volume']

        # 1. Exponential Moving Averages & Distances
        for span in [9, 21, 50, 200]:
            ema = close.ewm(span=span, adjust=False).mean()
            data[f'ema_{span}'] = ema
            data[f'dist_ema_{span}'] = (close - ema) / (ema + 1e-8)

        data['ema_9_21_diff'] = (data['ema_9'] - data['ema_21']) / (data['ema_21'] + 1e-8)
        data['ema_21_50_diff'] = (data['ema_21'] - data['ema_50']) / (data['ema_50'] + 1e-8)

        # 2. MACD
        ema12 = close.ewm(span=12, adjust=False).mean()
        ema26 = close.ewm(span=26, adjust=False).mean()
        macd_line = ema12 - ema26
        macd_signal = macd_line.ewm(span=9, adjust=False).mean()
        data['macd'] = macd_line / (close + 1e-8)
        data['macd_signal'] = macd_signal / (close + 1e-8)
        data['macd_hist'] = (macd_line - macd_signal) / (close + 1e-8)

        # 3. Relative Strength Index (RSI - 14)
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / (loss + 1e-8)
        data['rsi_14'] = 100 - (100 / (1 + rs))

        # 4. Bollinger Bands (20, 2)
        sma20 = close.rolling(window=20).mean()
        std20 = close.rolling(window=20).std()
        upper_bb = sma20 + (std20 * 2)
        lower_bb = sma20 - (std20 * 2)
        data['bb_bandwidth'] = (upper_bb - lower_bb) / (sma20 + 1e-8)
        data['bb_pct'] = (close - lower_bb) / ((upper_bb - lower_bb) + 1e-8)

        # 5. Average True Range (ATR - 14)
        tr1 = high - low
        tr2 = (high - close.shift(1)).abs()
        tr3 = (low - close.shift(1)).abs()
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        data['atr_14'] = tr.rolling(window=14).mean()
        data['natr_14'] = data['atr_14'] / (close + 1e-8)

        # 6. Volume Signals
        vol_sma24 = volume.rolling(window=24).mean()
        data['vol_surge_ratio'] = volume / (vol_sma24 + 1e-8)

        # 7. Past Returns (Multi-horizon)
        for h in [1, 3, 6, 12, 24]:
            data[f'return_{h}h'] = close.pct_change(h)

        # 8. Volatility (Rolling standard deviation of returns)
        data['volatility_24h'] = data['return_1h'].rolling(window=24).std()

        # 9. Target for 24h prediction (Only for training)
        future_close = close.shift(-self.horizon)
        data['target_return_24h'] = (future_close - close) / close
        data['target_growth'] = (data['target_return_24h'] > 0).astype(int)

        # 10. Enrich with Bitcoin Beta features if available
        try:
            from src.features.market_regime import MarketRegimeEngine
            regime_engine = MarketRegimeEngine()
            data = regime_engine.compute_altcoin_btc_features(data)
        except Exception:
            data['relative_strength_btc_24h'] = 0.0
            data['btc_return_24h'] = 0.0
            data['btc_rsi'] = 50.0

        for col in ['relative_strength_btc_24h', 'btc_return_24h', 'btc_rsi']:
            if col not in data.columns:
                data[col] = 0.0

        return data

    def get_feature_names(self) -> list[str]:
        """Returns the list of predictive features used for the ML models."""
        return [
            'dist_ema_9', 'dist_ema_21', 'dist_ema_50', 'dist_ema_200',
            'ema_9_21_diff', 'ema_21_50_diff',
            'macd', 'macd_signal', 'macd_hist',
            'rsi_14', 'bb_bandwidth', 'bb_pct', 'natr_14',
            'vol_surge_ratio',
            'return_1h', 'return_3h', 'return_6h', 'return_12h', 'return_24h',
            'volatility_24h',
            'relative_strength_btc_24h', 'btc_return_24h', 'btc_rsi'
        ]
