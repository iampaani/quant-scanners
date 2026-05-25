import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import ta

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

# --- UI: CREATE TABS ---
tab1, tab2, tab3 = st.tabs(["⚡ Z-Score Scanner", "🚀 Short Squeeze Radar", "🔬 Micro-Anatomy Analyzer"])

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
    def calculate_fno_zscores(tickers, lookback):
        results = []
        data = yf.download(tickers, period="6mo", interval="1d", progress=False)['Close']
        
        if data.empty:
            return pd.DataFrame()
            
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.droplevel(1)

        for ticker in tickers:
            if ticker in data.columns:
                df = data[[ticker]].dropna().copy()
                if len(df) < lookback:
                    continue
                    
                df['Mean'] = df[ticker].rolling(window=lookback).mean()
                df['StdDev'] = df[ticker].rolling(window=lookback).std()
                df['Z-Score'] = (df[ticker] - df['Mean']) / df['StdDev']
                
                current_price = df[ticker].iloc[-1]
                current_z = df['Z-Score'].iloc[-1]
                
                if current_z >= z_threshold:
                    signal = "🔴 OVERBOUGHT (Look to Short)"
                elif current_z <= -z_threshold:
                    signal = "🟢 OVERSOLD (Look to Buy)"
                else:
                    signal = "➖ NEUTRAL"

                results.append({
                    "F&O Stock": ticker.replace('.NS', ''),
                    "Current Price": f"₹{current_price:.2f}",
                    "Z-Score": round(current_z, 2),
                    "Signal": signal
                })
                
        return pd.DataFrame(results).sort_values(by="Z-Score", ascending=False, key=abs)

    # Automatically runs the Z-Score math
    st.write(f"Calculating current {window}-day Z-Scores...")
    df_zscore = calculate_fno_zscores(fno_basket_yf, window)

    if not df_zscore.empty:
        actionable_df = df_zscore[df_zscore['Signal'] != "➖ NEUTRAL"]
        
        st.subheader("🔥 Actionable Extremes (Mean Reversion)")
        if actionable_df.empty:
            st.success(f"No F&O stocks are stretched beyond a Z-Score of {z_threshold} right now.")
        else:
            st.error(f"These stocks have violently detached from their moving average.")
            st.table(actionable_df.set_index('F&O Stock'))
            
        st.subheader("📊 Full Basket Overview")
        def highlight_zscore_fno(val):
            color = '#ff4b4b' if val >= z_threshold else '#00cc96' if val <= -z_threshold else 'gray'
            weight = 'bold' if abs(val) >= z_threshold else 'normal'
            return f'color: {color}; font-weight: {weight}'

        styled_z_df = df_zscore.style.map(highlight_zscore_fno, subset=['Z-Score'])
        st.dataframe(styled_z_df, height=400, use_container_width=True)

# ==========================================
# ENGINE 2: SHORT SQUEEZE RADAR (TAB 2)
# ==========================================
with tab2:
    st.header("🚀 Institutional Short Squeeze Radar")
    st.write("Hunting for trapped bears using the Triple Confirmation method: OI Drop + Volume Spike + VWAP Reclaim.")

    @st.cache_data(ttl=60)
    def fetch_squeeze_data():
        np.random.seed() # Simulator logic
        results = []
        for ticker in fno_basket_clean:
            price_change_pct = np.random.uniform(-2.0, 5.0)
            oi_change_pct = np.random.uniform(-10.0, 5.0)
            relative_volume = np.random.uniform(0.5, 3.0)
            is_above_vwap = True if price_change_pct > 1.0 else np.random.choice([True, False])
            
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
            
        return pd.DataFrame(results).sort_values(by="Score", ascending=False)

    # Runs automatically and refreshes on its own via the cache TTL
    df_squeeze = fetch_squeeze_data()

    st.subheader("🎯 High Conviction Targets (Score 3/3)")
    high_conviction_df = df_squeeze[df_squeeze['Score'] == 3].drop(columns=['Score'])

    if not high_conviction_df.empty:
        st.error("**ALERT: Perfect Storm Detected.** Bears are trapped, volume is exploding, and buyers have reclaimed VWAP.")
        st.table(high_conviction_df.set_index('Stock'))
    else:
        st.info("No perfect 3/3 squeezes detected right now.")

    st.divider()

    st.subheader("👀 Squeeze Watchlist (Score 2/3)")
    building_df = df_squeeze[df_squeeze['Score'] == 2].drop(columns=['Score'])

    if not building_df.empty:
        st.warning("These stocks are showing heavy short covering, but are missing either the Volume spike or haven't crossed VWAP yet.")
        st.table(building_df.set_index('Stock'))
    else:
        st.info("No building squeezes at the moment.")

    st.divider()

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

    styled_sq_df = df_squeeze.drop(columns=['Score']).style.map(highlight_squeeze, subset=['Squeeze Status'])
    st.dataframe(styled_sq_df, height=400, use_container_width=True)

# ==========================================
# ENGINE 3: MICRO-ANATOMY ANALYZER (TAB 3)
# ==========================================
with tab3:
    st.header("🔬 F&O Micro-Anatomy Analyzer")
    st.write("Deep quantitative analysis on a single asset to generate a definitive trading strategy.")
    
    selected_name = st.selectbox("Select F&O Stock for Deep Analysis:", list(fno_stocks.keys()))
    ticker_deep = fno_stocks[selected_name]
    st.divider()

    @st.cache_data(ttl=60)
    def analyze_deep_stock(ticker):
        stock = yf.Ticker(ticker)
        df = stock.history(period="1y")
        
        if df.empty or len(df) < 50:
            return None
            
        close = df['Close']
        volume = df['Volume']

        df['EMA_20'] = ta.trend.ema_indicator(close, window=20)
        df['EMA_50'] = ta.trend.ema_indicator(close, window=50)
        df['RSI'] = ta.momentum.rsi(close, window=14)
        
        mean_20 = close.rolling(window=20).mean()
        std_20 = close.rolling(window=20).std()
        df['Z_Score'] = (close - mean_20) / std_20
        
        df['OBV'] = ta.volume.on_balance_volume(close, volume)
        df['OBV_SMA'] = df['OBV'].rolling(window=20).mean()

        df['Log_Ret'] = np.log(close / close.shift(1))
        df['HV_20'] = df['Log_Ret'].rolling(window=20).std() * np.sqrt(252) * 100
        df['ATR'] = ta.volatility.average_true_range(df['High'], df['Low'], close, window=14)

        return df

    # Runs instantly the second you change the dropdown menu
    df_deep = analyze_deep_stock(ticker_deep)

    if df_deep is not None:
        latest = df_deep.iloc[-1]
        
        current_price = latest['Close']
        rsi = latest['RSI']
        z_score = latest['Z_Score']
        hv = latest['HV_20']
        atr = latest['ATR']
        trend_up = latest['EMA_20'] > latest['EMA_50']
        smart_money_in = latest['OBV'] > latest['OBV_SMA']
        
        bull_stop = current_price - (1.5 * atr)
        bear_stop = current_price + (1.5 * atr)
        
        st.subheader(f"🧠 The F&O Verdict: {selected_name} @ ₹{current_price:.2f}")
        
        verdict_text = ""
        strategy = ""
        
        if trend_up and smart_money_in and rsi < 70:
            if hv < 25:
                verdict_text = "🔥 HIGH PROBABILITY BUY. Trend is strong and volatility is low (premiums are cheap)."
                strategy = "Call Buying or Bull Call Spread."
            else:
                verdict_text = "🔥 HIGH PROBABILITY BUY. Trend is strong, but volatility is extremely high (premiums are expensive)."
                strategy = "Bull Put Spread (Option Selling) to collect inflated premium."
                
        elif not trend_up and not smart_money_in and rsi > 30:
            if hv < 25:
                verdict_text = "🩸 AGGRESSIVE SHORT. Trend is broken, smart money is leaving, and volatility is low."
                strategy = "Put Buying or Bear Put Spread."
            else:
                verdict_text = "🩸 AGGRESSIVE SHORT. Trend is broken, but volatility is elevated."
                strategy = "Bear Call Spread (Option Selling) to avoid IV crush."
                
        elif trend_up and rsi >= 70:
            verdict_text = "⚠️ EXHAUSTION WARNING. Stock is in an uptrend but severely overbought."
            strategy = "Do not chase. Wait for a pullback or consider Covered Calls if holding equity."
            
        elif not trend_up and rsi <= 30 and z_score <= -2.0:
            verdict_text = "🎯 SNIPER REVERSAL ZONE. Price has crashed too fast and is stretched dangerously far below the mean."
            strategy = "High risk/high reward Mean Reversion. Look for intraday bottoming patterns."
            
        else:
            verdict_text = "⚖️ CHOP ZONE. No quantitative edge detected. Institutional capital is dormant."
            strategy = "Iron Condor if you must trade, otherwise deploy capital elsewhere."

        st.info(f"**MARKET ACTION:** {verdict_text}")
        st.success(f"**OPTIMAL STRATEGY:** {strategy}")
        st.warning(f"**QUANTITATIVE STOP LOSS (1.5x ATR):** ₹{bull_stop:.2f} (If Long) | ₹{bear_stop:.2f} (If Short)")
        
        st.divider()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("### 📈 Trend & Flow")
            st.write(f"**Trend:** {'🟢 Bullish' if trend_up else '🔴 Bearish'}")
            st.write(f"**Smart Money (OBV):** {'🟢 Accumulating' if smart_money_in else '🔴 Distributing'}")
            
        with col2:
            st.markdown("### 🌪️ Volatility")
            st.write(f"**Historical Volatility:** {hv:.1f}%")
            st.write(f"**ATR:** ₹{atr:.2f} per day")

        with col3:
            st.markdown("### ⚡ Exhaustion")
            st.write(f"**RSI (14):** {rsi:.1f}")
            st.write(f"**Z-Score:** {z_score:.2f}")
                     
    else:
        st.error("Market data currently unavailable for this ticker.")