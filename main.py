"""Main Entry Point for AI Crypto Predictor."""

import argparse
import json
import subprocess
import sys
from pathlib import Path

# Fix Windows console UTF-8 output
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from config.settings import COINS_CONFIG_PATH, get_tracked_symbols
from src.scheduler.auto_updater import AutoUpdatePipeline
from src.utils.logger import logger

def update_coins_file(coins: list[str]):
    """Update config/coins.json with user's coin list."""
    formatted = [c.upper() if "/" in c else f"{c.upper()}/USDT" for c in coins]
    data = {
        "description": "List of 20 cryptocurrencies to monitor, analyze, and predict 24h growth.",
        "symbols": formatted
    }
    with open(COINS_CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    logger.info(f"Updated tracked crypto list with {len(formatted)} coins.")
    print(f"✅ Successfully updated tracked list to {len(formatted)} coins: {', '.join(formatted)}")

def main():
    parser = argparse.ArgumentParser(description="AI Crypto 24h Growth Predictor")
    parser.add_argument("--update", action="store_true", help="Run a full auto-analysis and update cycle now")
    parser.add_argument("--daemon", action="store_true", help="Start continuous scheduled auto-update daemon")
    parser.add_argument("--interval", type=int, default=10, help="Scheduler refresh interval in minutes (default: 10)")
    parser.add_argument("--ui", action="store_true", help="Launch the pixel-perfect neon web app at http://localhost:8000")
    parser.add_argument("--dashboard", action="store_true", help="Launch interactive web UI")
    parser.add_argument("--port", type=int, default=8000, help="Web server port (default: 8000)")
    parser.add_argument("--list", action="store_true", help="Show currently configured cryptocurrencies")
    parser.add_argument("--set-coins", nargs="+", help="Replace tracked cryptocurrencies with new list")

    args = parser.parse_args()

    if args.set_coins:
        update_coins_file(args.set_coins)
        return

    if args.list:
        coins = get_tracked_symbols()
        print(f"Tracked Cryptocurrencies ({len(coins)}):")
        for i, c in enumerate(coins, 1):
            print(f"  {i}. {c}")
        return

    if args.ui or args.dashboard:
        import uvicorn
        print(f"\n🚀 Launching Crypto Watchlist UI at http://localhost:{args.port} ...")
        print(f"Press CTRL+C to stop.\n")
        uvicorn.run("src.dashboard.web_server:app", host="127.0.0.1", port=args.port, reload=False)
        return

    if args.daemon:
        pipeline = AutoUpdatePipeline()
        pipeline.start_scheduler_loop(interval_minutes=args.interval)
        return

    # Default action: run one update cycle
    pipeline = AutoUpdatePipeline()
    results = pipeline.run_update_cycle()
    print("\n--- 🚀 Top 24h Growth Probability Rankings ---")
    for r in results[:10]:
        print(f"{r['symbol']:<12} | Price: ${r['current_price']:<10.4f} | 24h Growth Chance: {r['growth_probability']}% | {r['signal']}")

if __name__ == "__main__":
    main()
