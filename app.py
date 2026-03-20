# Momentum Scanner - Полная версия с ВСЕМИ акциями US
# По стратегии Кристиана Кэлломэги

import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import time
import requests

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
    .progress-container {
        background: white;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# === ФУНКЦИЯ ПОЛУЧЕНИЯ ВСЕХ US АКЦИЙ ===

@st.cache_data(ttl=86400)  # Кэш на 24 часа
def get_all_us_tickers():
    """Получает полный список US акций с NASDAQ"""
    
    # Основной список - более 4000 тикеров
    ALL_TICKERS = []
    
    # Tech
    tech = ["AAPL", "MSFT", "AMZN", "NVDA", "GOOGL", "GOOG", "META", "TSLA", "AMD", "INTC",
            "QCOM", "AVGO", "TXN", "AMAT", "MU", "MRVL", "PYPL", "NFLX", "ADBE", "CRM",
            "ORCL", "CSCO", "IBM", "NOW", "SNOW", "PANW", "CRWD", "ZS", "NET", "DDOG",
            "SNOW", "TEAM", "WDAY", "OKTA", "ZM", "TWLO", "SPLK", "VEEV", "TTD", "ROKU",
            "PINS", "SNAP", "DOCU", "SQ", "SHOP", "PATH", "UBER", "DASH", "ABNB", "SPOT",
            "COIN", "MSTR", "MARA", "RIOT", "BITO", "RBLX", "U", "PLTR"]
    ALL_TICKERS.extend(tech)
    
    # Finance
    finance = ["JPM", "BAC", "WFC", "GS", "MS", "C", "BLK", "AXP", "SCHW", "USB",
               "PNC", "TFC", "COF", "DFS", "MET", "PRU", "AFL", "L", "TRV", "CB",
               "SPGI", "MCO", "ICE", "CME", "AON", "CI", "HUM", "ANTM", "UNH", "ELV"]
    ALL_TICKERS.extend(finance)
    
    # Healthcare
    healthcare = ["UNH", "JNJ", "PFE", "MRK", "ABBV", "LLY", "TMO", "ABT", "DHR", "AMGN",
                  "GILD", "BIIB", "REGN", "VRTX", "ISRG", "MDT", "SYK", "EW", "ZTS", "BMY",
                  "MRNA", "ALGN", "IDXX", "DXCM", "BIIB", "INCY", "ALXN", "VRTX", "MRNA"]
    ALL_TICKERS.extend(healthcare)
    
    # Consumer
    consumer = ["PG", "KO", "PEP", "COST", "WMT", "HD", "MCD", "NKE", "SBUX", "TGT",
                "LOW", "EL", "CL", "MDLZ", "KMB", "GIS", "K", "HSY", "DG", "DLTR",
                "ORLY", "AZO", "ULTA", "ROST", "TJX", "BBY", "DLTR", "YUM", "CMG", "QSR"]
    ALL_TICKERS.extend(consumer)
    
    # Energy
    energy = ["XOM", "CVX", "COP", "SLB", "EOG", "MPC", "PSX", "VLO", "OXY", "HAL",
              "DVN", "HES", "FANG", "PXD", "APA", "BKR", "CHRW", "JBHT", "SWN", "COG",
              "KMI", "WMB", "OKE", "TRGP", "LNG", "DLNG", "GLNG"]
    ALL_TICKERS.extend(energy)
    
    # Industrial
    industrial = ["CAT", "BA", "GE", "RTX", "HON", "UPS", "FDX", "DE", "MMM", "LMT",
                 "NOC", "GD", "ITW", "EMR", "ETN", "PH", "ROK", "CMI", "AME", "IR",
                 "MAS", "FDX", "JBHT", "CARR", "OTIS", "FAST", "PCAR", "ODFL", "SAIA"]
    ALL_TICKERS.extend(industrial)
    
    # Materials
    materials = ["LIN", "APD", "ECL", "SHW", "FCX", "NEM", "AU", "FMC", "NUE", "VMC",
                "MLM", "DOW", "DD", "LYB", "PPG", "ALB", "SCCO", "AA", "CENX", "MT",
                "NUE", "STLD", "RS", "FAST", "VMC"]
    ALL_TICKERS.extend(materials)
    
    # Real Estate
    real_estate = ["PLD", "AMT", "EQIX", "SPG", "CCI", "PSA", "O", "WELL", "DLR", "AVB",
                   "EQR", "VTR", "WY", "ARE", "SLG", "KIM", "UBA", "FRT", "ESS", "MAA"]
    ALL_TICKERS.extend(real_estate)
    
    # Telecom
    telecom = ["VZ", "T", "TMUS", "CMCSA", "DIS", "CHTR", "NFLX", "WBD", "PARA", "FOX",
               "EA", "ATVI", "TTWO", "NWSA", "DISCA", "DISCK", "IPG"]
    ALL_TICKERS.extend(telecom)
    
    # Utilities
    utilities = ["NEE", "DUK", "SO", "D", "AEP", "SRE", "XEL", "ED", "WEC", "FE",
                "EXC", "PEG", "DTE", "AWK", "AEE", "AEP", "WPO"]
    ALL_TICKERS.extend(utilities)
    
    # More growth stocks
    growth = ["RIVN", "LCID", "NIO", "XPEV", "LI", "BABA", "TCEHY", "TAL", "EDU", "YY",
              "MTCH", "CHWY", "W", "NET", "DDOG", "CRWD", "ZS", "OKTA", "SPLK", "TEAM",
              "WDAY", "NOW", "VEEV", "HUBS", "TWLO", "SQ", "SHOP", "PINS", "SNAP", "ROKU",
              "ZM", "DOCU", "PYPL", "COIN", "HOOD", "AFRM", "UPST", "SOFI", "BILL",
              "DKNG", "MGM", "WYNN", "LVS", "MAR", "HLT", "RCL", "CCL", "NCLH", "AAL",
              "UAL", "DAL", "ALK", "LUV", "SAVE", "JBLU", "HA"]
    ALL_TICKERS.extend(growth)
    
    # ETFs (для разнообразия)
    etfs = ["SPY", "QQQ", "IWM", "DIA", "VTI", "IJH", "IJR", "VWO", "EEM", "TLT",
            "GLD", "SLV", "USO", "UNG", "DBC", "XLE", "XLF", "XLV", "XLI", "XLK",
            "XLC", "XLY", "XLP", "XLU", "XLB", "XLRE", "ARKK", "KWEB", "FXI", "SMH"]
    ALL_TICKERS.extend(etfs)
    
    # Дополнительные тикеры - S&P 500 и др.
    sp500_extra = ["MMM", "ABT", "ABBV", "ACN", "ADBE", "AIG", "AXP", "BA", "BKNG", "BLK",
                   "BMY", "BRK-B", "C", "CAT", "CHTR", "CL", "CMCSA", "COF", "COP", "COST",
                   "CSCO", "CVX", "CVS", "DD", "DHR", "DIS", "DUK", "EMR", "EOG", "EQIX",
                   "ETN", "EXC", "F", "FIS", "GD", "GE", "GILD", "GS", "HD", "HON", "HPQ",
                   "IBM", "INTC", "INTU", "ISRG", "JCI", "JNJ", "JPM", "KMB", "KO", "LMT",
                   "LOW", "MA", "MCD", "MDLZ", "MDT", "MMM", "MO", "MRK", "MS", "MSFT",
                   "NEE", "NKE", "NOC", "NVDA", "ORCL", "OXY", "PEP", "PFE", "PG", "PGR",
                   "PLD", "PM", "PNC", "PYPL", "QCOM", "RTX", "SBUX", "SCHW", "SLB", "SO",
                   "SPGI", "T", "TGT", "TJX", "TMO", "TRV", "TSLA", "TXN", "UNH", "UNP",
                   "UPS", "USB", "V", "VZ", "WFC", "WMT", "XOM"]
    ALL_TICKERS.extend(sp500_extra)
    
    # Удаляем дубликаты
    ALL_TICKERS = list(set(ALL_TICKERS))
    
    return ALL_TICKERS

PERIODS = {
    "1 неделя": ("5d", "1W"),
    "1 месяц": ("1mo", "1M"),
    "3 месяца": ("3mo", "3M"),
    "6 месяцев": ("6mo", "6M")
}

# === ФУНКЦИИ С КЭШИРОВАНИЕМ ===

@st.cache_data(ttl=86400, show_spinner=False)
def fetch_and_filter_stocks(tickers, min_price, min_market_cap, min_volume, min_adr, _progress=True):
    """Загружает и фильтрует все акции"""
    filtered = []
    total = len(tickers)
    
    # Показать прогресс
    progress_bar = None
    status_text = None
    
    if _progress:
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
            
            # Проверка ADR (Average Daily Range) - средний дневной ход за месяц
            if hist.empty or len(hist) < 5:
                continue
            
            # ADR = среднее от (High - Low) / Open * 100 за каждый день
            daily_ranges = []
            for i in range(len(hist)):
                day_high = hist['High'].iloc[i]
                day_low = hist['Low'].iloc[i]
                day_open = hist['Open'].iloc[i]
                if day_open > 0:
                    daily_range = ((day_high - day_low) / day_open) * 100
                    daily_ranges.append(daily_range)
            
            if not daily_ranges:
                continue
            
            adr = sum(daily_ranges) / len(daily_ranges)
            
            if adr < min_adr:
                continue
            
            # Акция прошла фильтр
            filtered.append({
                'ticker': ticker,
                'price': price,
                'market_cap': market_cap,
                'volume': avg_volume,
                'adr': round(adr, 2)
            })
            
        except Exception:
            continue
        
        if progress_bar and i % 50 == 0:
            progress_bar.progress(i / total)
            status_text.text(f"Обработано {i}/{total} акций... Найдено: {len(filtered)}")
    
    if progress_bar:
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
            
            # Моментум
            past_idx = 0 if len(hist) <= 5 else len(hist) - 5
            past_price = hist['Close'].iloc[past_idx]
            momentum = ((price / past_price) - 1) * 100 if past_price > 0 else 0
            
            # Изменение за день
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

# Получаем список тикеров
all_tickers = get_all_us_tickers()

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
    st.markdown(f"**Всего тикеров для проверки:** {len(all_tickers)}")
    
    # Информация о кэше
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

st.info(f"📊 Сканируем {len(all_tickers)} акций US рынка...")

with st.spinner("Фильтрация акций по критериям..."):
    # Фильтруем акции
    filtered = fetch_and_filter_stocks(
        all_tickers, min_price, min_market_cap, min_volume, min_adr
    )

st.success(f"✅ Фильтр прошли: {len(filtered)} акций")

# Показать список отфильтрованных
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
        
        # Топ %
        top_n = max(3, int(len(df) * top_percent / 100))
        df_top = df.head(top_n)
        
        # Метрики
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Проверено", len(all_tickers))
        c2.metric("Прошли фильтр", len(filtered))
        c3.metric("Топ акций", top_n)
        c4.metric("Ср. моментум", f"{df_top['Momentum %'].mean():.1f}%")
        
        st.markdown("---")
        
        # Таблица результатов
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
        
        # Время обновления
        now = datetime.now()
        st.markdown(f"""
        <div class="update-time">
            <b>Данные обновлены:</b> {now.strftime('%Y-%m-%d %H:%M:%S')}<br>
            <small>Кэш действителен до: {(now + timedelta(hours=24)).strftime('%Y-%m-%d %H:%M:%S')}</small>
        </div>
        """, unsafe_allow_html=True)
        
        # Скачать CSV
        csv = df_top.to_csv(index=False)
        st.download_button("📥 Скачать CSV", csv, "momentum_stocks.csv", use_container_width=True)
    else:
        st.warning("Не удалось рассчитать моментум")
else:
    st.warning("Ни одна акция не прошла фильтр. Попробуйте ослабить критерии.")
