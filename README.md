Here is a **clean, professional GitHub README.md** tailored for your project
—including your website URL placeholder, usage instructions, deployment notes, screenshots placeholders, and AI explanation.

You can copy-paste this directly into `README.md` in your repository.

---

# 📈 Universal Stock Tracker – AI-Powered Stock Analysis

### Real-time charts, financial metrics, and Groq-powered AI insights for any stock

🔗 **Live App:** [https://YOUR-STREAMLIT-APP-URL.streamlit.app](https://fullstock-ai.streamlit.app/)

---

## 🚀 Overview

Universal Stock Tracker is a powerful Streamlit web application that lets you:

* Track **any stock** (default: AAPL)
* View **live stock prices**
* Explore **historical charts** (candlestick + volume)
* Check **key financial metrics**
* Get **AI-powered** analysis using Groq Llama-3.3-70B
* Chat with AI about any stock in real time

This project blends **finance**, **visualization**, and **AI agents** into one intuitive interface.

---

## 🧠 Features

### ✔️ Real-Time Stock Price

* Current price
* Intraday change (% and absolute)
* Daily high/low
* Volume

### ✔️ Interactive Price Chart

* Candlestick + Volume
* Selectable ranges: `1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y`

### ✔️ Stock Fundamentals

* Company name
* Sector & Industry
* Market Cap
* P/E Ratio
* 52-Week High/Low
* Avg volume
* Dividend yield

### ✔️ AI Analysis (Groq)

* Current performance analysis
* Investment insights
* Technical analysis
* AI chat about any stock

### ✔️ Emoji-safe, Unicode-safe

All text sent to Groq is sanitized to avoid issues with non-ASCII characters.

---

## ⚙️ Installation & Local Usage

### 1️⃣ Clone the repository

```bash
git clone https://github.com/YOUR-USERNAME/fullstock-ai.git
cd fullstock-ai
```

### 2️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

### 3️⃣ Set your Groq API key

Create `.streamlit/secrets.toml` locally:

```toml
GROQ_API_KEY = "your_api_key_here"
```

Or set environment variable:

```bash
export GROQ_API_KEY="your_api_key_here"
```

### 4️⃣ Run the app

```bash
streamlit run app.py
```

---

## 🌐 Deploy on Streamlit Cloud (Free)

1. Push your code to GitHub
2. Go to **[https://streamlit.io/cloud](https://streamlit.io/cloud)**
3. Click **New App** → choose your repo
4. Set **app.py** as the main file
5. Add secret key under **App Settings → Secrets**:

```toml
GROQ_API_KEY = "your_api_key_here"
```

6. Deploy 🚀

---

## 🧪 How to Use the App

### 1️⃣ Select a Stock

Enter any ticker symbol (AAPL, TSLA, EXLS, MSFT, NVDA, etc.)

### 2️⃣ Choose a Historical Range

Pick from the dropdown in the sidebar.

### 3️⃣ View Charts & Metrics

* Live prices
* Candlestick chart
* Key stock fundamentals

### 4️⃣ Use AI Analysis

Under **“🤖 AI Analysis”**, choose:

* 📊 Current Performance
* 💡 Investment Insights
* 📈 Technical Analysis

### 5️⃣ Chat With AI

Go to **“💬 AI Chat”**
Ask anything:

> “Is AAPL overvalued?”
> “What does the latest 3-month trend mean?”
> “Show me important risk factors.”

---

## 📦 Requirements

```
streamlit==1.51.0
yfinance
pandas
plotly
groq
```

---

## 🏗️ Project Structure

```
fullstock-ai/
│── app.py
│── requirements.txt
│── README.md
└── .streamlit/
    └── secrets.toml (not included in repo)
```

---

## 📷 Screenshots (Optional)

> Add screenshots of UI here

```
![Dashboard](assets/dashboard.png)
![AI Analysis](assets/ai_analysis.png)
```

---

## 🛡️ Disclaimer

This tool is for **educational & informational purposes only**.
Not financial advice. Always do your own research.

---

## ⭐ Support

If you like this project:

* ⭐ Star the repo
* 🔗 Share the deployed link

---

