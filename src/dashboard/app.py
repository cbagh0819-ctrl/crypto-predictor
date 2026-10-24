"""Interactive Streamlit Web Dashboard for 24h Crypto Growth Predictions."""

import json
from pathlib import Path
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from config.settings import PROCESSED_DATA_DIR, COINS_CONFIG_PATH
from src.scheduler.auto_updater import AutoUpdatePipeline, LATEST_RESULTS_FILE

st.set_page_config(
    page_title="AI Crypto 24h Growth Predictor",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom high-tech styling
st.markdown("""
<style>
    .metric-card {
        background-color: #131722;
        border: 1px solid #2a2e39;
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 15px;
    }
    .bullish-badge {
        background-color: rgba(38, 166, 154, 0.2);
        color: #26a69a;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: bold;
    }
    .bearish-badge {
        background-color: rgba(239, 83, 80, 0.2);
        color: #ef5350;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

st.title("⚡ AI Crypto 24h Growth Predictor & Auto-Analyzer")
st.caption("Powered by Probabilistic Gradient Boosting, Multi-Factor Technical Features & Scheduled Auto-Updating")

# Load existing predictions
data = {}
if LATEST_RESULTS_FILE.exists():
    try:
        with open(LATEST_RESULTS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        data = {}

predictions = data.get("predictions", [])
last_updated = data.get("last_updated", "Not yet run")

# Sidebar Controls
st.sidebar.header("🕹️ Control Panel")
st.sidebar.info(f"🕒 **Last Updated**: {last_updated}")

if st.sidebar.button("🔄 Run Auto-Analysis & Update Now", use_container_width=True):
    with st.spinner("Fetching latest live market data & computing 24h probabilities..."):
        pipeline = AutoUpdatePipeline()
        predictions = pipeline.run_update_cycle()
        st.sidebar.success("Updated successfully!")
        st.rerun()

st.sidebar.divider()
st.sidebar.subheader("🎯 Filters")
filter_option = st.sidebar.selectbox(
    "Signal Category",
    ["All Signals", "Strong Bullish 🚀", "Moderate Bullish 📈", "Neutral / Sideways ⚖️", "Bearish / Caution 🔻"]
)

# Sector filter
available_categories = ["All Sectors"] + sorted(list({p.get("category", "General") for p in predictions if p.get("category")}))
sector_filter = st.sidebar.selectbox("Filter by Sector", available_categories)

min_prob = st.sidebar.slider("Minimum 24h Growth Probability (%)", 0, 100, 0, step=5)

# Main Display
if not predictions:
    st.warning("⚠️ No predictions generated yet. Click 'Run Auto-Analysis & Update Now' in the sidebar or run `python main.py --update`.")
else:
    df_pred = pd.DataFrame(predictions)

    # Filter
    filtered_preds = [
        p for p in predictions
        if (filter_option == "All Signals" or p.get("signal") == filter_option)
        and (sector_filter == "All Sectors" or p.get("category") == sector_filter)
        and p.get("growth_probability", 0) >= min_prob
    ]

    # Overview Metrics
    col1, col2, col3, col4 = st.columns(4)
    top_coin = predictions[0] if predictions else {}
    avg_prob = sum(p.get("growth_probability", 0) for p in predictions) / len(predictions) if predictions else 0
    bullish_count = sum(1 for p in predictions if "Bullish" in p.get("signal", ""))

    with col1:
        st.metric("Total Cryptos Tracked", len(predictions))
    with col2:
        st.metric("Top 24h Growth Pick", f"{top_coin.get('symbol', 'N/A')}", f"{top_coin.get('growth_probability', 0)}% Chance")
    with col3:
        st.metric("Bullish Market Breadth", f"{bullish_count}/{len(predictions)} Coins")
    with col4:
        st.metric("Average 24h Growth Probability", f"{avg_prob:.1f}%")

    st.divider()

    # Ranking Table
    st.subheader("📊 24-Hour Growth Probability Leaderboard")

    def format_price(p):
        if p is None:
            return "$0.00"
        if p < 0.0001:
            return f"${p:.8f}"
        elif p < 1.0:
            return f"${p:.4f}"
        else:
            return f"${p:,.2f}"

    table_data = []
    for p in filtered_preds:
        table_data.append({
            "Token": p.get("symbol"),
            "Name": p.get("name", ""),
            "Sector": p.get("category", "General"),
            "Live Price": format_price(p.get("current_price")),
            "24h Past Change": f"{p.get('change_24h_pct', 0):+.2f}%",
            "Chance of Growth (Next 24h)": f"{p.get('growth_probability', 0)}%",
            "Signal": p.get("signal"),
            "Confidence": f"{p.get('confidence_score', 0)}%"
        })

    if table_data:
        st.dataframe(pd.DataFrame(table_data), use_container_width=True)

        # Bar chart comparison
        chart_df = pd.DataFrame(filtered_preds).sort_values("growth_probability", ascending=True)
        fig = px.bar(
            chart_df,
            x="growth_probability",
            y="symbol",
            orientation="h",
            color="growth_probability",
            color_continuous_scale="Viridis",
            labels={"growth_probability": "Growth Probability (%)", "symbol": "Cryptocurrency"},
            title="Next 24h Growth Probability Comparison"
        )
        fig.add_vline(x=50, line_dash="dash", line_color="gray", annotation_text="50% Equilibrium")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No cryptocurrencies match the current filter criteria.")

    # Deep Analysis Section
    st.divider()
    st.subheader("🔍 Deep Technical Diagnostics & Catalyst Drivers")
    selected_symbol = st.selectbox("Select a coin to view detailed AI analysis:", [p["symbol"] for p in predictions])
    selected_coin = next((p for p in predictions if p["symbol"] == selected_symbol), None)

    if selected_coin:
        analysis = selected_coin.get("analysis", {})
        st.markdown(f"### {selected_symbol} - **{selected_coin.get('signal')}**")
        st.info(analysis.get("summary", "No summary available."))

        st.markdown("#### Key Drivers Identified by AI Engine:")
        for driver in analysis.get("drivers", []):
            st.markdown(f"- {driver}")
