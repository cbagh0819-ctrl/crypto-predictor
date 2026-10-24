"""Cryptocurrency historical and live market data collector."""

import re
from pathlib import Path
import pandas as pd
import requests
from config.settings import RAW_DATA_DIR, LOOKBACK_CANDLES, DEFAULT_TIMEFRAME

RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

def sanitize_symbol(symbol: str) -> str:
    """Sanitize symbol string for filesystem usage."""
    return re.sub(r'[^a-zA-Z0-9]', '_', symbol)

class CryptoDataFetcher:
    """Fetches real-time and historical OHLCV data with multi-exchange fallbacks."""

    def __init__(self, exchange_id: str = "binance"):
        self.exchange_id = exchange_id
        self._exchange = None

    def fetch_ohlcv_binance_rest(self, symbol: str, interval: str = "1h", limit: int = LOOKBACK_CANDLES) -> pd.DataFrame:
        """Fetch OHLCV candles directly from Binance Public REST API."""
        clean_pair = symbol.replace("/", "").replace("-", "").upper()
        # Direct Binance endpoints
        endpoints = [
            f"https://api.binance.com/api/v3/klines?symbol={clean_pair}&interval={interval}&limit={min(limit, 1000)}",
            f"https://data-api.binance.vision/api/v3/klines?symbol={clean_pair}&interval={interval}&limit={min(limit, 1000)}"
        ]
        for url in endpoints:
            try:
                res = requests.get(url, timeout=8)
                if res.status_code == 200:
                    raw = res.json()
                    if raw and len(raw) > 0:
                        df = pd.DataFrame(raw, columns=[
                            'open_time', 'open', 'high', 'low', 'close', 'volume',
                            'close_time', 'quote_asset_volume', 'number_of_trades',
                            'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
                        ])
                        df['datetime'] = pd.to_datetime(df['open_time'], unit='ms')
                        for col in ['open', 'high', 'low', 'close', 'volume']:
                            df[col] = df[col].astype(float)
                        df['timestamp'] = df['open_time']
                        df.sort_values('datetime', inplace=True)
                        df.reset_index(drop=True, inplace=True)
                        return df[['timestamp', 'datetime', 'open', 'high', 'low', 'close', 'volume']]
            except Exception:
                continue
        return pd.DataFrame()

    def fetch_ohlcv_ccxt(self, symbol: str, timeframe: str = DEFAULT_TIMEFRAME, limit: int = LOOKBACK_CANDLES) -> pd.DataFrame:
        """Fetch OHLCV candles via CCXT."""
        try:
            if self._exchange is None:
                import ccxt
                self._exchange = ccxt.binance({'enableRateLimit': True, 'timeout': 10000})
            candles = self._exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
            if not candles:
                return pd.DataFrame()
            df = pd.DataFrame(candles, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.sort_values('datetime', inplace=True)
            df.reset_index(drop=True, inplace=True)
            return df
        except Exception:
            return pd.DataFrame()

    def fetch_ohlcv_yfinance(self, symbol: str, period: str = "60d", interval: str = "1h") -> pd.DataFrame:
        """Fallback to Yahoo Finance."""
        try:
            import yfinance as yf
            base = symbol.split('/')[0]
            yf_symbol = f"{base}-USD"
            ticker = yf.Ticker(yf_symbol)
            hist = ticker.history(period=period, interval=interval)
            if hist.empty:
                return pd.DataFrame()
            df = hist.reset_index()
            df.rename(columns={
                'Datetime': 'datetime',
                'Date': 'datetime',
                'Open': 'open',
                'High': 'high',
                'Low': 'low',
                'Close': 'close',
                'Volume': 'volume'
            }, inplace=True)
            df['timestamp'] = df['datetime'].astype('int64') // 10**6
            for col in ['open', 'high', 'low', 'close', 'volume']:
                df[col] = df[col].astype(float)
            return df[['timestamp', 'datetime', 'open', 'high', 'low', 'close', 'volume']]
        except Exception:
            return pd.DataFrame()

    def get_market_data(self, symbol: str, timeframe: str = DEFAULT_TIMEFRAME, limit: int = LOOKBACK_CANDLES, cache: bool = True) -> pd.DataFrame:
        """Fetch data across prioritized sources with caching."""
        # 1. Binance Direct REST
        df = self.fetch_ohlcv_binance_rest(symbol, interval=timeframe, limit=limit)

        # 2. CCXT
        if df.empty or len(df) < 50:
            df = self.fetch_ohlcv_ccxt(symbol, timeframe=timeframe, limit=limit)

        # 3. Yahoo Finance
        if df.empty or len(df) < 50:
            df = self.fetch_ohlcv_yfinance(symbol)

        cache_file = RAW_DATA_DIR / f"{sanitize_symbol(symbol)}.csv"
        if not df.empty and cache:
            df.to_csv(cache_file, index=False)
        elif df.empty and cache_file.exists():
            df = pd.read_csv(cache_file)
            df['datetime'] = pd.to_datetime(df['datetime'])

        return df
