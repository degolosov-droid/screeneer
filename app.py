# Momentum Scanner - Полный скрининг US акций (без ETF)
# По стратегии Кристиана Кэлломэги

import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

# Настройки страницы
st.set_page_config(
    page_title="Momentum Scanner",
    page_icon="📊",
    layout="wide"
)

# CSS
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    div[data-testid="stMetric"] {
        background: white;
        padding: 15px;
        border-radius: 10px;
    }
    .stock-card {
        background: white;
        padding: 15px;
        margin: 10px 0;
        border-radius: 10px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .positive { color: #00c853; }
    .negative { color: #ff1744; }
    .update-time {
        background: rgba(255,255,255,0.9);
        padding: 10px;
        border-radius: 5px;
        text-align: center;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# === ПОЛНЫЙ СПИСОК US АКЦИЙ (только акции, без ETF) ===
# Около 800+ основных US акций

ALL_TICKERS = [
    # Tech - Large Cap
    "AAPL", "MSFT", "AMZN", "NVDA", "GOOGL", "GOOG", "META", "TSLA", "AMD", "INTC",
    "QCOM", "AVGO", "TXN", "AMAT", "MU", "MRVL", "PYPL", "NFLX", "ADBE", "CRM",
    "ORCL", "CSCO", "IBM", "NOW", "SNOW", "PANW", "CRWD", "ZS", "NET", "DDOG",
    "INTU", "ADI", "MCHP", "TXN", "AMAT", "LRCX", "KLAC", "SNPS", "CDNS", "ANSS",
    "SNOW", "TEAM", "WDAY", "OKTA", "ZM", "TWLO", "SPLK", "VEEV", "TTD", "ROKU",
    "PINS", "SNAP", "DOCU", "SQ", "SHOP", "PATH", "UBER", "DASH", "ABNB", "SPOT",
    "COIN", "MSTR", "RBLX", "U", "PLTR", "GME", "AMC", "BB", "NOK", "SPCE",
    "DKNG", "MGM", "WYNN", "LVS", "MAR", "HLT", "RCL", "CCL", "NCLH", "AAL",
    "UAL", "DAL", "ALK", "LUV", "SAVE", "JBLU", "HA", "ASTS", "ASTR",
    
    # Finance
    "JPM", "BAC", "WFC", "GS", "MS", "C", "BLK", "AXP", "SCHW", "USB",
    "PNC", "TFC", "COF", "DFS", "MET", "PRU", "AFL", "L", "TRV", "CB",
    "SPGI", "MCO", "ICE", "CME", "AON", "CI", "HUM", "ANTM", "UNH", "ELV",
    "SYF", "ALL", "TRV", "PGR", "CINF", "AFL", "AIG", "MET", "PRU", "LNC",
    "MMC", "WLTW", "AON", "MAR", "BRO", "FNF", "JHG", "BEN", "TROW", "AMP",
    "OI", "BALL", "IPG", "NTRS", "STT", "BSBR", "BXP", "SLG", "HIW", "ARE",
    
    # Healthcare
    "UNH", "JNJ", "PFE", "MRK", "ABBV", "LLY", "TMO", "ABT", "DHR", "AMGN",
    "GILD", "BIIB", "REGN", "VRTX", "ISRG", "MDT", "SYK", "EW", "ZTS", "BMY",
    "MRNA", "ALGN", "IDXX", "DXCM", "ALXN", "INCY", "MRNA", "ILMN", "A", "PKI",
    "WAT", "DOV", "FTV", "AME", "ITW", "ROK", "PH", "CMI", "IR", "ETN",
    "MNST", "KMB", "GIS", "K", "HSY", "STZ", "LW", "CAG", "MDLZ", "KHC",
    
    # Consumer - Discretionary
    "PG", "KO", "PEP", "COST", "WMT", "HD", "MCD", "NKE", "SBUX", "TGT",
    "LOW", "EL", "CL", "MDLZ", "KMB", "DG", "DLTR", "ORLY", "AZO", "ULTA",
    "ROST", "TJX", "BBY", "DLTR", "YUM", "CMG", "QSR", "DPZ", "MCD", "YUMC",
    "DRI", "TXRH", "BJ", "BBWI", "CHWY", "W", "ETSY", "WLM", "APTV", "BWA",
    
    # Consumer - Staples
    "PG", "KO", "PEP", "COST", "WMT", "MDLZ", "KMB", "GIS", "K", "HSY",
    "STZ", "LW", "CAG", "MDLZ", "KHC", "HSY", "K", "GIS", "CAG", "SYY",
    
    # Energy
    "XOM", "CVX", "COP", "SLB", "EOG", "MPC", "PSX", "VLO", "OXY", "HAL",
    "DVN", "HES", "FANG", "PXD", "APA", "BKR", "CHRW", "JBHT", "SWN", "COG",
    "KMI", "WMB", "OKE", "TRGP", "LNG", "DLNG", "GLNG", "COG", "NFX", "RRC",
    "EQT", "AR", "CNX", "MOS", "FMC", "NUE", "STLD", "X", "AA", "CENX",
    
    # Industrial
    "CAT", "BA", "GE", "RTX", "HON", "UPS", "FDX", "DE", "MMM", "LMT",
    "NOC", "GD", "ITW", "EMR", "ETN", "PH", "ROK", "CMI", "AME", "IR",
    "MAS", "FDX", "JBHT", "CARR", "OTIS", "FAST", "PCAR", "ODFL", "SAIA",
    "SWK", "SNA", "ROK", "ITW", "EMR", "PH", "CMI", "AME", "DOV", "FTV",
    
    # Materials
    "LIN", "APD", "ECL", "SHW", "FCX", "NEM", "AU", "FMC", "NUE", "VMC",
    "MLM", "DOW", "DD", "LYB", "PPG", "ALB", "SCCO", "AA", "CENX", "MT",
    "NUE", "STLD", "RS", "VMC", "MLM", "DOW", "DD", "LYB", "PPG", "ALB",
    
    # Real Estate
    "PLD", "AMT", "EQIX", "SPG", "CCI", "PSA", "O", "WELL", "DLR", "AVB",
    "EQR", "VTR", "WY", "ARE", "SLG", "KIM", "UBA", "FRT", "ESS", "MAA",
    "BXP", "SLG", "KIM", "VTR", "WY", "ARE", "O", "SPG", "PLD", "AMT",
    
    # Telecom
    "VZ", "T", "TMUS", "CMCSA", "DIS", "WBD", "PARA", "FOX", "EA", "ATVI",
    "TTWO", "NWSA", "DISCA", "DISCK", "IPG", "CHTR", "NFLX", "WBD", "PARA",
    
    # Utilities
    "NEE", "DUK", "SO", "D", "AEP", "SRE", "XEL", "ED", "WEC", "FE",
    "EXC", "PEG", "DTE", "AWK", "AEE", "WPO", "AES", "BKH", "EDE", "EGD",
    
    # Additional popular stocks
    "A", "AAL", "AAP", "AAPL", "ABBV", "ABC", "ABMD", "ABT", "ACGL", "ACN",
    "ADBE", "ADI", "ADM", "ADP", "ADSK", "AEE", "AEP", "AES", "AFL", "AIG",
    "AIV", "AIZ", "AJG", "AKAM", "ALB", "ALGN", "ALK", "ALL", "ALLE", "AMAT",
    "AMCR", "AMD", "AME", "AMGN", "AMP", "AMT", "AMZN", "ANET", "ANSS", "ANTM",
    "AON", "AOS", "APA", "APD", "APH", "APTV", "ARE", "ARNA", "ARW", "ASML",
    "ATVI", "AVB", "AVGO", "AVY", "AWK", "AXP", "AZO", "BA", "BABA", "BAC",
    "BALL", "BAX", "BB", "BBWI", "BBY", "BDX", "BEN", "BIIB", "BK", "BKNG",
    "BKR", "BLK", "BMY", "BR", "BRK.B", "BSX", "BTU", "BWA", "BXP", "C",
    "CAG", "CAH", "CARR", "CAT", "CB", "CBD", "CBRE", "CCI", "CDNS", "CE",
    "CELG", "CERN", "CF", "CFG", "CHD", "CHRW", "CHTR", "CI", "CINF", "CL",
    "CLX", "CMA", "CMCSA", "CME", "CMG", "CMI", "CMS", "CNP", "COF", "COG",
    "COO", "COST", "COTY", "CPB", "CPRI", "CPT", "CRL", "CRM", "CSCO", "CSX",
    "CTAS", "CTSH", "CTVA", "CVS", "CVX", "CXO", "D", "DAL", "DASH", "DBX",
    "DD", "DE", "DFS", "DG", "DGX", "DHI", "DHR", "DIS", "DISCA", "DISH",
    "DLR", "DOV", "DRI", "DTE", "DUK", "DVA", "DVN", "DXC", "DXCM", "EA",
    "EBAY", "ECL", "ED", "EDU", "EIX", "EL", "ELAN", "ELV", "EMN", "EMR",
    "ENPH", "EOG", "EPAM", "EQIX", "EQR", "ES", "ETN", "ETR", "EVRG", "EW",
    "EXC", "EXPD", "EXPE", "EXR", "F", "FANG", "FAST", "FB", "FCX", "FDX",
    "FE", "FFIV", "FIS", "FISV", "FITB", "FLT", "FMC", "FRC", "FRT", "FSLR",
    "FTNT", "FTV", "GD", "GE", "GILD", "GIS", "GLD", "GLW", "GM", "GNRC",
    "GOOG", "GOOGL", "GPC", "GPN", "GPS", "GRMN", "GS", "GWW", "HAL", "HAS",
    "HBAN", "HCA", "HD", "HES", "HIG", "HII", "HLT", "HOG", "HOLX", "HON",
    "HPQ", "HRL", "HSIC", "HSY", "HUM", "HWM", "IBM", "ICE", "IDXX", "IEX",
    "IFF", "ILMN", "INCY", "INFO", "INTC", "INTU", "INVH", "IONS", "IPG", "IQV",
    "IR", "IRM", "ISRG", "IT", "ITW", "IVZ", "J", "JBHT", "JCI", "JKHY", "JNJ",
    "JPM", "K", "KDP", "KEY", "KHC", "KIM", "KLAC", "KMB", "KMI", "KO", "KOF",
    "KR", "L", "LCID", "LDOS", "LEN", "LH", "LHX", "LIN", "LKQ", "LLY", "LMT",
    "LNC", "LNT", "LOW", "LRCX", "LULU", "LUV", "LW", "LYB", "LYV", "M", "MA",
    "MAA", "MAR", "MAS", "MCD", "MCHP", "MCK", "MCO", "MDLZ", "MDT", "MELI",
    "MET", "META", "MGM", "MHK", "MKC", "MKTX", "MLM", "MMC", "MMM", "MO",
    "MOH", "MOS", "MPC", "MRK", "MRNA", "MS", "MSCI", "MTCH", "MTD", "MU",
    "NDAQ", "NEE", "NEM", "NFLX", "NIO", "NKE", "NLSN", "NOC", "NOV", "NOW",
    "NRG", "NSC", "NTAP", "NTES", "NTRS", "NUE", "NVR", "NWS", "NXP", "NYCB",
    "O", "ODFL", "OIH", "OKE", "OKTA", "OMC", "ON", "ORCL", "ORLY", "OXY",
    "PANW", "PARA", "PAYC", "PBCT", "PBI", "PCAR", "PCG", "PEAK", "PEG", "PENN",
    "PEP", "PFE", "PFG", "PGR", "PG", "PH", "PHM", "PKG", "PKI", "PLD", "PLTR",
    "PM", "PNC", "PNR", "PNW", "POOL", "PPG", "PPL", "PRU", "PSX", "PTC",
    "PVH", "PWR", "PXD", "QCOM", "R", "RAI", "RBA", "RCL", "RE", "REG", "REGN",
    "RHI", "RIVN", "RJF", "RL", "RMD", "ROK", "ROPE", "ROP", "ROST", "RSG",
    "RTX", "SBUX", "SCHW", "SIRI", "SIVB", "SLB", "SLG", "SNA", "SNAP", "SNPS",
    "SO", "SPG", "SPGI", "SRE", "STE", "STT", "STZ", "SWK", "SWKS", "SYF", "SYY",
    "T", "TAP", "TCOM", "TDG", "TEL", "TER", "TFC", "TGT", "TJX", "TMO",
    "TMUS", "TROW", "TRV", "TSCO", "TSLA", "TSN", "TT", "TTWO", "TWLO", "TXN",
    "TXT", "TYL", "U", "UBER", "UDR", "UHS", "ULTA", "UNH", "UNP", "UPS",
    "URBN", "USB", "V", "VFC", "VICI", "VLO", "VMC", "VMW", "VZ", "WAB", "WAT",
    "WBA", "WBD", "WCG", "WDC", "WEC", "WELL", "WFC", "WHR", "WLTW", "WM",
    "WMB", "WMT", "WPO", "WRB", "WSM", "WST", "WTW", "WY", "WYNN", "X", "XEL",
    "XOM", "XRAY", "XYL", "YUM", "YUMC", "ZBH", "ZION", "ZM", "ZS"
]

# Удаляем дубликаты
ALL_TICKERS = list(set(ALL_TICKERS))
ALL_TICKERS.sort()

PERIODS = {
    "1 неделя": ("5d", "1W"),
    "1 месяц": ("1mo", "1M"),
    "3 месяца": ("3mo", "3M"),
    "6 месяцев": ("6mo", "6M")
}

# === ФУНКЦИИ С КЭШИРОВАНИЕМ ===

@st.cache_data(ttl=86400, show_spinner=False)
def fetch_and_filter_stocks(tickers, min_price, min_market_cap, min_volume, min_adr):
    """Загружает и фильтрует все акции"""
    filtered = []
    total = len(tickers)
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, ticker in enumerate(tickers):
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            hist = stock.history(period="1mo")
            
            # Проверка цены
            price = info.get('currentPrice') or info.get('regularMarketPrice')
            if not price or price < min_price:
                continue
            
            # Проверка капитализации
            market_cap = info.get('marketCap')
            if not market_cap or market_cap < min_market_cap * 1_000_000:
                continue
            
            # Проверка объёма
            avg_volume = info.get('averageVolume') or info.get('averageVolume10days')
            if not avg_volume or avg_volume < min_volume * 1000:
                continue
            
            # Проверка ADR (Average Daily Range)
            if hist.empty or len(hist) < 5:
                continue
            
            daily_ranges = []
            for j in range(len(hist)):
                day_high = hist['High'].iloc[j]
                day_low = hist['Low'].iloc[j]
                day_open = hist['Open'].iloc[j]
                if day_open > 0:
                    daily_range = ((day_high - day_low) / day_open) * 100
                    daily_ranges.append(daily_range)
            
            if not daily_ranges:
                continue
            
            adr = sum(daily_ranges) / len(daily_ranges)
            
            if adr < min_adr:
                continue
            
            filtered.append({
                'ticker': ticker,
                'price': price,
                'market_cap': market_cap,
                'volume': avg_volume,
                'adr': round(adr, 2)
            })
            
        except Exception:
            continue
        
        if i % 50 == 0:
            progress_bar.progress(i / total)
            status_text.text(f"Обработано {i}/{total} акций... Найдено: {len(filtered)}")
    
    progress_bar.progress(1.0)
    status_text.text(f"Готово! Найдено {len(filtered)} акций")
    
    return filtered


@st.cache_data(ttl=3600, show_spinner=False)
def calculate_momentum_for_stocks(filtered_tickers, period_key):
    """Рассчитывает моментум для отфильтрованных акций"""
    momentum_data = []
    progress_bar = st.progress(0)
    status_text = st.empty()
    total = len(filtered_tickers)
    
    for i, item in enumerate(filtered_tickers):
        ticker = item['ticker']
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period=period_key)
            
            if hist.empty or len(hist) < 2:
                continue
            
            price = hist['Close'].iloc[-1]
            
            past_idx = 0 if len(hist) <= 5 else len(hist) - 5
            past_price = hist['Close'].iloc[past_idx]
            momentum = ((price / past_price) - 1) * 100 if past_price > 0 else 0
            
            if len(hist) >= 2:
                prev = hist['Close'].iloc[-2]
                day_chg = ((price / prev) - 1) * 100
            else:
                day_chg = 0
            
            momentum_data.append({
                'Ticker': ticker,
                'Price': price,
                'Momentum %': momentum,
                'Day %': day_chg,
                'Volume': item['volume']
            })
            
        except Exception:
            continue
        
        if i % 20 == 0:
            progress_bar.progress(i / total)
            status_text.text(f"Расчёт моментума: {i}/{total}")
    
    progress_bar.progress(1.0)
    status_text.text("Расчёт завершён!")
    
    return momentum_data


# === ИНТЕРФЕЙС ===

st.title("📊 Momentum Scanner")
st.markdown("### Стратегия Кэлломэги - Полный скрининг US акций")

# Боковая панель с фильтрами
with st.sidebar:
    st.header("⚙️ Первичные фильтры")
    
    min_price = st.number_input("Мин. цена ($)", value=2.0, min_value=0.1, step=0.5)
    min_market_cap = st.number_input("Мин. капитализация ($M)", value=500.0, min_value=10.0, step=50.0)
    min_volume = st.number_input("Мин. объём (тыс.)", value=1000.0, min_value=100.0, step=100.0)
    min_adr = st.slider("Мин. ADR (%)", 1, 20, 5)
    
    st.markdown("---")
    st.header("📊 Параметры скрининга")
    top_percent = st.slider("Топ % акций", 1, 20, 5)
    
    st.markdown("---")
    st.markdown(f"**Всего тикеров:** {len(ALL_TICKERS)}")
    
    st.markdown("---")
    st.info("💾 Данные кэшируются на 24 часа")
    
    if st.button("🔄 Очистить кэш и обновить"):
        fetch_and_filter_stocks.clear()
        calculate_momentum_for_stocks.clear()
        st.rerun()

# Выбор периода
col1, col2 = st.columns([3, 1])
with col1:
    period_name = st.selectbox("Выберите период моментума:", list(PERIODS.keys()))

period_key, period_label = PERIODS[period_name]

st.markdown("---")

# === ЗАГРУЗКА И ФИЛЬТРАЦИЯ ===

st.info(f"📊 Сканируем {len(ALL_TICKERS)} акций US рынка...")

with st.spinner("Фильтрация акций по критериям..."):
    filtered = fetch_and_filter_stocks(
        ALL_TICKERS, min_price, min_market_cap, min_volume, min_adr
    )

st.success(f"✅ Фильтр прошли: {len(filtered)} акций")

# Показать список
if filtered:
    with st.expander(f"📋 Список акций после фильтра ({len(filtered)})"):
        df_filtered = pd.DataFrame(filtered)
        df_filtered['Market Cap ($M)'] = df_filtered['market_cap'] / 1_000_000
        df_filtered['Volume (K)'] = df_filtered['volume'] / 1000
        df_filtered = df_filtered.sort_values('Market Cap ($M)', ascending=False)
        st.dataframe(
            df_filtered[['ticker', 'price', 'Market Cap ($M)', 'Volume (K)', 'adr']],
            use_container_width=True
        )

# === РАСЧЁТ МОМЕНТУМА ===

st.markdown("---")
st.markdown(f"### 📈 Топ {top_percent}% моментум ({period_name})")

if filtered:
    with st.spinner("Расчёт моментума..."):
        momentum_data = calculate_momentum_for_stocks(filtered, period_key)
    
    if momentum_data:
        df = pd.DataFrame(momentum_data)
        df = df.sort_values('Momentum %', ascending=False)
        
        top_n = max(3, int(len(df) * top_percent / 100))
        df_top = df.head(top_n)
        
        # Метрики
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Проверено", len(ALL_TICKERS))
        c2.metric("Прошли фильтр", len(filtered))
        c3.metric("Топ акций", top_n)
        c4.metric("Ср. моментум", f"{df_top['Momentum %'].mean():.1f}%")
        
        st.markdown("---")
        
        # Результаты
        for idx, row in df_top.iterrows():
            m_color = "green" if row['Momentum %'] > 0 else "red"
            d_color = "green" if row['Day %'] > 0 else "red"
            
            st.markdown(f"""
            <div class="stock-card">
                <div>
                    <b style="font-size:20px;">{row['Ticker']}</b>
                </div>
                <div style="text-align:right;">
                    <div style="font-size:20px;">${row['Price']:.2f}</div>
                    <div class="{m_color}" style="font-weight:bold;">Моментум: {'+' if row['Momentum %']>0 else ''}{row['Momentum %']:.1f}%</div>
                    <div class="{d_color}">День: {'+' if row['Day %']>0 else ''}{row['Day %']:.1f}%</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        now = datetime.now()
        st.markdown(f"""
        <div class="update-time">
            <b>Данные обновлены:</b> {now.strftime('%Y-%m-%d %H:%M:%S')}<br>
            <small>Кэш действителен до: {(now + timedelta(hours=24)).strftime('%Y-%m-%d %H:%M:%S')}</small>
        </div>
        """, unsafe_allow_html=True)
        
        csv = df_top.to_csv(index=False)
        st.download_button("📥 Скачать CSV", csv, "momentum_stocks.csv", use_container_width=True)
    else:
        st.warning("Не удалось рассчитать моментум")
else:
    st.warning("Ни одна акция не прошла фильтр")
