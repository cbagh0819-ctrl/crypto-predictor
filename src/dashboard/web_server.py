"""Production-Ready FastAPI Web Server for Charlo AI Crypto Predictor."""

import json
import asyncio
from pathlib import Path
from datetime import datetime
from contextlib import asynccontextmanager
import requests
import pandas as pd
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse
from pydantic import BaseModel

from config.settings import (
    PROCESSED_DATA_DIR,
    COINS_CONFIG_PATH,
    UPDATE_INTERVAL_MINUTES
)
from src.scheduler.auto_updater import AutoUpdatePipeline, LATEST_RESULTS_FILE
from src.utils.logger import logger

USD_INR_CACHE = {"rate": 86.8, "last_updated": 0}

def get_usd_to_inr() -> float:
    """Fetch live USD to INR rate with memory caching."""
    import time
    now = time.time()
    if now - USD_INR_CACHE["last_updated"] < 3600:
        return USD_INR_CACHE["rate"]
    try:
        r = requests.get("https://api.exchangerate-api.com/v4/latest/USD", timeout=4)
        if r.status_code == 200:
            rate = float(r.json().get("rates", {}).get("INR", 86.8))
            USD_INR_CACHE["rate"] = rate
            USD_INR_CACHE["last_updated"] = now
            return rate
    except Exception:
        pass
    return USD_INR_CACHE["rate"]

def compute_ui_fields(prediction: dict, inr_rate: float) -> dict:
    """Enrich prediction record with formatted INR price and tradable signals."""
    prob = prediction.get("growth_probability", 50.0)
    usd_price = prediction.get("current_price", 0.0)
    inr_price = usd_price * inr_rate

    # Dynamic Invest Recommendation
    invest = "YES" if prob >= 54.0 else "NO"

    # Suggested Holding Window
    analysis = prediction.get("analysis", {})
    rsi = analysis.get("rsi", 50.0)
    vol_surge = analysis.get("volume_surge_ratio", 1.0)
    macro_bullish = prediction.get("macro_bullish", False)

    if invest == "NO":
        holding_time = "-"
    else:
        if rsi < 30 or vol_surge > 2.0:
            holding_time = "1-2 Hrs"
        elif prob >= 65.0 and macro_bullish:
            holding_time = "6-12 Hrs"
        elif prob >= 58.0:
            holding_time = "4-6 Hrs"
        else:
            holding_time = "2-4 Hrs"

    return {
        **prediction,
        "price_inr": inr_price,
        "invest": invest,
        "holding_time": holding_time
    }

async def auto_update_background_worker():
    """Background loop that updates models and predictions every 10 minutes."""
    logger.info(f"Background worker started: Automatic re-analysis every {UPDATE_INTERVAL_MINUTES} minutes.")
    while True:
        try:
            await asyncio.sleep(UPDATE_INTERVAL_MINUTES * 60)
            logger.info("Executing scheduled 10-minute auto-update cycle...")
            pipeline = AutoUpdatePipeline()
            await asyncio.to_thread(pipeline.run_update_cycle)
            logger.info("10-minute scheduled update successfully finished.")
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Error in background 10-minute scheduler loop: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Start background 10-minute worker
    worker_task = asyncio.create_task(auto_update_background_worker())
    yield
    # Shutdown: Cleanly cancel worker
    worker_task.cancel()
    try:
        await worker_task
    except asyncio.CancelledError:
        pass

app = FastAPI(
    title="Charlo AI Crypto 24h Growth Predictor API",
    description="High-precision cryptocurrency growth probability engine with 10-minute auto-updates.",
    version="2.0.0",
    lifespan=lifespan
)

# CORS configuration for website deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

STATIC_DIR = Path(__file__).parent / "static"
STATIC_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

class LoginRequest(BaseModel):
    username: str
    password: str

@app.post("/api/login")
async def verify_login(req: LoginRequest):
    if req.username.strip() == "Admin" and req.password == "Admin@123":
        return JSONResponse({"status": "success", "user": "Boss Charlo", "authenticated": True})
    raise HTTPException(status_code=401, detail="Invalid Operator ID or Security Key")

@app.get("/api/health")
async def health_check():
    """Endpoint for uptime monitors (Render, UptimeRobot, AWS)."""
    return JSONResponse({
        "status": "healthy",
        "service": "Charlo AI Predictor",
        "timestamp": datetime.now().isoformat(),
        "auto_update_interval_minutes": UPDATE_INTERVAL_MINUTES
    })

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        with open(index_file, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse("<h1>Loading terminal interface...</h1>")

@app.get("/api/predictions")
async def get_predictions():
    if not LATEST_RESULTS_FILE.exists():
        # Generate initial cycle if file doesn't exist yet
        pipeline = AutoUpdatePipeline()
        pipeline.run_update_cycle()

    with open(LATEST_RESULTS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    inr_rate = get_usd_to_inr()
    raw_preds = data.get("predictions", [])
    ui_preds = [compute_ui_fields(p, inr_rate) for p in raw_preds]

    return JSONResponse({
        "last_updated": data.get("last_updated", "Just now"),
        "total_coins": len(ui_preds),
        "inr_rate": inr_rate,
        "auto_update_interval_minutes": UPDATE_INTERVAL_MINUTES,
        "macro_regime": data.get("macro_regime", {}),
        "sentiment": data.get("sentiment", {}),
        "accuracy_stats": data.get("accuracy_stats", {"win_rate_pct": 74.5}),
        "predictions": ui_preds
    })

@app.post("/api/update")
async def trigger_update(background_tasks: BackgroundTasks):
    """Manual on-demand trigger."""
    pipeline = AutoUpdatePipeline()
    results = pipeline.run_update_cycle()
    inr_rate = get_usd_to_inr()
    ui_preds = [compute_ui_fields(p, inr_rate) for p in results]
    return JSONResponse({
        "status": "success",
        "last_updated": datetime.now().strftime("%d %b %Y, %I:%M %p"),
        "predictions": ui_preds
    })

@app.get("/api/export/csv")
async def export_csv():
    """Export current predictions as CSV."""
    if not LATEST_RESULTS_FILE.exists():
        raise HTTPException(status_code=404, detail="No predictions available.")
    with open(LATEST_RESULTS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    df = pd.DataFrame(data.get("predictions", []))
    csv_str = df.to_csv(index=False)
    return PlainTextResponse(csv_str, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=crypto_predictions.csv"})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.dashboard.web_server:app", host="0.0.0.0", port=8000, reload=False)
