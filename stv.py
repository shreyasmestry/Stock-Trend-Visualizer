import json
from datetime import datetime
import matplotlib.pyplot as plt
import ollama  # Handles local or remote inference pipelines
import streamlit as st
import yfinance as yf  # Free, unlimited financial data stream

# OLLAMA CONFIGURATION:
# Defaults to your local machine, but reads an environment variable on Render
OLLAMA_HOST = st.environ.get("OLLAMA_HOST", "http://localhost:11434")

# Configure widescreen dark terminal canvas
st.set_page_config(
    page_title="Quantum Stock Analytics", page_icon="⚡", layout="wide"
)

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
            margin-top: 10px;
        }
    </style>
""",
    unsafe_allow_html=True,
)


# --- AUTOMATED AI ENGINE ---
def generate_ai_analysis(ticker, selected_df):
    """Feeds historical metric segments into local/remote Ollama instance."""
    summary_pack = {}
    for index, row in selected_df.iterrows():
        date_str = index.strftime("%Y-%m-%d")
        summary_pack[date_str] = {
            "Close": round(row["Close"], 2),
            "Volume": int(row["Volume"]),
        }

    prompt = f"Analyze the following stock market asset history for ticker code: {ticker}.\nData:\n{json.dumps(summary_pack)}\n\nProvide a rapid 2-to-3 sentence analysis of the structural trend pattern (Bullish, Bearish, or Volatile) and highlight any immediate momentum risks."

    try:
        client = ollama.Client(host=OLLAMA_HOST)
        response = client.generate(model="qwen2.5-coder:1.5b", prompt=prompt)
        return response["response"]
    except Exception as e:
        return f"⚠️ **AI Sub-Engine Offline**: Could not connect to the model node at `{OLLAMA_HOST}`. Check your local service or your Render app environment configs."


# Main Canvas Headers
st.title("⚡ Quantum Financial Analytics Terminal")
st.markdown("🔒 *Internal Dashboard Connected to Unlimited Data Stream*")
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
        "📅 Timeline Window (Days)", min_value=5, max_value=30, value=12
    )
    chart_color = st.color_picker("🎨 Performance Accent Line Glow", "#10b981")

    st.markdown("---")
    st.subheader("🔋 Infrastructure Quota")
    st.progress(1.0)
    st.caption("Network status: **UNLIMITED ACCESSIBILITY**")

# Canvas Data Processing Pipeline
if ticker:
    st.markdown("---")
    try:
        with st.spinner(f"Pulling live data matrix for {ticker}..."):
            stock = yf.Ticker(ticker)
            # Fetch 1 month of data to ensure we safely cover enough business/trading days
            df = stock.history(period="1mo")

        if not df.empty:
            df = df.sort_index()
            selected_df = df.tail(days_to_show)

            # Extract lists for your matplotlib chart
            selected_dates = [
                date.strftime("%Y-%m-%d") for date in selected_df.index
            ]
            closing_prices = selected_df["Close"].tolist()

            # Stat cards calculus transformations
            latest_price = closing_prices[-1]
            previous_price = (
                closing_prices[-2] if len(closing_prices) > 1 else latest_price
            )
            price_delta = latest_price - previous_price
            percentage_growth = (price_delta / previous_price) * 100
            highest_record = max(closing_prices)
            lowest_record = min(closing_prices)

            # Build Grid Rows Metrics
            m1, m2, m3, m4 = st.columns(4)
            m1.metric(
                label="📌 CURRENT TRANSACTION CLOSE",
                value=f"${latest_price:,.2f}",
                delta=f"{price_delta:+,.2f} ({percentage_growth:+.2f}%)",
            )
            m2.metric(label="📈 PERIOD CEILING HIGH", value=f"${highest_record:,.2f}")
            m3.metric(label="📉 PERIOD FLOOR LOW", value=f"${lowest_record:,.2f}")
            m4.metric(
                label="📦 SYSTEM ARCHIVE STATUS",
                value="CLOUD LIVE",
                delta="0 API Key Cost",
            )

            st.markdown("<br>", unsafe_allow_html=True)

            # Dual-Column Terminal Window Splitting
            chart_col, data_col = st.columns(2)

            with chart_col:
                fig, ax = plt.subplots(figsize=(10, 4.8), facecolor="#111827")
                ax.set_facecolor("#111827")

                ax.plot(
                    selected_dates,
                    closing_prices,
                    marker="o",
                    color=chart_color,
                    linewidth=3,
                    markersize=6,
                    label=ticker,
                )
                ax.fill_between(
                    selected_dates,
                    closing_prices,
                    min(closing_prices) * 0.99,
                    color=chart_color,
                    alpha=0.1,
                )

                ax.set_title(
                    f"{ticker} — OVERVIEW STRATIFIED TIMELINE PROFILE",
                    color="#9ca3af",
                    fontsize=11,
                    fontweight="bold",
                    pad=15,
                )
                ax.tick_params(colors="#9ca3af", labelsize=9)
                ax.grid(True, color="#374151", linestyle="--", alpha=0.5)
                plt.xticks(rotation=45)

                for spine in ax.spines.values():
                    spine.set_color("#374151")

                st.pyplot(fig)
                plt.close(fig)

            with data_col:
                st.subheader("📊 Historical Ledger Sheet")
                ledger_data = []
                for index, row in selected_df.iloc[::-1].iterrows():
                    ledger_data.append(
                        {
                            "Date": index.strftime("%Y-%m-%d"),
                            "Open": f"${row['Open']:.2f}",
                            "High": f"${row['High']:.2f}",
                            "Low": f"${row['Low']:.2f}",
                            "Close": f"${row['Close']:.2f}",
                            "Volume": f"{int(row['Volume']):,}",
                        }
                    )
                st.dataframe(
                    ledger_data, use_container_width=True, hide_index=True
                )

            # --- STREAMING AI LOG BLOCK ---
            st.markdown("---")
            st.subheader("🤖 Localized Cognitive Intelligence Interpretation")
            with st.spinner(
                "Parsing temporal vector matrix calculations via AI engine..."
            ):
                ai_interpretation = generate_ai_analysis(ticker, selected_df)

            st.markdown(
                f"""
                <div class="ai-terminal">
                    <strong>[TERMINAL FEED] Matrix Evaluation System (qwen2.5-coder:1.5b)</strong><br><br>
                    {ai_interpretation}
                </div>
            """,
                unsafe_allow_html=True,
            )

        else:
            st.error(f"❌ No asset data found for symbol: {ticker}")
    except Exception as e:
        st.error(f"💥 Analytics pipeline failure: {str(e)}")
else:
    st.info(
        "ℹ️ System terminal initialized. Change the asset ticker in the sidebar to load charts."
    )
