"""Binance Futures Derivatives Data Fetcher (Funding Rate & Long/Short Sentiment)."""

import requests

class DerivativesFetcher:
    """Pulls live funding rates and institutional/retail long-short positioning."""

    def __init__(self):
        self.base_url = "https://fapi.binance.com"

    def get_derivatives_metrics(self, symbol: str) -> dict:
        """Fetch funding rate and long/short ratio for a crypto pair."""
        clean = symbol.replace("/", "").replace("-", "").upper()
        # For meme coins, Binance futures often uses 1000PEPEUSDT or 1000BONKUSDT
        candidates = [clean, f"1000{clean}"]

        funding_rate = 0.0001
        long_short_ratio = 1.0

        for cand in candidates:
            try:
                # 1. Funding Rate
                r1 = requests.get(f"{self.base_url}/fapi/v1/premiumIndex?symbol={cand}", timeout=3)
                if r1.status_code == 200:
                    data1 = r1.json()
                    funding_rate = float(data1.get("lastFundingRate", 0.0))
                    
                    # 2. Long/Short Account Ratio
                    r2 = requests.get(f"{self.base_url}/futures/data/globalLongShortAccountRatio?symbol={cand}&period=1h&limit=1", timeout=3)
                    if r2.status_code == 200:
                        data2 = r2.json()
                        if data2 and len(data2) > 0:
                            long_short_ratio = float(data2[0].get("longShortRatio", 1.0))
                    break
            except Exception:
                continue

        # Derivatives interpretation & signal modifiers
        signal_modifier = 1.0
        derivatives_note = None

        if funding_rate < -0.0002: # Negative funding: Short squeeze setup
            signal_modifier = 1.08
            derivatives_note = f"🔥 Short Squeeze Alert: Negative funding ({funding_rate*100:.3f}%). Bears paying longs."
        elif funding_rate > 0.0005: # Extreme positive funding: Long flush risk
            signal_modifier = 0.90
            derivatives_note = f"⚠️ Overcrowded Longs: High funding ({funding_rate*100:.3f}%). Long liquidation risk."
        elif long_short_ratio > 2.5:
            signal_modifier = 0.93
            derivatives_note = f"⚠️ Retail Heavily Long (Ratio: {long_short_ratio:.2f}). Potential liquidity trap."

        return {
            "symbol": symbol,
            "funding_rate_pct": round(funding_rate * 100, 4),
            "long_short_ratio": round(long_short_ratio, 2),
            "signal_modifier": signal_modifier,
            "derivatives_note": derivatives_note
        }
