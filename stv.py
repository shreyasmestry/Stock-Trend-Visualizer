import sqlite3
import time
import json
from datetime import datetime, timedelta
import requests
import matplotlib.pyplot as plt
import streamlit as st
import os
import ollama  # Handles local or remote inference pipelines
import yfinance as yf

# ... (keep your layout, styles, and sidebar controls exactly the same)

# Canvas Data Processing Pipeline
if ticker:
    st.markdown("---")
    try:
        # Fetch directly from Yahoo Finance with no API keys required
        with st.spinner(f"Pulling live data matrix for {ticker}..."):
            stock = yf.Ticker(ticker)
            # Fetch 30 days of history to safely cover trading days
            df = stock.history(period="1mo") 
            
        if not df.empty:
            # Sort and slice the exact number of days chosen by the slider
            df = df.sort_index()
            selected_df = df.tail(days_to_show)
            
            # Extract lists for your matplotlib chart
            selected_dates = [date.strftime('%Y-%m-%d') for date in selected_df.index]
            closing_prices = selected_df['Close'].tolist()
            
            # --- Map the metrics for your current stat cards ---
            latest_price = closing_prices[-1]
            previous_price = closing_prices[-2] if len(closing_prices) > 1 else latest_price
            price_delta = latest_price - previous_price
            percentage_growth = (price_delta / previous_price) * 100
            highest_record = max(closing_prices)
            lowest_record = min(closing_prices)
            
            # ... (Paste your existing Metric Columns and Chart/Ledger layout code here!) ...
            # Note: For the AI payload dictionary, you can loop through selected_df rows.
            
        else:
            st.error(f"❌ No asset data found for symbol: {ticker}")
            
    except Exception as e:
        st.error(f"💥 Analytics pipeline failure: {str(e)}")

# OLLAMA CONFIGURATION:
# Defaults to your local machine, but reads an environment variable on Render
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")

CACHE_DB = "stock_cache.db"
CACHE_EXPIRY = 86400  
DAILY_LIMIT = 25      

# Configure widescreen dark terminal canvas
st.set_page_config(page_title="Quantum Stock Analytics", page_icon="⚡", layout="wide")

# Inject Premium Neon Dark Mode UI Styling Rules
st.markdown("""
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
            margin-top: 10px;
        }
    </style>
""", unsafe_allow_html=True)

# --- DATABASE LOGIC ENGINE ---
def init_database():
    with sqlite3.connect(CACHE_DB) as conn:
        cursor = conn.cursor()
        cursor.execute('CREATE TABLE IF NOT EXISTS api_cache (ticker TEXT PRIMARY KEY, response_data TEXT, timestamp REAL)')
        cursor.execute('CREATE TABLE IF NOT EXISTS daily_tracker (log_date TEXT PRIMARY KEY, call_count INTEGER)')
        conn.commit()

def get_cached_data(ticker):
    try:
        with sqlite3.connect(CACHE_DB) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT response_data, timestamp FROM api_cache WHERE ticker = ?", (ticker,))
            row = cursor.fetchone()
            if row and (time.time() - float(row[1]) < CACHE_EXPIRY):
                return json.loads(row[0])
    except Exception as e:
        pass
    return None

def save_to_cache(ticker, data):
    try:
        with sqlite3.connect(CACHE_DB) as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT OR REPLACE INTO api_cache VALUES (?, ?, ?)', (ticker, json.dumps(data), time.time()))
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
            cursor.execute("SELECT call_count FROM daily_tracker WHERE log_date = ?", (today_str,))
            row = cursor.fetchone()
            current_calls = int(row[0]) if row else 0
            cursor.execute('INSERT OR REPLACE INTO daily_tracker VALUES (?, ?)', (today_str, current_calls + 1))
            conn.commit()
    except:
        pass

def get_daily_calls():
    today_str = datetime.now().strftime("%Y-%m-%d")
    try:
        with sqlite3.connect(CACHE_DB) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT call_count FROM daily_tracker WHERE log_date = ?", (today_str,))
            row = cursor.fetchone()
            return int(row[0]) if row else 0
    except:
        return 0

# --- AUTOMATED AI ENGINE ---
def generate_ai_analysis(ticker, selected_dates, time_series):
    """Feeds historical metric segments into local/remote Ollama instance."""
    # Build light-weight serialized JSON packet for context windows
    summary_pack = {}
    for date in selected_dates:
        summary_pack[date] = {
            "Close": time_series[date]["4. close"],
            "Volume": time_series[date]["5. volume"]
        }
        
    prompt = f"Analyze the following stock market asset history for ticker code: {ticker}.\nData:\n{json.dumps(summary_pack)}\n\nProvide a rapid 2-to-3 sentence analysis of the structural trend pattern (Bullish, Bearish, or Volatile) and highlight any immediate momentum risks."
    
    try:
        # Client initialized targeting dynamically shifted host locations
        client = ollama.Client(host=OLLAMA_HOST)
        response = client.generate(model="qwen2.5-coder:1.5b", prompt=prompt)
        return response['response']
    except Exception as e:
        return f"⚠️ **AI Sub-Engine Offline**: Could not connect to the model node at `{OLLAMA_HOST}`. Check your local service or your Render app environment configs."

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
    ticker = st.text_input("🎯 Target Asset Ticker", value="IBM", help="Type stock code").upper().strip()
    days_to_show = st.slider("📅 Timeline Window (Days)", min_value=5, max_value=30, value=12)
    chart_color = st.color_picker("🎨 Performance Accent Line Glow", "#10b981")

    st.markdown("---")
    st.subheader("🔋 Infrastructure Quota")
    st.progress(min(current_usage / DAILY_LIMIT, 1.0))
    st.caption(f"Network calls utilized: **{current_usage} / {DAILY_LIMIT}**")

# Canvas Data Processing Pipeline
if ticker:
    data = get_cached_data(ticker)
    is_cached = False

    if data:
        is_cached = True
    else:
        if current_usage >= DAILY_LIMIT:
            st.error(f"🛑 Daily terminal allotment reached! Network firewall unlock resets in {get_time_until_midnight()}.")
            data = None
        else:
            url = "https://www.alphavantage.co/query"
            query_params = {"function": "TIME_SERIES_DAILY", "symbol": ticker, "apikey": API_KEY}

            try:
                response = requests.get(url, params=query_params)

                if response.status_code == 200 and "application/json" in response.headers.get("Content-Type", "").lower():
                    raw_json = response.json()

                    if "Time Series (Daily)" in raw_json:
                        data = raw_json
                        save_to_cache(ticker, data)
                        increment_daily_calls()
                        
                    elif "Note" in raw_json:
                        st.warning("⚠️ Alpha Vantage Rate Limit hit (5 requests/min limit). The local server will resume in 60s.")
                        data = None
                    elif "Information" in raw_json:
                        st.error(f"❌ Key Engine Error: {raw_json['Information']}")
                        data = None
                    elif "Error Message" in raw_json:
                        st.error(f"❌ Invalid Stock Syntax Symbol: {raw_json['Error Message']}")
                        data = None
                    else:
                        st.error("❓ Server responded with an unknown JSON format blueprint configuration.")
                        data = None
                else:
                    st.error(f"📡 API Server didn't return JSON. Received status code {response.status_code}. Content-type: {response.headers.get('Content-Type')}")
                    data = None
            except Exception as e:
                st.error(f"💥 Network pipeline process exception error: {str(e)}")
                data = None

    # UI Rendering Execution Phase
    if data and "Time Series (Daily)" in data:
        time_series = data.get("Time Series (Daily)")
        all_dates = sorted(time_series.keys())
        selected_dates = all_dates[-days_to_show:]
        closing_prices = [float(time_series[date]["4. close"]) for date in selected_dates]

        # Stat cards calculus transformations
        latest_price = closing_prices[-1]
        previous_price = closing_prices[-2] if len(closing_prices) > 1 else latest_price
        price_delta = latest_price - previous_price
        percentage_growth = (price_delta / previous_price) * 100
        highest_record = max(closing_prices)
        lowest_record = min(closing_prices)

        # Build Grid Rows Metrics 
        m1, m2, m3, m4 = st.columns(4)
        m1.metric(label="📌 CURRENT TRANSACTION CLOSE", value=f"${latest_price:,.2f}", delta=f"{price_delta:+,.2f} ({percentage_growth:+.2f}%)")
        m2.metric(label="📈 PERIOD CEILING HIGH", value=f"${highest_record:,.2f}")
        m3.metric(label="📉 PERIOD FLOOR LOW", value=f"${lowest_record:,.2f}")
        m4.metric(label="📦 CACHE FILE ARCHIVE STATUS", value="LOCAL DISK" if is_cached else "LIVE CLOUD SERVER", delta="0 API Cost" if is_cached else "+1 API Cost")

        st.markdown("<br>", unsafe_allow_html=True)

        # Dual-Column Terminal Window Splitting 
        chart_col, data_col = st.columns(2)

        with chart_col:
            fig, ax = plt.subplots(figsize=(10, 4.8), facecolor='#111827')
            ax.set_facecolor('#111827')

            ax.plot(selected_dates, closing_prices, marker='o', color=chart_color, linewidth=3, markersize=6, label=ticker)
            ax.fill_between(selected_dates, closing_prices, min(closing_prices)*0.99, color=chart_color, alpha=0.1)

            ax.set_title(f"{ticker} — OVERVIEW STRATIFIED TIMELINE PROFILE", color='#9ca3af', fontsize=11, fontweight='bold', pad=15)
            ax.tick_params(colors='#9ca3af', labelsize=9)
            ax.grid(True, color='#374151', linestyle='--', alpha=0.5)
            plt.xticks(rotation=45)

            for spine in ax.spines.values():
                spine.set_color('#374151')

            st.pyplot(fig)
            plt.close(fig) # Memory safe cleaning

        with data_col:
            st.subheader("📊 Historical Ledger Sheet")
            ledger_data = []
            for date in reversed(selected_dates):
                metrics = time_series[date]
                ledger_data.append({
                    "Date": date,
                    "Open": f"${float(metrics['1. open']):.2f}",
                    "High": f"${float(metrics['2. high']):.2f}",
                    "Low": f"${float(metrics['3. low']):.2f}",
                    "Close": f"${float(metrics['4. close']):.2f}",
                    "Volume": f"{int(metrics['5. volume']):,}"
                })
            st.dataframe(ledger_data, use_container_width=True, hide_index=True)
            
        # --- NEW INLINE LAYOUT SECTION: STREAMING AI LOG BLOCK ---
        st.markdown("---")
        st.subheader("🤖 Localized Cognitive Intelligence Interpretation")
        with st.spinner("Parsing temporal vector matrix calculations via local engine..."):
            ai_interpretation = generate_ai_analysis(ticker, selected_dates, time_series)
            
        st.markdown(f"""
            <div class="ai-terminal">
                <strong>[TERMINAL FEED] Matrix Evaluation System (qwen2.5-coder:1.5b)</strong><br><br>
                {ai_interpretation}
            </div>
        """, unsafe_allow_html=True)
            
    else:
        if data is None:
            st.info("ℹ️ System terminal initialized. Change the asset ticker in the sidebar or wait for the standard API rate limit window to clear.")
