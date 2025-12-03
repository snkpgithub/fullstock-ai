"""
Universal Stock Tracker - Streamlit Web App
AI-powered web application to track any stock (default: AAPL)

Requirements:
pip install streamlit groq yfinance pandas plotly
"""

import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import os

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

# ---------------- Page configuration ----------------
st.set_page_config(
    page_title="Stock Tracker",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------- Custom CSS ----------------
st.markdown(
    """
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .stButton>button {
        width: 100%;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------- Session State Init ----------------
if "api_key" not in st.session_state:
    st.session_state.api_key = os.getenv("GROQ_API_KEY", "")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "ticker" not in st.session_state:
    st.session_state.ticker = "AAPL"  # default


class StockTracker:
    def __init__(self, ticker: str):
        self.ticker = ticker.upper()
        self.model = "llama-3.3-70b-versatile"

    @st.cache_data(ttl=60)
    def get_current_price(_self, ticker: str):
        """Fetch current stock price (cached for 60 seconds)"""
        try:
            stock = yf.Ticker(ticker)
            data = stock.history(period="1d")
            if not data.empty:
                current_price = data["Close"].iloc[-1]
                # Try to get previous close safely
                try:
                    info = stock.info
                    prev_close = info.get("previousClose", current_price)
                except Exception:
                    prev_close = current_price

                if prev_close in (None, 0):
                    prev_close = current_price

                change = current_price - prev_close
                change_pct = (change / prev_close) * 100
                return {
                    "price": round(current_price, 2),
                    "change": round(change, 2),
                    "change_pct": round(change_pct, 2),
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                }
            return None
        except Exception as e:
            st.error(f"Error fetching price for {ticker}: {e}")
            return None

    @st.cache_data(ttl=300)
    def get_historical_data(_self, ticker: str, period: str = "1mo"):
        """Fetch historical stock data (cached for 5 minutes)"""
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period=period)
            return hist
        except Exception as e:
            st.error(f"Error fetching historical data for {ticker}: {e}")
            return None

    @st.cache_data(ttl=3600)
    def get_stock_info(_self, ticker: str):
        """Get detailed stock information (cached for 1 hour)"""
        try:
            stock = yf.Ticker(ticker)
            info = stock.info or {}
            return {
                "company": info.get("longName", ticker),
                "sector": info.get("sector", "N/A"),
                "industry": info.get("industry", "N/A"),
                "market_cap": info.get("marketCap", "N/A"),
                "pe_ratio": info.get("trailingPE", "N/A"),
                "day_high": info.get("dayHigh", "N/A"),
                "day_low": info.get("dayLow", "N/A"),
                "52week_high": info.get("fiftyTwoWeekHigh", "N/A"),
                "52week_low": info.get("fiftyTwoWeekLow", "N/A"),
                "volume": info.get("volume", "N/A"),
                "avg_volume": info.get("averageVolume", "N/A"),
                "dividend_yield": info.get("dividendYield", "N/A"),
            }
        except Exception as e:
            st.error(f"Error fetching stock info for {ticker}: {e}")
            return None

    def create_price_chart(self, hist: pd.DataFrame, ticker: str, period: str):
        """Create interactive price chart using Plotly"""
        fig = go.Figure()

        # Candlestick chart
        fig.add_trace(
            go.Candlestick(
                x=hist.index,
                open=hist["Open"],
                high=hist["High"],
                low=hist["Low"],
                close=hist["Close"],
                name=ticker,
            )
        )

        # Add volume as bar chart
        fig.add_trace(
            go.Bar(
                x=hist.index,
                y=hist["Volume"],
                name="Volume",
                yaxis="y2",
                marker_color="rgba(100, 100, 250, 0.3)",
            )
        )

        fig.update_layout(
            title=f"{ticker} Stock Price History ({period})",
            yaxis_title="Price ($)",
            yaxis2=dict(
                title="Volume",
                overlaying="y",
                side="right",
            ),
            xaxis_rangeslider_visible=False,
            height=500,
            hovermode="x unified",
        )

        return fig
    def sanitize_for_groq(text: str) -> str:
        """
        Groq (or the underlying HTTP stack) may sometimes choke on non-ASCII chars
        in certain environments. This helper removes emojis and non-ASCII symbols.
        """
        if not isinstance(text, str):
            text = str(text)
        return text.encode("ascii", "ignore").decode()

    def analyze_with_ai(self, ticker: str, query: str, stock_data: dict, api_key: str) -> str:
        """Use Groq AI to analyze stock data"""
        if not GROQ_AVAILABLE:
            return "Groq library not installed. Please run: pip install groq"

        if not api_key:
            return "Please enter your FREE Groq API key in the sidebar."

        try:
            client = Groq(api_key=api_key)

            context = f"""
    Current {ticker} Stock Data:
    - Current Price: ${stock_data.get('current_price', 'N/A')}
    - Day Change: {stock_data.get('change', 'N/A')} ({stock_data.get('change_pct', 'N/A')}%)
    - Day High: ${stock_data.get('day_high', 'N/A')}
    - Day Low: ${stock_data.get('day_low', 'N/A')}
    - 52 Week High: ${stock_data.get('52week_high', 'N/A')}
    - 52 Week Low: ${stock_data.get('52week_low', 'N/A')}
    - Market Cap: {stock_data.get('market_cap', 'N/A')}
    - P/E Ratio: {stock_data.get('pe_ratio', 'N/A')}
    - Volume: {stock_data.get('volume', 'N/A')}
    - Sector: {stock_data.get('sector', 'N/A')}
    - Industry: {stock_data.get('industry', 'N/A')}

    Historical Performance:
    {stock_data.get('historical_summary', 'N/A')}
    """

            # 🔑 Sanitize all text sent to Groq (removes emojis / non-ASCII)
            safe_context = sanitize_for_groq(context)
            safe_query = sanitize_for_groq(query)

            completion = client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": sanitize_for_groq(
                            "You are a helpful financial analyst assistant. "
                            "Provide clear, balanced analysis of stock data. "
                            "Always remind users this is not financial advice and they should do their own research."
                        ),
                    },
                    {
                        "role": "user",
                        "content": f"{safe_context}\n\nUser Query: {safe_query}\n\nProvide helpful analysis based on the data above.",
                    },
                ],
                temperature=0.7,
                max_tokens=1000,
            )

            return completion.choices[0].message.content

        except Exception as e:
            # Keep this error message plain ASCII to be extra safe
            return (
                f"AI Error: {str(e)}\n\n"
                "Make sure your API key is valid or try again without emojis in your question."
            )


# ---------------- Sidebar ----------------
with st.sidebar:
    st.markdown("## ⚙️ Settings")

    # ----- Ticker Input -----
    st.markdown("### 🏷️ Stock Selection")
    ticker_input = st.text_input(
        "Stock Ticker (e.g., AAPL, EXLS, MSFT)",
        value=st.session_state.ticker,
        help="Enter any valid stock ticker symbol",
    )

    # Normalize + store ticker
    new_ticker = (ticker_input or "AAPL").strip().upper()
    if new_ticker != st.session_state.ticker:
        st.session_state.ticker = new_ticker

    st.markdown("### 🔑 AI Configuration")
    st.markdown("Get your FREE API key at [console.groq.com](https://console.groq.com)")

    api_key_input = st.text_input(
        "Groq API Key",
        value=st.session_state.api_key,
        type="password",
        help="Enter your FREE Groq API key for AI analysis",
    )

    if api_key_input != st.session_state.api_key:
        st.session_state.api_key = api_key_input
        st.success("✅ API Key updated!")

    st.markdown("---")

    # Time period selector
    st.markdown("### 📊 Chart Settings")
    period = st.selectbox(
        "Historical Period",
        options=["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y"],
        index=2,
        help="Select time period for historical data",
    )

    st.markdown("---")

    # Refresh button
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    st.markdown("---")
    st.markdown("### ℹ️ About")
    st.info(
        """
    **Universal Stock Tracker**
    
    Track any stock with real-time data and AI-powered analysis.
    
    Powered by:
    - 📊 Yahoo Finance
    - 🤖 Groq AI (FREE)
    - ⚡ Streamlit
    """
    )

# ---------------- Main Content ----------------
ticker = st.session_state.ticker
tracker = StockTracker(ticker)

# Fetch info once
info = tracker.get_stock_info(ticker) or {}
company_name = info.get("company", ticker)

st.markdown(
    f'<h1 class="main-header">📈 {ticker} Stock Tracker</h1>',
    unsafe_allow_html=True,
)
st.markdown(
    f"**{company_name} ({ticker})** | Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
)

# Fetch current price
price_data = tracker.get_current_price(ticker)

# ----- Top Metrics -----
if price_data:
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="💰 Current Price",
            value=f"${price_data['price']}",
            delta=f"{price_data['change']} ({price_data['change_pct']}%)",
        )

    with col2:
        day_high = info.get("day_high", "N/A")
        if day_high not in ("N/A", None):
            st.metric(label="📈 Day High", value=f"${day_high:.2f}")
        else:
            st.metric(label="📈 Day High", value="N/A")

    with col3:
        day_low = info.get("day_low", "N/A")
        if day_low not in ("N/A", None):
            st.metric(label="📉 Day Low", value=f"${day_low:.2f}")
        else:
            st.metric(label="📉 Day Low", value="N/A")

    with col4:
        volume = info.get("volume", "N/A")
        if volume not in ("N/A", None, 0):
            volume_m = volume / 1_000_000
            st.metric(label="📊 Volume", value=f"{volume_m:.2f}M")
        else:
            st.metric(label="📊 Volume", value="N/A")

st.markdown("---")

# ---------------- Tabs ----------------
tab1, tab2, tab3, tab4 = st.tabs(
    ["📊 Chart", "📋 Details", "🤖 AI Analysis", "💬 AI Chat"]
)

# ========== Tab 1: Chart ==========
with tab1:
    st.markdown("### 📈 Price Chart")

    hist = tracker.get_historical_data(ticker, period)

    if hist is not None and not hist.empty:
        fig = tracker.create_price_chart(hist, ticker, period)
        st.plotly_chart(fig, use_container_width=True)

        col1, col2, col3 = st.columns(3)

        period_start = hist["Close"].iloc[0]
        period_end = hist["Close"].iloc[-1]
        change = period_end - period_start
        change_pct = (change / period_start) * 100

        with col1:
            st.metric(label=f"Period Start ({period})", value=f"${period_start:.2f}")

        with col2:
            st.metric(label="Period End", value=f"${period_end:.2f}")

        with col3:
            st.metric(
                label="Period Change",
                value=f"${change:.2f}",
                delta=f"{change_pct:+.2f}%",
            )
    else:
        st.error(f"Unable to load chart data for {ticker}")

# ========== Tab 2: Details ==========
with tab2:
    st.markdown("### 📋 Stock Details")

    if info:
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### Company Information")
            st.write(f"**Company:** {info.get('company', ticker)}")
            st.write(f"**Sector:** {info.get('sector', 'N/A')}")
            st.write(f"**Industry:** {info.get('industry', 'N/A')}")

            market_cap = info.get("market_cap", "N/A")
            if market_cap not in ("N/A", None):
                market_cap_b = market_cap / 1_000_000_000
                st.write(f"**Market Cap:** ${market_cap_b:.2f}B")
            else:
                st.write("**Market Cap:** N/A")

            pe_ratio = info.get("pe_ratio", "N/A")
            if pe_ratio not in ("N/A", None):
                st.write(f"**P/E Ratio:** {pe_ratio:.2f}")
            else:
                st.write("**P/E Ratio:** N/A")

        with col2:
            st.markdown("#### Trading Information")
            st.write(f"**52-Week High:** ${info.get('52week_high', 'N/A')}")
            st.write(f"**52-Week Low:** ${info.get('52week_low', 'N/A')}")

            avg_volume = info.get("avg_volume", "N/A")
            if avg_volume not in ("N/A", None, 0):
                avg_vol_m = avg_volume / 1_000_000
                st.write(f"**Avg Volume:** {avg_vol_m:.2f}M")
            else:
                st.write("**Avg Volume:** N/A")

            dividend_yield = info.get("dividend_yield", "N/A")
            if (
                dividend_yield not in ("N/A", None)
                and isinstance(dividend_yield, (int, float))
                and dividend_yield > 0
            ):
                st.write(f"**Dividend Yield:** {dividend_yield * 100:.2f}%")
            else:
                st.write("**Dividend Yield:** N/A")
    else:
        st.error(f"No stock info available for {ticker}.")

# ========== Tab 3: AI Analysis ==========
with tab3:
    st.markdown("### 🤖 AI Stock Analysis")

    if not st.session_state.api_key:
        st.warning("⚠️ Please enter your FREE Groq API key in the sidebar to use AI features.")
        st.info("Get your free API key at: https://console.groq.com")
    else:
        if not GROQ_AVAILABLE:
            st.error("Groq library is not installed. Run: `pip install groq`")
        else:
            st.info(f"Click a button below to get AI-powered analysis of {ticker} stock")

            col1, col2, col3 = st.columns(3)

            def build_stock_data(base_hist_period: str) -> dict:
                data = {
                    "current_price": price_data["price"] if price_data else "N/A",
                    "change": price_data["change"] if price_data else "N/A",
                    "change_pct": price_data["change_pct"] if price_data else "N/A",
                    **info,
                }
                hist_local = tracker.get_historical_data(ticker, base_hist_period)
                if hist_local is not None and not hist_local.empty:
                    pct = (
                        (hist_local["Close"].iloc[-1] - hist_local["Close"].iloc[0])
                        / hist_local["Close"].iloc[0]
                        * 100
                    )
                    data["historical_summary"] = (
                        f"{base_hist_period} change: {pct:.2f}%"
                    )
                else:
                    data["historical_summary"] = "Historical data not available."
                return data

            with col1:
                if st.button("📊 Analyze Current Performance", use_container_width=True):
                    with st.spinner("Analyzing..."):
                        stock_data = build_stock_data("1mo")
                        analysis = tracker.analyze_with_ai(
                            ticker,
                            "Provide a comprehensive analysis of current performance and trends.",
                            stock_data,
                            st.session_state.api_key,
                        )
                        st.markdown(analysis)

            with col2:
                if st.button("💡 Investment Insights", use_container_width=True):
                    with st.spinner("Analyzing..."):
                        stock_data = build_stock_data("3mo")
                        analysis = tracker.analyze_with_ai(
                            ticker,
                            "What are the key factors investors should consider? Analyze valuation, growth potential, and risks.",
                            stock_data,
                            st.session_state.api_key,
                        )
                        st.markdown(analysis)

            with col3:
                if st.button("📈 Technical Analysis", use_container_width=True):
                    with st.spinner("Analyzing..."):
                        stock_data = build_stock_data("6mo")
                        analysis = tracker.analyze_with_ai(
                            ticker,
                            "Provide technical analysis: price levels, support/resistance, and momentum based on the data.",
                            stock_data,
                            st.session_state.api_key,
                        )
                        st.markdown(analysis)

# ========== Tab 4: AI Chat ==========
with tab4:
    st.markdown("### 💬 Chat with AI About This Stock")

    if not st.session_state.api_key:
        st.warning("⚠️ Please enter your FREE Groq API key in the sidebar to use AI chat.")
        st.info("Get your free API key at: https://console.groq.com")
    else:
        if not GROQ_AVAILABLE:
            st.error("Groq library is not installed. Run: `pip install groq`")
        else:
            # Display chat history
            for message in st.session_state.chat_history:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

            prompt = st.chat_input(f"Ask anything about {ticker} stock...")
            if prompt:
                # Add user message
                st.session_state.chat_history.append(
                    {"role": "user", "content": prompt}
                )
                with st.chat_message("user"):
                    st.markdown(prompt)

                # Assistant response
                with st.chat_message("assistant"):
                    with st.spinner("Thinking..."):
                        stock_data = {
                            "current_price": price_data["price"] if price_data else "N/A",
                            "change": price_data["change"] if price_data else "N/A",
                            "change_pct": price_data["change_pct"]
                            if price_data
                            else "N/A",
                            **info,
                        }

                        hist_local = tracker.get_historical_data(ticker, "1mo")
                        if hist_local is not None and not hist_local.empty:
                            pct = (
                                (hist_local["Close"].iloc[-1] - hist_local["Close"].iloc[0])
                                / hist_local["Close"].iloc[0]
                                * 100
                            )
                            stock_data["historical_summary"] = (
                                f"1-month change: {pct:.2f}%"
                            )
                        else:
                            stock_data["historical_summary"] = (
                                "1-month historical data not available."
                            )

                        response = tracker.analyze_with_ai(
                            ticker, prompt, stock_data, st.session_state.api_key
                        )
                        st.markdown(response)

                        st.session_state.chat_history.append(
                            {"role": "assistant", "content": response}
                        )

            if st.button("🗑️ Clear Chat History"):
                st.session_state.chat_history = []
                st.rerun()

# ---------------- Footer ----------------
st.markdown("---")
st.markdown(
    """
<div style='text-align: center; color: #666;'>
    <p>⚠️ <strong>Disclaimer:</strong> This tool is for informational purposes only. Not financial advice. Always do your own research.</p>
    <p>Data provided by Yahoo Finance | AI powered by Groq (FREE)</p>
</div>
""",
    unsafe_allow_html=True,
)
