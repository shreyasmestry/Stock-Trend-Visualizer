import streamlit as st
import yfinance as yf
import matplotlib.pyplot as plt
from groq import Groq
import os

# ==============================================================================
# CONFIGURATION & GLOBAL VARIABLES
# ==============================================================================
# Retrieve secret keys securely from system environment runtime variables
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Basic page layout configuration
st.set_page_config(
    page_title="Quantum Strategy Analytics Sandbox",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom injection styles for dark mode thematic terminal and layout matching
st.markdown(
    """
    <style>
    .ai-terminal {
        background-color: #0f172a !important;
        border-left: 4px solid #3b82f6 !important;
        padding: 15px !important;
        border-radius: 6px !important;
        font-family: 'Courier New', Courier, monospace !important;
        color: #e2e8f0 !important;
        line-height: 1.6 !important;
    }
    div[data-testid="stMetricValue"] {
        font-size: 24px !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ==============================================================================
# SIDEBAR CONTROL INTERFACE PANEL
# ==============================================================================
with st.sidebar:
    st.title("🛡️ Core System Controls")
    st.markdown("Select system variables to alter underlying evaluation matrices.")
    
    # Text input ticker default
    ticker = st.text_input("🔤 Asset Core Ticker", value="AAPL").upper().strip()
    
    # 1. FIXED: Default timeline window window updated to 10 days
    days_to_show = st.slider(
        "📅 Timeline Window (Days)", 
        min_value=5, 
        max_value=30, 
        value=10
    )
    
    accent_color = st.color_picker("🎨 UI Trajectory Line Accent", value="#3b82f6")
    
    st.markdown("---")
    st.info("System terminal fully operational.")

# ==============================================================================
# MAIN CORE LOGIC ENGINE (DATA ACQUISITION)
# ==============================================================================
st.title("🎛️ Quantum Strategy Analytics Dashboard")

if not ticker:
    st.warning("⚠️ Access Denied: Core asset ticker string payload cannot be left empty.")
else:
    df_window = None
    ai_interpretation = ""
    
    try:
        with st.spinner(f"Pulling live data matrix for {ticker}..."):
            stock = yf.Ticker(ticker)
            df = stock.history(period="1mo")

        if not df.empty:
            df = df.sort_index()
            # Prepare data slice matrix
            df_window = df.tail(days_to_show).reset_index()
            df_window['Date'] = df_window['Date'].dt.strftime('%Y-%m-%d')
            
            closing_prices = df_window["Close"].tolist()

            latest_price = closing_prices[-1]
            previous_price = (
                closing_prices[-2] if len(closing_prices) > 1 else latest_price
            )
            price_delta = latest_price - previous_price
            percentage_growth = (price_delta / previous_price) * 100
            highest_record = max(closing_prices)
            lowest_record = min(closing_prices)

            # Build System Grid Metric Rows
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
            
            # Formulate structured payload prompt for the AI text analysis
            raw_summary = (
                f"Asset: {ticker}. Latest Close: ${latest_price:,.2f} ({percentage_growth:+.2f}%). "
                f"High: ${highest_record:,.2f}, Low: ${lowest_record:,.2f} over past {days_to_show} intervals."
            )
            ai_interpretation = f"The underlying market matrix shows a dynamic shift. {raw_summary}"

    except Exception as e:
        st.error(f"⚠️ Core data engine link broken: {str(e)}")
        df_window = None
        ai_interpretation = "Analysis temporarily unavailable due to upstream connectivity drop."

    # ==============================================================================
    # VISUALIZATION & ANALYTICS DATA DISPLAY LAYOUT
    # ==============================================================================
    if df_window is not None and not df_window.empty:
        # Create side-by-side column partitions with a clean horizontal gap
        chart_col, data_col = st.columns([1, 1], gap="medium")

        with chart_col:
            # Standardize the Matplotlib layout container dimensions
            fig, ax = plt.subplots(figsize=(7, 4.3), facecolor="#111827")
            ax.set_facecolor("#111827")
            
            # Render asset plotting matrix onto frame
            ax.plot(
                df_window['Date'], 
                df_window['Close'], 
                color=accent_color, 
                linewidth=2.5, 
                marker='o', 
                markersize=4
            )
            
            ax.set_title(
                f"{ticker} – OVERVIEW STRATIFIED TIMELINE PROFILE", 
                color="#e5e7eb", 
                fontsize=10, 
                fontweight='bold', 
                pad=10
            )
            
            ax.grid(True, linestyle='--', alpha=0.3, color='#374151')
            ax.tick_params(colors='#9ca3af', labelsize=8)
            plt.xticks(rotation=45)
            
            plt.tight_layout()
            st.pyplot(fig, use_container_width=True)

        with data_col:
            st.subheader("📊 Historical Ledger Sheet")
            
            # Build and map currency text parameters
            ledger_data = df_window[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']].copy()
            ledger_data['Open'] = ledger_data['Open'].map('${:,.2f}'.format)
            ledger_data['High'] = ledger_data['High'].map('${:,.2f}'.format)
            ledger_data['Low'] = ledger_data['Low'].map('${:,.2f}'.format)
            ledger_data['Close'] = ledger_data['Close'].map('${:,.2f}'.format)
            ledger_data['Volume'] = ledger_data['Volume'].map('{:,.0f}'.format)
            
            # 2. FIXED: Locked frame height parameter guarantees absolute visual symmetry
            st.dataframe(
                ledger_data, 
                use_container_width=True, 
                hide_index=True,
                height=320  
            )

        # ==============================================================================
        # COGNITIVE ENGINE INTERPRETATION OUTPUT TERMINAL
        # ==============================================================================
        st.subheader("👁️ Cloud Cognitive Intelligence Interpretation")

        # 3. FIXED: Stripped out the "[TERMINAL FEED]" bold subtitle line completely
        st.markdown(
            f"""
            <div class="ai-terminal">
                {ai_interpretation}
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.info("ℹ Rose Terminal Error: No transactional ledger rows available to display.")

# ==============================================================================
# PERSISTENT CONVERSATIONAL CHATBOT FOOTER 
# ==============================================================================
st.markdown("---")
st.subheader("💬 Quantum Strategy Sandbox")

# 4. FIXED: Clean empty list initialization eliminates default automated messages
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Output conversational logs
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Track submission loops
if user_query := st.chat_input("Enter strategic data inquiry (e.g., 'What is a momentum risk?')..."):
    st.session_state.chat_history.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.write(user_query)

    with st.chat_message("assistant"):
        with st.spinner("Processing cognitive matrix response..."):
            try:
                client = Groq(api_key=GROQ_API_KEY)
                
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
                
                st.session_state.chat_history.append({"role": "assistant", "content": bot_response})
                
            except Exception as e:
                st.error(f"⚠️ Chat node link broken: `{str(e)}`")
