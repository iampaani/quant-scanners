import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import ta
import requests

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Master Quant Dashboard", layout="wide")
st.title("🦅 Master Quant Terminal: F&O Universe")
st.write("Macro scanning and Micro analysis for high-probability quantitative setups.")

# --- THE F&O BASKETS ---
fno_stocks = {
    "Aarti Industries": "AARTIIND.NS", "Adani Enterprises": "ADANIENT.NS", "Adani Ports": "ADANIPORTS.NS",
    "Ambuja Cements": "AMBUJACEM.NS", "Angel One": "ANGELONE.NS", "Apollo Hospitals": "APOLLOHOSP.NS", 
    "Ashok Leyland": "ASHOKLEY.NS", "Asian Paints": "ASIANPAINT.NS", "Astral": "ASTRAL.NS", 
    "Axis Bank": "AXISBANK.NS", "Bajaj Auto": "BAJAJ-AUTO.NS", "Bajaj Finance": "BAJFINANCE.NS", 
    "Bajaj Finserv": "BAJAJFINSV.NS", "Bandhan Bank": "BANDHANBNK.NS", "Bank of Baroda": "BANKBARODA.NS", 
    "Bharti Airtel": "BHARTIARTL.NS", "BHEL": "BHEL.NS", "BPCL": "BPCL.NS", "Britannia": "BRITANNIA.NS", 
    "Canara Bank": "CANBK.NS", "Cholamandalam Inv": "CHOLAFIN.NS", "Cipla": "CIPLA.NS", "Coal India": "COALINDIA.NS",
    "Coforge": "COFORGE.NS", "DLF": "DLF.NS", "Dixon Tech": "DIXON.NS", "Dr. Reddy's": "DRREDDY.NS",
    "Eicher Motors": "EICHERMOT.NS", "Federal Bank": "FEDERALBNK.NS", "Godrej Properties": "GODREJPROP.NS",
    "Grasim": "GRASIM.NS", "HAL": "HAL.NS", "HCL Tech": "HCLTECH.NS", "HDFC Bank": "HDFCBANK.NS",
    "HDFC Life": "HDFCLIFE.NS", "Hero MotoCorp": "HEROMOTOCO.NS", "Hindalco": "HINDALCO.NS",
    "Hindustan Unilever": "HINDUNILVR.NS", "ICICI Bank": "ICICIBANK.NS", "IDFC First Bank": "IDFCFIRSTB.NS",
    "Indian Hotels": "INDHOTEL.NS", "IndusInd Bank": "INDUSINDBK.NS", "Infosys": "INFY.NS",
    "ITC": "ITC.NS", "JSW Steel": "JSWSTEEL.NS", "Kotak Mahindra Bank": "KOTAKBANK.NS",
    "Larsen & Toubro": "LT.NS", "LTIMindtree": "LTIM.NS", "Lupin": "LUPIN.NS", "Mahindra & Mahindra": "M&M.NS",
    "Maruti Suzuki": "MARUTI.NS", "NTPC": "NTPC.NS", "ONGC": "ONGC.NS", "Polycab": "POLYCAB.NS",
    "Power Grid": "POWERGRID.NS", "Reliance Industries": "RELIANCE.NS", "State Bank of India": "SBIN.NS",
    "Sun Pharma": "SUNPHARMA.NS", "Tata Motors": "TATAMOTORS.NS", "Tata Power": "TATAPOWER.NS",
    "Tata Steel": "TATASTEEL.NS", "TCS": "TCS.NS", "Tech Mahindra": "TECHM.NS", "Titan": "TITAN.NS",
    "TVS Motor": "TVSMOTOR.NS", "UltraTech Cement": "ULTRACEMCO.NS", "Vedanta": "VEDL.NS", "Wipro": "WIPRO.NS"
}

fno_basket_yf = list(fno_stocks.values())
fno_basket_clean = [ticker.replace('.NS', '') for ticker in fno_basket_yf]

# --- TELEGRAM ENGINE ---
def send_telegram_message(message):
    """Sends an instant push notification to your phone."""
    try:
        # Pulls your secure keys from the Streamlit vault
        token = st.secrets["TELEGRAM_BOT_TOKEN"]
        chat_id = st.secrets["TELEGRAM_CHAT_ID"]

        # The API trigger
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}
        requests.post(url, data=payload)
        return True
    except Exception as e:
        # Fails silently on your local Mac if secrets aren't set, but prints an error
        st.sidebar.error("⚠️ Telegram secrets not found. Alerts will not send.")
        return False


def send_squeeze_alert(stock, price_change_pct):
    message = f"🚨 **MASSIVE SQUEEZE DETECTED** 🚨\n\n🎯 Stock: {stock}\n💰 Price Chg: {price_change_pct}%\n\nBears are trapped. Volume is spiking. VWAP Reclaimed. Look for entry."
    return send_telegram_message(message)

# --- SECTOR BASKETS (for Smart Money Sector Scanner) ---
sectors = {
    "Banking & Financial": {
        "HDFC Bank": "HDFCBANK.NS",
        "ICICI Bank": "ICICIBANK.NS",
        "State Bank of India": "SBIN.NS",
        "Axis Bank": "AXISBANK.NS",
        "Kotak Mahindra": "KOTAKBANK.NS",
        "IndusInd Bank": "INDUSINDBK.NS",
        "Punjab National Bank": "PNB.NS",
        "Bank of Baroda": "BANKBARODA.NS",
        "Federal Bank": "FEDERALBNK.NS",
        "IDFC First Bank": "IDFCFIRSTB.NS",
        "AU Small Finance": "AUBANK.NS",
        "Bandhan Bank": "BANDHANBNK.NS",
        "Bajaj Finance": "BAJFINANCE.NS",
        "Bajaj Finserv": "BAJAJFINSV.NS",
        "Cholamandalam Inv": "CHOLAFIN.NS"
    },
    "FMCG (Defensive)": {
        "ITC": "ITC.NS",
        "Hindustan Unilever": "HINDUNILVR.NS",
        "Nestle India": "NESTLEIND.NS",
        "Britannia": "BRITANNIA.NS",
        "Tata Consumer": "TATACONSUM.NS",
        "Godrej Consumer": "GODREJCP.NS",
        "Dabur India": "DABUR.NS",
        "Marico": "MARICO.NS",
        "Varun Beverages": "VBL.NS",
        "Colgate Palmolive": "COLPAL.NS",
        "United Breweries": "UBL.NS",
        "United Spirits": "MCDOWELL-N.NS",
        "Emami": "EMAMILTD.NS",
        "Balrampur Chini": "BALRAMCHIN.NS",
        "Radico Khaitan": "RADICO.NS"
    },
    "Information Technology": {
        "TCS": "TCS.NS",
        "Infosys": "INFY.NS",
        "HCL Tech": "HCLTECH.NS",
        "Wipro": "WIPRO.NS",
        "Tech Mahindra": "TECHM.NS",
        "LTIMindtree": "LTIM.NS",
        "Persistent Systems": "PERSISTENT.NS",
        "Coforge": "COFORGE.NS",
        "Mphasis": "MPHASIS.NS",
        "KPIT Tech": "KPITTECH.NS",
        "Tata Elxsi": "TATAELXSI.NS",
        "Cyient": "CYIENT.NS",
        "Sonata Software": "SONATSOFTW.NS",
        "Zensar Tech": "ZENSARTECH.NS",
        "Birlasoft": "BSOFT.NS"
    },
    "Energy & Oil": {
        "Reliance Industries": "RELIANCE.NS",
        "ONGC": "ONGC.NS",
        "NTPC": "NTPC.NS",
        "Power Grid": "POWERGRID.NS",
        "Tata Power": "TATAPOWER.NS",
        "Coal India": "COALINDIA.NS",
        "Indian Oil Corp (IOC)": "IOC.NS",
        "Bharat Petroleum (BPCL)": "BPCL.NS",
        "Hindustan Petroleum": "HINDPETRO.NS",
        "GAIL India": "GAIL.NS",
        "Indraprastha Gas": "IGL.NS",
        "Mahanagar Gas": "MGL.NS",
        "Adani Green": "ADANIGREEN.NS",
        "Adani Power": "ADANIPOWER.NS",
        "JSW Energy": "JSWENERGY.NS"
    },
    "Real Estate": {
        "DLF": "DLF.NS",
        "Macrotech (Lodha)": "LODHA.NS",
        "Godrej Properties": "GODREJPROP.NS",
        "Oberoi Realty": "OBEROIRLTY.NS",
        "Prestige Estates": "PRESTIGE.NS",
        "Phoenix Mills": "PHOENIXLTD.NS",
        "Brigade Enterprises": "BRIGADE.NS",
        "Sobha": "SOBHA.NS",
        "Mahindra Lifespace": "MAHLIFE.NS",
        "Sunteck Realty": "SUNTECK.NS",
        "Puravankara": "PURVA.NS",
        "Indiabulls Real Estate": "IBREALEST.NS",
        "Hemisphere Properties": "HEMIPROP.NS",
        "Kolte-Patil": "KOLTEPATIL.NS",
        "Ashiana Housing": "ASHIANA.NS"
    },
    "Mid Cap (Risk-On)": {
        "Delhivery": "DELHIVERY.NS",
        "Indian Hotels": "INDHOTEL.NS",
        "Dixon Tech": "DIXON.NS",
        "Polycab India": "POLYCAB.NS",
        "Cummins India": "CUMMINSIND.NS",
        "Trent": "TRENT.NS",
        "TVS Motor": "TVSMOTOR.NS",
        "Astral": "ASTRAL.NS",
        "Max Healthcare": "MAXHEALTH.NS",
        "Voltas": "VOLTAS.NS",
        "Escorts Kubota": "ESCORTS.NS",
        "Oracle Fin Services": "OFSS.NS",
        "Lupin": "LUPIN.NS",
        "PI Industries": "PIIND.NS",
        "Coromandel Int": "COROMANDEL.NS"
    },
    "Small Cap (High Beta)": {
        "MTAR Technologies": "MTARTECH.NS",
        "MCX India": "MCX.NS",
        "CDSL": "CDSL.NS",
        "BSE Limited": "BSE.NS",
        "Angel One": "ANGELONE.NS",
        "CAMS": "CAMS.NS",
        "Latent View Analytics": "LATENTVIEW.NS",
        "CE Info Systems (MapMyIndia)": "CEINFO.NS",
        "Happiest Minds": "HAPPSTMNDS.NS",
        "Route Mobile": "ROUTE.NS",
        "Redington": "REDINGTON.NS",
        "Trident": "TRIDENT.NS",
        "Shree Renuka Sugars": "RENUKA.NS",
        "Suzlon Energy": "SUZLON.NS",
        "HCC": "HCC.NS"
    }
}

# --- INDEX UNIVERSE (for Options & Futures Analyzer) ---
index_instruments = {
    "Nifty 50": "^NSEI",
    "Bank Nifty": "^NSEBANK"
}

# --- UI: CREATE TABS ---
tab1, tab2, tab3, tab4, tab5 = st.tabs(["⚡ Z-Score Scanner", "🚀 Short Squeeze Radar", "🔬 Micro-Anatomy Analyzer", "🎯 Smart Money Sector Scanner", "📉 Options & Futures Analyzer"])

# ==========================================
# ENGINE 1: Z-SCORE SCANNER (TAB 1)
# ==========================================
with tab1:
    st.header("⚡ F&O Universe: Price Z-Score Scanner")
    st.write("Hunting for extreme mean-reversion setups across highly liquid derivatives.")

    col1, col2 = st.columns(2)
    with col1:
        window = st.slider("Rolling Window (Days)", 10, 100, 20, key="z_window")
    with col2:
        z_threshold = st.slider("Actionable Z-Score Threshold", 1.5, 3.0, 2.0, step=0.1, key="z_thresh")

    @st.cache_data(ttl=300)
    def calculate_fno_zscores(tickers, lookback, threshold):
        results = []

        # Download data in one fast batch
        data = yf.download(tickers, period="6mo", interval="1d", progress=False)['Close']

        if data.empty:
            return pd.DataFrame()

        # Flatten yfinance data structure if needed
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.droplevel(1)

        for ticker in tickers:
            if ticker in data.columns:
                df = data[[ticker]].dropna().copy()
                if len(df) < lookback:
                    continue

                # The Math
                df['Mean'] = df[ticker].rolling(window=lookback).mean()
                df['StdDev'] = df[ticker].rolling(window=lookback).std()
                df['Z-Score'] = (df[ticker] - df['Mean']) / df['StdDev']

                current_price = df[ticker].iloc[-1]
                current_z = df['Z-Score'].iloc[-1]

                if pd.isna(current_z):
                    continue

                # Trade Logic Engine
                if current_z >= threshold:
                    signal = "🔴 OVERBOUGHT (Look to Short)"
                elif current_z <= -threshold:
                    signal = "🟢 OVERSOLD (Look to Buy)"
                else:
                    signal = "➖ NEUTRAL"

                results.append({
                    "F&O Stock": ticker.replace('.NS', ''),
                    "Current Price": f"₹{current_price:.2f}",
                    "Z-Score": round(current_z, 2),
                    "Signal": signal
                })

        if not results:
            return pd.DataFrame()

        # Sort so the most extreme setups are at the top
        return pd.DataFrame(results).sort_values(by="Z-Score", ascending=False, key=abs)

    st.write(f"Calculating current {window}-day Z-Scores across {len(fno_basket_yf)} F&O stocks...")
    df_zscore = calculate_fno_zscores(fno_basket_yf, window, z_threshold)

    if not df_zscore.empty:
        # Filter for actionable extremes
        actionable_df = df_zscore[df_zscore['Signal'] != "➖ NEUTRAL"]

        st.subheader("🔥 Actionable Extremes (Mean Reversion)")
        if actionable_df.empty:
            st.success(f"No F&O stocks are stretched beyond a Z-Score of {z_threshold} right now. The market is mathematically balanced.")
        else:
            st.error("These stocks have violently detached from their moving average. High probability of snapping back.")
            st.table(actionable_df.set_index('F&O Stock'))

        st.divider()
        st.subheader("📊 Full Basket Overview")

        # Apply color styling to the Z-Score column
        def highlight_zscore_fno(val):
            color = '#ff4b4b' if val >= z_threshold else '#00cc96' if val <= -z_threshold else 'gray'
            weight = 'bold' if abs(val) >= z_threshold else 'normal'
            return f'color: {color}; font-weight: {weight}'

        styled_df = df_zscore.style.map(highlight_zscore_fno, subset=['Z-Score'])
        st.dataframe(styled_df, use_container_width=True)
    else:
        st.error("Could not fetch market data.")

    st.divider()

    if not df_zscore.empty and not actionable_df.empty:
        if st.button("🔔 Send Telegram Alerts for Actionable Z-Scores", key="z_alert_btn"):
            sent = 0
            for _, row in actionable_df.iterrows():
                message = (
                    f"🚨 **Z-SCORE ALERT** 🚨\n\n"
                    f"🎯 Stock: {row['F&O Stock']}\n"
                    f"💰 Price: {row['Current Price']}\n"
                    f"📊 Z-Score: {row['Z-Score']}\n"
                    f"📣 Signal: {row['Signal']}"
                )
                if send_telegram_message(message):
                    sent += 1
            st.success(f"Sent {sent} Telegram alert(s).")
    else:
        st.caption("No actionable Z-Scores to alert on right now.")

# ==========================================
# ENGINE 2: SHORT SQUEEZE RADAR (TAB 2)
# ==========================================
with tab2:
    st.header("🚀 Institutional Short Squeeze Radar")
    st.write("Hunting for trapped bears using the Triple Confirmation method: OI Drop + Volume Spike + VWAP Reclaim.")
    st.info("ℹ️ OI/Volume/VWAP data below is **simulated** — yfinance has no live options-chain feed. Wire `fetch_squeeze_data()` up to a real provider (e.g. TrueData, Global Datafeeds) for live ticks.")

    @st.cache_data(ttl=60)
    def fetch_squeeze_data(tickers):
        """
        Simulates live Price, OI, Volume, and VWAP data.
        When your API is live, replace this to pull actual tick data.
        """
        np.random.seed()
        results = []

        for ticker in tickers:
            # 1. Simulate Price & OI
            price_change_pct = np.random.uniform(-2.0, 5.0)
            oi_change_pct = np.random.uniform(-10.0, 5.0)

            # 2. Simulate Volume (1.0 = Average, 2.0 = Double normal volume)
            relative_volume = np.random.uniform(0.5, 3.0)

            # 3. Simulate VWAP relationship
            is_above_vwap = True if price_change_pct > 1.0 else np.random.choice([True, False])

            # --- TRIPLE CONFIRMATION LOGIC ---
            squeeze_score = 0
            status = "➖ Neutral / No Squeeze"

            if price_change_pct > 0 and oi_change_pct < -2.0:
                squeeze_score += 1
                if relative_volume > 1.5:
                    squeeze_score += 1
                    if is_above_vwap:
                        squeeze_score += 1

            if squeeze_score == 3:
                status = "🔥 MASSIVE SQUEEZE"
            elif squeeze_score == 2:
                status = "⚠️ Squeeze Building"

            results.append({
                "Stock": ticker,
                "Price Chg (%)": round(price_change_pct, 2),
                "OI Chg (%)": round(oi_change_pct, 2),
                "Relative Vol (x)": round(relative_volume, 2),
                "Above VWAP": "✅ Yes" if is_above_vwap else "❌ No",
                "Squeeze Status": status,
                "Score": squeeze_score
            })

        # Sort so the highest conviction squeezes are at the top
        return pd.DataFrame(results).sort_values(by="Score", ascending=False)

    st.write("Running Triple Confirmation Math across the F&O basket...")
    df_squeeze = fetch_squeeze_data(fno_basket_clean)

    # 1. The High Conviction Squeezes
    st.subheader("🎯 High Conviction Targets (Score 3/3)")
    high_conviction_df = df_squeeze[df_squeeze['Score'] == 3].drop(columns=['Score'])

    if not high_conviction_df.empty:
        st.error("**ALERT: Perfect Storm Detected.** Bears are trapped, volume is exploding, and buyers have reclaimed VWAP.")
        st.table(high_conviction_df.set_index('Stock'))

        if st.button("🔔 Send Telegram Alerts for High Conviction Squeezes"):
            sent = 0
            for _, row in high_conviction_df.iterrows():
                if send_squeeze_alert(row['Stock'], row['Price Chg (%)']):
                    sent += 1
            st.success(f"Sent {sent} Telegram alert(s).")
    else:
        st.info("No perfect 3/3 squeezes detected right now.")

    st.divider()

    # 2. Building Squeezes (Watchlist)
    st.subheader("👀 Squeeze Watchlist (Score 2/3)")
    building_df = df_squeeze[df_squeeze['Score'] == 2].drop(columns=['Score'])

    if not building_df.empty:
        st.warning("These stocks are showing heavy short covering, but are missing either the Volume spike or haven't crossed VWAP yet. Keep on radar.")
        st.table(building_df.set_index('Stock'))
    else:
        st.info("No building squeezes at the moment.")

    st.divider()

    # 3. Full Data Matrix
    st.subheader("📊 Full Market Raw Data")

    def highlight_squeeze(val):
        if "MASSIVE" in str(val):
            color = '#00cc96'
            weight = 'bold'
        elif "Building" in str(val):
            color = 'orange'
            weight = 'bold'
        else:
            color = 'gray'
            weight = 'normal'
        return f'color: {color}; font-weight: {weight}'

    styled_df = df_squeeze.drop(columns=['Score']).style.map(highlight_squeeze, subset=['Squeeze Status'])
    st.dataframe(styled_df, use_container_width=True)

# ==========================================
# ENGINE 3: MICRO-ANATOMY ANALYZER (TAB 3)
# ==========================================
with tab3:
    st.header("🔬 F&O Universe: Micro-Anatomy Analyzer")
    st.write("Deep quantitative analysis on a single asset to generate a definitive trading verdict.")

    selected_name = st.selectbox("Select F&O Stock for Deep Analysis:", list(fno_stocks.keys()), key="micro_select")
    ticker = fno_stocks[selected_name]
    st.divider()

    @st.cache_data(ttl=60)
    def analyze_stock(ticker):
        # Fetch 1 year of daily data for robust moving averages
        stock = yf.Ticker(ticker)
        df = stock.history(period="1y")

        if df.empty or len(df) < 50:
            return None

        close = df['Close']
        open_price = df['Open']
        volume = df['Volume']

        # 1. EMAs for Trend
        df['EMA_20'] = ta.trend.ema_indicator(close, window=20)
        df['EMA_50'] = ta.trend.ema_indicator(close, window=50)

        # 2. RSI for Exhaustion
        df['RSI'] = ta.momentum.rsi(close, window=14)

        # 3. MACD for Momentum
        macd = ta.trend.MACD(close)
        df['MACD'] = macd.macd()
        df['MACD_Signal'] = macd.macd_signal()

        # 4. Z-Score (Mean Reversion)
        mean_20 = close.rolling(window=20).mean()
        std_20 = close.rolling(window=20).std()
        df['Z_Score'] = (close - mean_20) / std_20

        # 5. OBV (Smart Money Footprint)
        df['OBV'] = ta.volume.on_balance_volume(close, volume)
        df['OBV_SMA'] = df['OBV'].rolling(window=20).mean()

        # 6. Candlestick Pattern Recognition (Last 3 Days)
        c1, c2, c3 = close.iloc[-3], close.iloc[-2], close.iloc[-1]
        o1, o2, o3 = open_price.iloc[-3], open_price.iloc[-2], open_price.iloc[-1]

        three_white_soldiers = (c1 > o1) and (c2 > o2) and (c3 > o3) and (c3 > c2 > c1)
        three_black_crows = (c1 < o1) and (c2 < o2) and (c3 < o3) and (c3 < c2 < c1)

        return df, three_white_soldiers, three_black_crows

    st.write(f"Running high-speed diagnostics on **{selected_name}**...")
    results = analyze_stock(ticker)

    if results is not None:
        df, three_white_soldiers, three_black_crows = results
        latest = df.iloc[-1]

        current_price = latest['Close']
        rsi = latest['RSI']
        z_score = latest['Z_Score']
        trend_up = latest['EMA_20'] > latest['EMA_50']
        macd_bullish = latest['MACD'] > latest['MACD_Signal']
        smart_money_in = latest['OBV'] > latest['OBV_SMA']

        # --- BUILDING THE EXACT VERDICT ---
        st.subheader(f"🧠 The Verdict: {selected_name} @ ₹{current_price:.2f}")

        if trend_up and rsi < 70 and smart_money_in and macd_bullish:
            verdict_text = "🔥 HIGH PROBABILITY BUY. The trend is bullish, smart money is accumulating, and the price is not yet exhausted."
            verdict_color = "green"
        elif trend_up and rsi >= 70:
            verdict_text = "⚠️ TRAP WARNING. The stock is in an uptrend, but it is mathematically overbought (RSI > 70). Do not chase. Wait for a pullback to the 20 EMA."
            verdict_color = "orange"
        elif not trend_up and rsi <= 30 and z_score <= -2.0:
            verdict_text = "🎯 SNIPER REVERSAL ZONE. The trend is bearish, but the price is violently oversold and stretched far below its mean. Watch for a bounce."
            verdict_color = "blue"
        elif not trend_up and not smart_money_in:
            verdict_text = "🩸 DO NOT TOUCH. The trend is broken and institutions are distributing shares. Capital preservation is priority."
            verdict_color = "red"
        else:
            verdict_text = "⚖️ CHOP ZONE. The quantitative signals are mixed. The stock is likely consolidating sideways. Deploy capital elsewhere."
            verdict_color = "gray"

        st.markdown(f"<h3 style='color: {verdict_color};'>{verdict_text}</h3>", unsafe_allow_html=True)
        st.divider()

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("### 📈 Trend & Momentum")
            st.write(f"**20/50 EMA Structure:** {'🟢 Bullish' if trend_up else '🔴 Bearish'}")
            st.write(f"**MACD Signal:** {'🟢 Buy Momentum' if macd_bullish else '🔴 Sell Momentum'}")

        with col2:
            st.markdown("### 🧲 Smart Money & Volume")
            st.write(f"**OBV (Accumulation):** {'🟢 Capital Inflow' if smart_money_in else '🔴 Capital Outflow'}")
            if three_white_soldiers:
                st.success("🚨 PATTERN: Three White Soldiers Detected! Strong institutional buying.")
            elif three_black_crows:
                st.error("🚨 PATTERN: Three Black Crows Detected! Aggressive institutional dumping.")
            else:
                st.write("**Candlestick Pattern:** ➖ Normal Price Action")

        with col3:
            st.markdown("### ⚡ Exhaustion (Mean Reversion)")
            st.write(f"**RSI (14):** {rsi:.1f} - " +
                     ("🔴 Overbought" if rsi > 70 else "🟢 Oversold" if rsi < 30 else "➖ Neutral"))
            st.write(f"**Z-Score:** {z_score:.2f} - " +
                     ("🔴 Stretched High" if z_score > 2 else "🟢 Stretched Low" if z_score < -2 else "➖ Inside Normal Band"))

        st.divider()
        if st.button("🔔 Send Telegram Alert for This Verdict", key="micro_alert_btn"):
            message = (
                f"🧠 **MICRO-ANATOMY VERDICT** 🧠\n\n"
                f"🎯 Stock: {selected_name}\n"
                f"💰 Price: ₹{current_price:.2f}\n"
                f"📣 Verdict: {verdict_text}\n\n"
                f"RSI: {rsi:.1f} | Z-Score: {z_score:.2f}\n"
                f"Trend: {'Bullish' if trend_up else 'Bearish'} | MACD: {'Bullish' if macd_bullish else 'Bearish'} | Smart Money: {'Inflow' if smart_money_in else 'Outflow'}"
            )
            if send_telegram_message(message):
                st.success("Telegram alert sent.")
    else:
        st.error("Market data currently unavailable for this ticker.")

# ==========================================
# ENGINE 4: SMART MONEY SECTOR SCANNER (TAB 4)
# ==========================================
with tab4:
    st.header("🎯 Top-Down Smart Money Scanner (Pro Edition)")
    st.write("Tracking institutional accumulation (OBV) across 100+ market heavyweights.")

    selected_sector = st.selectbox("Select Sector or Cap Size to Scan:", list(sectors.keys()), key="sector_select")
    st.divider()

    @st.cache_data(ttl=300)
    def scan_smart_money(sector_name):
        stock_dict = sectors[sector_name]
        results = []
        accumulation_count = 0

        for name, ticker in stock_dict.items():
            # Fetch 6 months of daily data
            data = yf.download(ticker, period="6mo", interval="1d", progress=False)

            if data.empty or len(data) < 50:
                continue

            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.droplevel(1)

            close_price = data['Close']
            volume = data['Volume']

            # 1. SMART MONEY (OBV)
            obv = ta.volume.OnBalanceVolumeIndicator(close=close_price, volume=volume).on_balance_volume()
            obv_sma = obv.rolling(window=20).mean()  # 20-day average of institutional volume

            current_obv = obv.iloc[-1]
            current_obv_sma = obv_sma.iloc[-1]

            if current_obv > current_obv_sma:
                smart_money_status = "🟢 Accumulation"
                accumulation_count += 1
            else:
                smart_money_status = "🔴 Distribution"

            # 2. TREND MOMENTUM (MACD)
            macd = ta.trend.MACD(close=close_price)
            current_macd = macd.macd().iloc[-1]
            current_signal = macd.macd_signal().iloc[-1]

            if current_macd > current_signal:
                trend_status = "↗️ Bullish"
            else:
                trend_status = "↘️ Bearish"

            # 3. VOLATILITY / EXHAUSTION (RSI)
            rsi = ta.momentum.RSIIndicator(close=close_price).rsi().iloc[-1]

            results.append({
                "Stock": name,
                "Latest Price": f"₹{close_price.iloc[-1]:.2f}",
                "Smart Money (OBV)": smart_money_status,
                "Trend (MACD)": trend_status,
                "RSI (14)": round(rsi, 1)
            })

        return pd.DataFrame(results), accumulation_count, len(stock_dict)

    # --- EXECUTE SCAN ---
    st.write(f"Scanning institutional order flow for **{selected_sector}**... *(This takes a few seconds for 15 stocks)*")
    df_results, acc_count, total_stocks = scan_smart_money(selected_sector)

    if not df_results.empty:
        # --- SECTOR HEALTH SUMMARY ---
        st.subheader("Macro Segment Health")
        health_percentage = (acc_count / total_stocks) * 100

        if health_percentage >= 60:
            st.success(f"🔥 **CAPITAL INFLOW:** {acc_count} out of {total_stocks} heavyweights are showing Smart Money Accumulation. Institutions are aggressively buying this segment.")
        elif health_percentage <= 40:
            st.error(f"⚠️ **CAPITAL OUTFLOW:** Only {acc_count} out of {total_stocks} heavyweights are accumulating. Institutions are draining capital from this segment.")
        else:
            st.warning(f"⚖️ **NEUTRAL:** {acc_count} out of {total_stocks} heavyweights are accumulating. The segment is consolidating without clear direction.")

        st.divider()

        # --- INDIVIDUAL STOCK BREAKDOWN ---
        st.subheader("Micro Stock Breakdown")
        st.table(df_results.set_index('Stock'))

        # --- TRADING LOGIC RULES ---
        st.markdown("""
        ### 🧠 How to Trade This Data:
        1. **The Sniper Setup:** Only buy a stock showing **🟢 Accumulation** and a **↗️ Bullish** trend IF the overall Macro Segment Health is also showing **CAPITAL INFLOW**.
        2. **The Trap:** If a stock is showing a Bullish trend, but the Smart Money status is **🔴 Distribution**, retail traders are buying the breakout while institutions are quietly dumping shares. Avoid it.
        """)

        st.divider()
        sniper_df = df_results[
            (df_results['Smart Money (OBV)'] == "🟢 Accumulation") &
            (df_results['Trend (MACD)'] == "↗️ Bullish")
        ]

        if health_percentage >= 60 and not sniper_df.empty:
            if st.button("🔔 Send Telegram Alerts for Sniper Setups", key="smart_money_alert_btn"):
                sent = 0
                for _, row in sniper_df.iterrows():
                    message = (
                        f"🎯 **SNIPER SETUP: {selected_sector}** 🎯\n\n"
                        f"🎯 Stock: {row['Stock']}\n"
                        f"💰 Price: {row['Latest Price']}\n"
                        f"🟢 Smart Money: Accumulation\n"
                        f"↗️ Trend: Bullish\n"
                        f"RSI (14): {row['RSI (14)']}\n\n"
                        f"Sector Capital Inflow confirmed ({acc_count}/{total_stocks} accumulating)."
                    )
                    if send_telegram_message(message):
                        sent += 1
                st.success(f"Sent {sent} Telegram alert(s).")
        else:
            st.caption("No confirmed Sniper Setups (Accumulation + Bullish + sector-wide Capital Inflow) to alert on right now.")
    else:
        st.error("Market data currently unavailable.")

# ==========================================
# ENGINE 5: OPTIONS & FUTURES ANALYZER (TAB 5)
# ==========================================
with tab5:
    st.header("📉 Nifty 50 / Bank Nifty: Options & Futures Analyzer")
    st.write("Realized-volatility regime crossed with trend to suggest an options strategy archetype.")
    st.info("ℹ️ NSE index options aren't available through yfinance (no live IV/OI/strikes), so volatility here is **realized (historical)**, computed from price history — not implied volatility. Treat the strategy label as an archetype, not a specific trade.")
    st.divider()

    period_options = {"1 Month": "1mo", "3 Months": "3mo", "6 Months": "6mo", "1 Year": "1y"}
    period_label = st.selectbox("Lookback Period:", list(period_options.keys()), index=1, key="options_period_select")
    period = period_options[period_label]

    index_strike_step = {"Nifty 50": 50, "Bank Nifty": 100}

    @st.cache_data(ttl=300)
    def analyze_options_futures(ticker, period):
        stock = yf.Ticker(ticker)
        df = stock.history(period=period)

        if df.empty or len(df) < 15:
            return None

        close = df['Close']
        n = len(close)

        # Windows scale down for shorter lookback periods so every period is usable
        long_window = min(50, max(10, n // 2))
        short_window = max(5, long_window // 2)
        vol_window = min(20, max(5, n // 3))
        signal_window = max(3, short_window // 2)

        # 1. REALIZED VOLATILITY (annualized %)
        log_returns = np.log(close / close.shift(1))
        realized_vol = (log_returns.rolling(window=vol_window).std() * np.sqrt(252) * 100).dropna()

        if realized_vol.empty:
            return None

        current_vol = realized_vol.iloc[-1]
        # Percentile rank of today's vol against its own history over this period
        vol_percentile = (realized_vol < current_vol).mean() * 100

        if vol_percentile >= 70:
            vol_regime = "High"
        elif vol_percentile <= 30:
            vol_regime = "Low"
        else:
            vol_regime = "Medium"

        # 2. TREND (EMA structure + MACD, windows adaptive to the period)
        ema_short = ta.trend.ema_indicator(close, window=short_window)
        ema_long = ta.trend.ema_indicator(close, window=long_window)
        macd = ta.trend.MACD(close, window_slow=long_window, window_fast=short_window, window_sign=signal_window)
        macd_line = macd.macd()
        macd_signal_line = macd.macd_signal()

        trend_up = ema_short.iloc[-1] > ema_long.iloc[-1] and macd_line.iloc[-1] > macd_signal_line.iloc[-1]
        trend_down = ema_short.iloc[-1] < ema_long.iloc[-1] and macd_line.iloc[-1] < macd_signal_line.iloc[-1]

        # 3. Z-SCORE (price mean-reversion, same window as volatility)
        mean_price = close.rolling(window=vol_window).mean()
        std_price = close.rolling(window=vol_window).std()
        current_price = close.iloc[-1]
        price_std = std_price.iloc[-1]
        z_score = (current_price - mean_price.iloc[-1]) / price_std if price_std else 0.0

        return {
            "current_price": current_price,
            "current_vol": current_vol,
            "vol_percentile": vol_percentile,
            "vol_regime": vol_regime,
            "trend_up": trend_up,
            "trend_down": trend_down,
            "z_score": z_score,
            "price_std": price_std,
            "vol_window": vol_window,
        }

    def suggest_strikes(current_price, price_std, step):
        def r(x):
            return int(round(x / step) * step)
        return {
            "atm": r(current_price),
            "call_1s": r(current_price + price_std),
            "call_2s": r(current_price + 2 * price_std),
            "put_1s": r(current_price - price_std),
            "put_2s": r(current_price - 2 * price_std),
        }

    def render_index_analysis(container, index_name, ticker):
        with container:
            st.write(f"Running volatility + trend diagnostics on **{index_name}** ({period_label})...")
            result = analyze_options_futures(ticker, period)

            if result is None:
                st.error(f"Not enough market data for {index_name} over {period_label} to run this analysis.")
                return

            current_price = result["current_price"]
            current_vol = result["current_vol"]
            vol_percentile = result["vol_percentile"]
            vol_regime = result["vol_regime"]
            trend_up = result["trend_up"]
            trend_down = result["trend_down"]
            z_score = result["z_score"]
            price_std = result["price_std"]
            vol_window = result["vol_window"]

            trend_label = "Bullish" if trend_up else "Bearish" if trend_down else "Range-bound"

            # --- STRATEGY ARCHETYPE MATRIX ---
            if vol_regime == "High":
                if trend_up:
                    strategy = "Bull Call Spread"
                    rationale = "Volatility is elevated (expensive premium) and momentum is bullish — cap cost by buying a call and selling a further OTM call."
                    color = "green"
                elif trend_down:
                    strategy = "Bear Put Spread"
                    rationale = "Volatility is elevated and momentum is bearish — cap cost by buying a put and selling a further OTM put."
                    color = "red"
                else:
                    strategy = "Short Straddle / Iron Condor"
                    rationale = "Volatility is stretched high with no clear trend — favor selling premium and expecting it to mean-revert."
                    color = "orange"
            elif vol_regime == "Low":
                if trend_up:
                    strategy = "Long Call"
                    rationale = "Volatility is compressed (cheap premium) and momentum is bullish — a plain long call has room to benefit from a vol expansion too."
                    color = "green"
                elif trend_down:
                    strategy = "Long Put"
                    rationale = "Volatility is compressed and momentum is bearish — a plain long put has room to benefit from a vol expansion too."
                    color = "red"
                else:
                    strategy = "No Trade — Wait for a Catalyst"
                    rationale = "Volatility is compressed and there's no clear trend — low edge for either direction or premium selling right now."
                    color = "gray"
            else:  # Medium
                if trend_up:
                    strategy = "Bull Call Spread or Long Call"
                    rationale = "Volatility is moderate with bullish momentum — a spread trims cost, a plain call keeps more upside."
                    color = "green"
                elif trend_down:
                    strategy = "Bear Put Spread or Long Put"
                    rationale = "Volatility is moderate with bearish momentum — a spread trims cost, a plain put keeps more downside."
                    color = "red"
                else:
                    strategy = "Calendar Spread / Wait"
                    rationale = "Volatility is moderate with no clear trend — mixed signals, no strong directional or premium edge."
                    color = "gray"

            st.subheader(f"🧠 {index_name} @ ₹{current_price:.2f}")
            st.markdown(f"<h3 style='color: {color};'>{strategy}</h3>", unsafe_allow_html=True)
            st.write(rationale)
            st.divider()

            st.markdown("### 📊 Realized Volatility")
            st.write(f"**{vol_window}-Day Realized Vol (Annualized):** {current_vol:.1f}%")
            st.write(f"**{period_label} Percentile:** {vol_percentile:.0f}th")
            st.write(f"**Regime:** {'🔴 High' if vol_regime == 'High' else '🟢 Low' if vol_regime == 'Low' else '🟡 Medium'}")

            st.markdown("### 📈 Trend")
            st.write(f"**EMA + MACD Structure:** {trend_label}")
            st.write(f"**Direction:** {'🟢 Bullish' if trend_up else '🔴 Bearish' if trend_down else '➖ Mixed'}")

            st.markdown("### 🎯 Strategy Archetype")
            st.write(f"**Suggested Setup:** {strategy}")

            st.markdown("### 📐 Z-Score & Suggested Strike Zones")
            st.write(f"**Z-Score ({vol_window}D price):** {z_score:.2f} — " +
                     ("🔴 Stretched High" if z_score > 2 else "🟢 Stretched Low" if z_score < -2 else "➖ Inside Normal Band"))

            step = index_strike_step.get(index_name, 50)
            strikes = suggest_strikes(current_price, price_std, step)
            strike_lines = []

            if "Call" in strategy:
                strike_lines.append(f"**Buy Call:** ~₹{strikes['atm']} (ATM)")
                if "Spread" in strategy:
                    strike_lines.append(f"**Sell Call:** ~₹{strikes['call_1s']} (+1σ)")
            elif "Put" in strategy:
                strike_lines.append(f"**Buy Put:** ~₹{strikes['atm']} (ATM)")
                if "Spread" in strategy:
                    strike_lines.append(f"**Sell Put:** ~₹{strikes['put_1s']} (-1σ)")
            elif "Straddle" in strategy or "Condor" in strategy:
                strike_lines.append(f"**Sell Call:** ~₹{strikes['call_1s']} (+1σ)")
                strike_lines.append(f"**Sell Put:** ~₹{strikes['put_1s']} (-1σ)")
                strike_lines.append(f"*Optional wings (Iron Condor): Buy Call ~₹{strikes['call_2s']} (+2σ) / Buy Put ~₹{strikes['put_2s']} (-2σ)*")

            if strike_lines:
                for line in strike_lines:
                    st.write(line)
            else:
                st.write("No strike zone suggested — no clear directional or premium edge.")

            st.caption(f"Strike zones = price ± Z-Score std-dev, rounded to the nearest {step}-pt {index_name} strike interval. Computed estimates, not live quoted strikes/expiries.")

            st.divider()
            if st.button(f"🔔 Send Telegram Alert for {index_name}", key=f"options_alert_btn_{ticker}_{period}"):
                strikes_message = "\n".join(l.replace("**", "") for l in strike_lines) if strike_lines else "No strike zone suggested."
                message = (
                    f"📉 **OPTIONS & FUTURES SETUP** 📉\n\n"
                    f"🎯 Index: {index_name} ({period_label})\n"
                    f"💰 Price: ₹{current_price:.2f}\n"
                    f"📊 Realized Vol: {current_vol:.1f}% ({vol_regime}, {vol_percentile:.0f}th pct)\n"
                    f"📈 Trend: {trend_label}\n"
                    f"📐 Z-Score: {z_score:.2f}\n"
                    f"🧠 Suggested Setup: {strategy}\n"
                    f"{strikes_message}\n\n"
                    f"{rationale}"
                )
                if send_telegram_message(message):
                    st.success("Telegram alert sent.")

    nifty_col, banknifty_col = st.columns(2)
    render_index_analysis(nifty_col, "Nifty 50", index_instruments["Nifty 50"])
    render_index_analysis(banknifty_col, "Bank Nifty", index_instruments["Bank Nifty"])
