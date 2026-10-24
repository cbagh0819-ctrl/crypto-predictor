"""Crypto Market Sentiment & Fear/Greed Index Engine (Pillar 4)."""

import time
import requests

class SentimentEngine:
    """Tracks global crypto sentiment and macro psychology."""

    _cache = {"value": 50, "sentiment": "Neutral", "last_updated": 0}

    @classmethod
    def get_market_sentiment(cls) -> dict:
        now = time.time()
        # Cache for 2 hours
        if now - cls._cache["last_updated"] < 7200:
            return cls._cache

        try:
            r = requests.get("https://api.alternative.me/fng/?limit=1", timeout=4)
            if r.status_code == 200:
                item = r.json().get("data", [{}])[0]
                val = int(item.get("value", 50))
                sent = item.get("value_classification", "Neutral")
                cls._cache = {
                    "value": val,
                    "sentiment": sent,
                    "last_updated": now
                }
        except Exception:
            pass

        return cls._cache
