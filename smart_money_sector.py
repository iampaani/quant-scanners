import streamlit as st
import yfinance as yf
import pandas as pd
import ta

st.set_page_config(page_title="Smart Money Sector Scanner", layout="wide")
st.title("🎯 Top-Down Smart Money Scanner (Pro Edition)")
st.write("Tracking institutional accumulation (OBV) across 100+ market heavyweights.")

# --- SECTOR BASKETS (Expanded to 15+ Stocks) ---
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

# --- UI: SECTOR SELECTION ---
selected_sector = st.selectbox("Select Sector or Cap Size to Scan:", list(sectors.keys()))
st.divider()

# --- QUANTITATIVE ENGINE ---
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
        obv_sma = obv.rolling(window=20).mean() # 20-day average of institutional volume
        
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
    # Lock the stock name to the left and display as a clean static table
    st.table(df_results.set_index('Stock'))
    
    # --- TRADING LOGIC RULES ---
    st.markdown("""
    ### 🧠 How to Trade This Data:
    1. **The Sniper Setup:** Only buy a stock showing **🟢 Accumulation** and a **↗️ Bullish** trend IF the overall Macro Segment Health is also showing **CAPITAL INFLOW**. 
    2. **The Trap:** If a stock is showing a Bullish trend, but the Smart Money status is **🔴 Distribution**, retail traders are buying the breakout while institutions are quietly dumping shares. Avoid it.
    """)
else:
    st.error("Market data currently unavailable.")