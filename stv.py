from datetime import datetime, timedelta
import json
import os
import sqlite3
import time
import matplotlib.pyplot as plt
import ollama  # Import local Ollama controller
import requests
import streamlit as st

# --- REPLIT SECURE AUTHENTICATION ---
API_KEY = os.environ.get("ALPHA_VANTAGE_KEY")

CACHE_DB = "stock_cache.db"
CACHE_EXPIRY = 86400
DAILY_LIMIT = 25

# Configure widescreen dark terminal canvas
st.set_page_config(page_title="Quantum Stock Analytics", page_icon="⚡", layout="wide")

# Inject Premium Neon Dark Mode UI Styling Rules
st.markdown(
    """
    <style>
        .stApp {
            background-color: #0b0f19;
            color: #f3f4f6;
        }
        div[data-testid="stMetricContainer"] {
            background: linear-gradient(145deg, #111827, #1f2937);
            border: 1px solid #374151;
            padding: 20px 24px;
            border-radius: 12px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        }
        h1 {
            background: linear-gradient(to right, #3b82f6, #10b981);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 800 !important;
        }
        .ai-terminal {
            background-color: #111827;
            border-left: 4px solid #3b82f6;
            padding: 15px;
            border-radius: 6px;
            font-family: 'Courier New', Courier, monospace;
            color: #a7f3d0;
        }
    </style>
""",
    unsafe_allow_html=True,
)


# --- DATABASE LOGIC ENGINE ---
def init_database():
    with sqlite3.connect(CACHE_DB) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS api_cache (ticker TEXT PRIMARY KEY, response_data TEXT, timestamp REAL)"
        )
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS daily_tracker (log_date TEXT PRIMARY KEY, call_count INTEGER)"
        )
        conn.commit()


def get_cached_data(ticker):
    try:
        with sqlite3.connect(CACHE_DB) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT response_data, timestamp FROM api_cache WHERE ticker = ?",
                (ticker,),
            )
            row = cursor.fetchone()
            if row and (time.time() - float(row[1]) < CACHE_EXPIRY):
                return json.loads(row[0])
    except:
        pass
    return None


def save_to_cache(ticker, data):
    try:
        with sqlite3.connect(CACHE_DB) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO api_cache VALUES (?, ?, ?)",
                (ticker, json.dumps(data), time.time()),
            )
            conn.commit()
    except:
        pass


def get_time_until_midnight():
    now = datetime.now()
    midnight = datetime.combine(now.date() + timedelta(days=1), datetime.min.time())
    time_remaining = midnight - now
    hours, remainder = divmod(time_remaining.seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    return f"{hours}h {minutes}m"


def increment_daily_calls():
    today_str = datetime.now().strftime("%Y-%m-%d")
    try:
        with sqlite3.connect(CACHE_DB) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT call_count FROM daily_tracker WHERE log_date = ?",
                (today_str,),
            )
            row = cursor.fetchone()
            current_calls = int(row[0]) if row else 0
            cursor.execute(
                "INSERT OR REPLACE INTO daily_tracker VALUES (?, ?)",
                (today_str, current_calls + 1),
            )
            conn.commit()
    except:
        pass


def get_daily_calls():
    today_str = datetime.now().strftime("%Y-%m-%d")
    try:
        with sqlite3.connect(CACHE_DB) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT call_count FROM daily_tracker WHERE log_date = ?",
                (today_str,),
            )
            row = cursor.fetchone()
            return int(row[0]) if row else 0
    except:
        return 0


# --- OLLAMA AI LOGIC ENGINE ---
def get_ai_analysis(ticker, historical_summary, timeline_days):
    """Sends stock historical rows to local Qwen 2.5 Coder for trend insights."""
    prompt = f"""
    You are an elite automated quantitative intelligence algorithm.
    Analyze this raw {timeline_days}-day stock matrix for ticker: {ticker}
    
    Data History (JSON):
    {historical_summary}
    
    Task: Write a concise 3-sentence performance assessment summary. 
    State if the global trend vector behaves as Bullish, Bearish, or Choppy/Volatile, and target the macro catalyst momentum shift.
    """
    try:
        response = ollama.generate(model="qwen2.5-coder:1.5b", prompt=prompt)
        return response["response"]
    except Exception as e:
        return f"⚠️ Quantum Core LLM Connection Lost: {str(e)}. Make sure Ollama desktop application is active."


# Initialize Cache Files Database
init_database()
current_usage = get_daily_calls()

# Main Canvas Headers
st.title("⚡ Quantum Financial Analytics Terminal")
st.markdown("🔒 *Internal Dashboard Connected to Local Vault Cache File*")
st.markdown("---")

# Setup Sidebar Panel Configurations
with st.sidebar:
    st.header("⚙️ Core Controls")
    ticker = (
        st.text_input("🎯 Target Asset Ticker", value="IBM", help="Type stock code")
        .upper()
        .strip()
    )

    days_to_show = st.slider(
        "📅 Timeline Window (Days)", min_value=5, max_value=30, value=10
    )
    chart_color = st.color_picker("🎨 Performance Accent Line Glow", "#10b981")

    st.markdown("---")
    st.subheader("🔋 Infrastructure Quota")
    st.progress(min(current_usage / DAILY_LIMIT, 1.0))
    st.caption(f"Network calls utilized: **{current_usage} / {DAILY_LIMIT}**")

# Canvas Data Processing Pipeline
if ticker:
    data = get_cached_data(ticker)
    is_cached = True if data else False

    if not data:
        if current_usage >= DAILY_LIMIT:
            st.error(
                f"🛑 Daily terminal allotment reached! Network firewall unlock resets in {get_time_until_midnight()}."
            )
        else:
            url = "https://alphavantage.co"
            query_params = {
                "function": "TIME_SERIES_DAILY",
                "symbol": ticker,
                "apikey": API_KEY,
            }

            try:
                response = requests.get(url, params=query_params)

                if (
                    response.status_code == 200
                    and "application/json"
                    in response.headers.get("Content-Type", "").lower()
                ):
                    raw_json = response.json()

                    if "Time Series (Daily)" in raw_json:
                        data = raw_json
                        save_to_cache(ticker, data)
                        increment_daily_calls()
                    elif "Note" in raw_json:
                        st.warning(
                            "⚠️ Alpha Vantage Rate Limit hit (5 requests/min limit). The local server will resume in 60s."
                        )
                    elif "Information" in raw_json:
                        st.error(
                            f"❌ Key Engine Error: {raw_json['Information']}"
                        )
                    elif "Error Message" in raw_json:
                        st.error(
                            f"❌ Invalid Stock Syntax Symbol: {raw_json['Error Message']}"
                        )
                    else:
                        st.error(
                            "❓ Server responded with an unknown JSON format blueprint configuration."
                        )
                else:
                    st.error(
                        f"📡 API Server didn't return JSON. Received status code {response.status_code}."
                    )
            except Exception as e:
                st.error(
                    f"💥 Network pipeline process exception error: {str(e)}"
                )

    # UI Rendering Execution Phase
    if data and "Time Series (Daily)" in data:
        time_series = data.get("Time Series (Daily)")
        all_dates = sorted(time_series.keys())
        selected_dates = all_dates[-days_to_show:]
        closing_prices = [
            float(time_series[date]["4. close"]) for date in selected_dates
        ]

        # Stat cards calculus transformations
        latest_price = closing_prices[-1]

        initial_price = closing_prices[0]
        price_delta = latest_price - initial_price
        percentage_growth = (price_delta / initial_price) * 100

        highest_record = max(closing_prices)
        lowest_record = min(closing_prices)

        # Build Grid Rows Metrics
        m1, m2, m3, m4 = st.columns(4)
        m1.metric(
            label=f"📌 {days_to_show}-DAY TIMELINE DELTA",
            value=f"${latest_price:,.2f}",
            delta=f"{price_delta:+,.2f} ({percentage_growth:+.2f}%)",
        )
        m2.metric(label="📈 PERIOD CEILING HIGH", value=f"${highest_record:,.2f}")
        m3.metric(label="📉 PERIOD FLOOR LOW", value=f"${lowest_record:,.2f}")
        m4.metric(
            label="📦 CACHE ARCHIVE STATUS",
            value="LOCAL DISK" if is_cached else "LIVE CLOUD",
            delta="0 API Cost" if is_cached else "+1 API Cost",
        )

        st.markdown("<br>", unsafe_allow_html=True)

        # ----------------------------------------------------
        # NEW SECTION: Chart Generation Block
        # ----------------------------------------------------
        st.subheader("📈 Performance Trend Vector")

        fig, ax = plt.subplots(figsize=(15, 4.5))  # Expanded full-width layout
        fig.patch.set_facecolor("#0b0f19")
        ax.set_facecolor("#111827")

        ax.plot(
            selected_dates,
            closing_prices,
            color=chart_color,
            marker="o",
            linewidth=2,
            markersize=5,
        )

        ax.set_title(
            f"{ticker} - {days_to_show} Day Price Blueprint",
            color="#f3f4f6",
            fontsize=12,
            fontweight="bold",
            pad=15,
        )
        ax.grid(True, color="#374151", linestyle="--", alpha=0.5)
        ax.tick_params(colors="#9ca3af", labelsize=8)
        plt.xticks(rotation=45)

        for spine in ["top", "right", "left", "bottom"]:
            ax.spines[spine].set_visible(False)

        st.pyplot(fig, use_container_width=True)
        plt.close(fig)

        st.markdown("---")

        # ----------------------------------------------------
        # NEW SECTION: Data Records vs AI Agent Engine split
        # ----------------------------------------------------
        data_col, ai_col = st.columns(2)

        with data_col:
            st.subheader("🗃️ Raw Data Matrix Record")

            raw_records = []
            for date in reversed(selected_dates):
                metrics = time_series[date]
                raw_records.append(
                    {
                        "Date": date,
                        "Open ($)": f"{float(metrics['1. open']):,.2f}",
                        "High ($)": f"{float(metrics['2. high']):,.2f}",
                        "Low ($)": f"{float(metrics['3. low']):,.2f}",
                        "Close ($)": f"{float(metrics['4. close']):,.2f}",
                        "Volume": f"{int(metrics['5. volume']):,}",
                    }
                )

            st.dataframe(
                raw_records, use_container_width=True, hide_index=True
            )

        with ai_col:
            st.subheader("🤖 Qwen AI Deep Analysis")

            # Format current sub-selected context frame for our LLM payload
            ai_payload = {}
            for d in selected_dates:
                ai_payload[d] = {
                    "Close": time_series[d]["4. close"],
                    "Volume": time_series[d]["5. volume"],
                }

            # Call local Ollama pipeline
            with st.spinner("Decoding trend patterns via qwen2.5-coder..."):
                ai_analysis_response = get_ai_analysis(
                    ticker, json.dumps(ai_payload), days_to_show
                )

            # Render custom Styled terminal output box
            st.markdown(
                f"""
                <div class="ai-terminal">
                    <strong>[SYSTEM ENGAGED]: qwen2.5-coder:1.5b</strong><br><br>
                    {ai_analysis_response}
                </div>
                """,
                unsafe_allow_html=True,
            )

    else:
        st.info(
            "💡 Enter a valid target ticker code asset above in the configuration dock panel to query statistics."
        )
