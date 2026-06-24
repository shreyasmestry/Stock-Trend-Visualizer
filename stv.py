import json
from datetime import datetime
import matplotlib.pyplot as plt
from groq import Groq  # Switched from ollama to lightweight Groq client
import streamlit as st
import yfinance as yf  # Free, unlimited financial data stream
import os

# GROQ API CONFIGURATION:
# Securely pulls your free API key from Render's Environment Variables
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")

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
        /* Container background styling */
        div[data-testid="stMetricContainer"] {
            background: linear-gradient(145deg, #111827, #1f2937);
            border: 1px solid #374151;
            padding: 20px 24px;
            border-radius: 12px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        }
        /* Changes the big numbers to bright white */
        div[data-testid="stMetricValue"] {
            color: #ffffff !important;
        }
        /* Force the top metric headers/labels to be high-contrast and readable */
        div[data-testid="stMetricLabel"] > div {
            color: #e5e7eb !important;
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
    """Feeds historical metric segments into cloud Groq instance."""
    if not GROQ_API_KEY:
        return "⚠️ **Groq API Key Missing**: Please set the `GROQ_API_KEY` environment variable in your Render dashboard settings."

    summary_pack = {}
    for index, row in selected_df.iterrows():
        date_str = index.strftime("%Y-%m-%d")
        summary_pack[date_str] = {
            "Close": round(row["Close"], 2),
            "Volume": int(row["Volume"]),
        }

    prompt = f"Analyze the following stock market asset history for ticker code: {ticker}.\nData:\n{json.dumps(summary_pack)}\n\nProvide a rapid 2-to-3 sentence analysis of the structural trend pattern (Bullish, Bearish, or Volatile) and highlight any immediate momentum risks."

    try:
        # Initialize Groq cloud engine client
        client = Groq(api_key=GROQ_API_KEY)
        
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",  # Free, lightning-fast model tier
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=150
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ **AI Sub-Engine Offline**: Cloud routing pipeline failure. Error details: `{str(e)}`"


# Main Canvas Headers
st.title("⚡ Quantum Financial Analytics Terminal")
st.markdown("🔒 *Internal Dashboard Connected to Unlimited Data Stream*")
st.markdown("---")

# Setup Sidebar Panel Configurations
with st.sidebar:
    st.header("⚙️ Core Controls")
    ticker = (
        st.text_input("🎯 Target Asset Ticker", value="NVDA", help="Type stock code")
        .upper()
        .strip()
    )
    days_to_show = st.slider(
        "📅 Timeline Window (Days)", min_value=5, max_value=30, value=12
    )
    chart_color = st.color_picker("🎨 Performance Accent Line Glow", "#10b981")

# Canvas Data Processing Pipeline
if ticker:
    st.markdown("---")
    try:
        with st.spinner(f"Pulling live data matrix for {ticker}..."):
            stock = yf.Ticker(ticker)
            df = stock.history(period="1mo")

        if not df.empty:
            df = df.sort_index()
            selected_df = df.tail(days_to_show)

            selected_dates = [
                date.strftime("%Y-%m-%d") for date in selected_df.index
            ]
            closing_prices = selected_df["Close"].tolist()

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
                value="LIVE",
                delta="Cloud API Connected",
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
            st.subheader("🤖 Cloud Cognitive Intelligence Interpretation")
            with st.spinner(
                "Streaming cloud-vectored analytics from Groq engine..."
            ):
                ai_interpretation = generate_ai_analysis(ticker, selected_df)

            st.markdown(
                f"""
                <div class="ai-terminal">
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

# --- PERSISTENT CONVERSATIONAL CHATBOT FOOTER ---
st.markdown("---")
st.subheader("💬 The Analytics Analyser ")

# Initialize chat matrix state variables if missing
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Display current active history logs
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Handle real-time interface submission input query
if user_query := st.chat_input("Enter strategic data inquiry (e.g., 'What is a momentum risk?')..."):
    # Append user prompt immediately to interface
    st.session_state.chat_history.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.write(user_query)

    # Route message query payload out to Groq engine cluster
    with st.chat_message("assistant"):
        with st.spinner("Processing cognitive matrix response..."):
            try:
                client = Groq(api_key=GROQ_API_KEY)
                
                # Format full thread context history for the model
                messages_payload = [
                    {"role": msg["role"], "content": msg["content"]}
                    for msg in st.session_state.chat_history
                ]
                
                response = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=messages_payload,
                    temperature=0.5,
                    max_tokens=250
                )
                
                bot_response = response.choices[0].message.content
                st.write(bot_response)
                
                # Append finalized structure output back to persistent session history state
                st.session_state.chat_history.append({"role": "assistant", "content": bot_response})
                
            except Exception as e:
                st.error(f"⚠️ Chat node link broken: `{str(e)}`")
