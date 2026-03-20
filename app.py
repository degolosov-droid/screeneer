# Momentum Scanner - Версия с динамическими фильтрами
# По стратегии Кристиана Кэлломэги

import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import time

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
</style>
""", unsafe_allow_html=True)

# === РАСШИРЕННЫЙ СПИСОК АКЦИЙ (все основные NYSE + NASDAQ) ===
# Для полного сканирования нужно использовать API тикеров
TICKERS = [
    # Tech
    "AAPL", "MSFT", "AMZN", "NVDA", "GOOGL", "GOOG", "META", "TSLA", "AMD", "INTC",
    "QCOM", "AVGO", "TXN", "AMAT", "MU", "MRVL", "PYPL", "NFLX", "ADBE", "CRM",
    "ORCL", "CSCO", "IBM", "NOW", "SNOW", "PANW", "CRWD", "ZS", "NET", "DDOG",
    # Finance
    "JPM", "BAC", "WFC", "GS", "MS", "C", "BLK", "AXP", "SCHW", "USB",
    "PNC", "TFC", "COF", "DFS", "MET", "PRU", "AFL", "L", "TRV", "CB",
    # Healthcare
    "UNH", "JNJ", "PFE", "MRK", "ABBV", "LLY", "TMO", "ABT", "DHR", "AMGN",
    "GILD", "BIIB", "REGN", "VRTX", "ISRG", "MDT", "SYK", "EW", "ZTS", "BMY",
    # Consumer
    "PG", "KO", "PEP", "COST", "WMT", "HD", "MCD", "NKE", "SBUX", "TGT",
    "LOW", "EL", "CL", "MDLZ", "KMB", "GIS", "K", "HSY", "DG", "DLTR",
    # Energy
    "XOM", "CVX", "COP", "SLB", "EOG", "MPC", "PSX", "VLO", "OXY", "HAL",
    "DVN", "HES", "FANG", "PXD", "APA", "BKR", "CHRW", "JBHT", "SWN", "COG",
    # Industrial
    "CAT", "BA", "GE", "RTX", "HON", "UPS", "FDX", "DE", "MMM", "LMT",
    "NOC", "GD", "ITW", "EMR", "ETN", "PH", "ROK", "CMI", "AME", "IR",
    # Materials
    "LIN", "APD", "ECL", "SHW", "FCX", "NEM", "AU", "FMC", "NUE", "VMC",
    "MLM", "SLB", "DOW", "DD", "LYB", "PPG", "ALB", "SCCO", "AA", "CENX",
    # Real Estate
    "PLD", "AMT", "EQIX", "SPG", "CCI", "PSA", "O", "WELL", "DLR", "AVB",
    # Telecom
    "VZ", "T", "TMUS", "CMCSA", "DIS", "CHTR", "NFLX", "WBD", "PARA", "FOX",
    # Utilities
    "NEE", "DUK", "SO", "D", "AEP", "SRE", "XEL", "ED", "WEC", "FE",
    # Crypto/Fintech
    "COIN", "MSTR", "MARA", "RIOT", "BITO", "BTF", "GBTC", "ETHE", "BITW",
    # Growth/Small Cap
    "PLTR", "SNAP", "PINS", "ROKU", "ZM", "DOCU", "TWLO", "SQ", "SHOP", "DDOG",
    "NET", "CRWD", "ZS", "OKTA", "TEAM", "WDAY", "SPLK", "NOW", "VEEV", "TTD",
    # Additional popular
    "F", "GM", "TM", "HMC", "RACE", "LCID", "RIVN", "NIO", "XPEV", "LI",
    "BABA", "TCEHY", "NKE", "U", "ABNB", "DASH", "GLBE", "COIN", "HOOD", "AFRM",
    "UPST", "SOFI", "BILL", "DKNG", "MGM", "WYNN", "LVS", "MAR", "HLT", "RCL"
]

# Расширенный список для более полного охвата
EXTENDED_TICKERS = TICKERS + [
    "ARKK", "QQQ", "IWM", "SPY", "DIA", "VTI", "IJH", "IJR", "VWO", "EEM",
    "TLT", "GLD", "SLV", "USO", "UNG", "DBC", "XLE", "XLF", "XLV", "XLI",
    "XLK", "XLC", "XLY", "XLP", "XLU", "XLB", "XLRE", "XLC", "KWEB", "FXI"
]

PERIODS = {
    "1 неделя": ("5d", "1W"),
    "1 месяц": ("1mo", "1M"),
    "3 месяца": ("3mo", "3M"),
    "6 месяцев": ("6mo", "6M")
}

# === ФУНКЦИИ ФИЛЬТРАЦИИ ===

def check_filters(ticker, info, hist):
    """Проверяет акцию по первичным фильтрам"""
    try:
        # 1. Цена акции > $2
        price = info.get('currentPrice') or info.get('regularMarketPrice')
        if not price or price < 2:
            return False, "Цена < $2"
        
        # 2. Капитализация > $500M
        market_cap = info.get('marketCap')
        if not market_cap or market_cap < 500_000_000:
            return False, "Кап < $500M"
        
        # 3. Средний объём > 1M
        avg_volume = info.get('averageVolume') or info.get('averageVolume10days')
        if not avg_volume or avg_volume < 1_000_000:
            return False, "Объём < 1M"
        
        # 4. ADR (Average Daily Range) > 5%
        if hist.empty or len(hist) < 2:
            return False, "Нет данных"
        
        high = hist['High']
        low = hist['Low']
        adr = ((high.max() - low.min()) / low.min()) * 100 if low.min() > 0 else 0
        
        if adr < 5:
            return False, f"ADR {adr:.1f}% < 5%"
        
        return True, "OK"
    except Exception as e:
        return False, str(e)


def calculate_momentum(hist, period):
    """Рассчитывает моментум"""
    if hist.empty or len(hist) < 2:
        return 0, 0
    
    price = hist['Close'].iloc[-1]
    
    # Моментум за период
    past_idx = 0 if len(hist) <= 5 else len(hist) - 5
    past_price = hist['Close'].iloc[past_idx]
    momentum = ((price / past_price) - 1) * 100 if past_price > 0 else 0
    
    # Изменение за день
    if len(hist) >= 2:
        prev = hist['Close'].iloc[-2]
        day_chg = ((price / prev) - 1) * 100
    else:
        day_chg = 0
    
    return momentum, day_chg


# === ИНТЕРФЕЙС ===

st.title("📊 Momentum Scanner")
st.markdown("### Стратегия Кэлломэги + Первичный фильтр")

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
    st.markdown(f"**Активных тикеров:** {len(EXTENDED_TICKERS)}")

# Выбор периода
col1, col2 = st.columns([3, 1])
with col1:
    period_name = st.selectbox("Выберите период моментума:", list(PERIODS.keys()))
with col2:
    if st.button("🔄 Обновить", use_container_width=True):
        st.rerun()

period_key, period_label = PERIODS[period_name]

st.markdown("---")

# === ЗАГРУЗКА И ФИЛЬТРАЦИЯ ДАННЫХ ===

if 'filtered_tickers' not in st.session_state:
    st.session_state.filtered_tickers = None
    st.session_state.filter_results = None

# Кнопка запуска фильтрации
if st.button("🚀 Применить фильтры и построить список"):
    with st.spinner("Фильтрация акций..."):
        filtered = []
        results = []
        progress_bar = st.progress(0)
        
        for i, ticker in enumerate(EXTENDED_TICKERS):
            try:
                stock = yf.Ticker(ticker)
                info = stock.info
                hist = stock.history(period="1mo")  # Достаточно для ADR
                
                passed, reason = check_filters(ticker, info, hist)
                
                if passed:
                    filtered.append({
                        'ticker': ticker,
                        'price': info.get('currentPrice') or info.get('regularMarketPrice'),
                        'market_cap': info.get('marketCap'),
                        'volume': info.get('averageVolume'),
                        'adr': ((hist['High'].max() - hist['Low'].min()) / hist['Low'].min()) * 100
                    })
                else:
                    results.append({'ticker': ticker, 'status': reason})
                    
            except Exception as e:
                results.append({'ticker': ticker, 'status': f"Error: {e}"})
            
            progress_bar.progress((i + 1) / len(EXTENDED_TICKERS))
        
        st.session_state.filtered_tickers = filtered
        st.session_state.filter_results = results

# === ОТОБРАЖЕНИЕ РЕЗУЛЬТАТОВ ФИЛЬТРАЦИИ ===

if st.session_state.filtered_tickers:
    filtered = st.session_state.filtered_tickers
    
    st.success(f"✅ Фильтр прошли: {len(filtered)} акций")
    
    # Показать отфильтрованный список
    with st.expander("📋 Список акций после фильтра"):
        df_filtered = pd.DataFrame(filtered)
        if not df_filtered.empty:
            df_filtered['Market Cap ($M)'] = df_filtered['market_cap'] / 1_000_000
            df_filtered['Volume (K)'] = df_filtered['volume'] / 1000
            df_filtered = df_filtered.sort_values('Market Cap ($M)', ascending=False)
            st.dataframe(
                df_filtered[['ticker', 'price', 'Market Cap ($M)', 'Volume (K)', 'adr']].head(50),
                use_container_width=True
            )
    
    # === РАСЧЁТ МОМЕНТУМА ===
    st.markdown("---")
    st.markdown(f"### 📈 Топ {top_percent}% моментум ({period_name})")
    
    with st.spinner("Расчёт моментума..."):
        momentum_data = []
        progress = st.progress(0)
        
        for i, item in enumerate(filtered):
            ticker = item['ticker']
            try:
                stock = yf.Ticker(ticker)
                hist = stock.history(period=period_key)
                
                if hist.empty:
                    continue
                
                momentum, day_chg = calculate_momentum(hist, period_key)
                
                momentum_data.append({
                    'Ticker': ticker,
                    'Price': hist['Close'].iloc[-1],
                    'Momentum %': momentum,
                    'Day %': day_chg,
                    'Volume': item['volume']
                })
                
            except Exception as e:
                continue
            
            progress.progress((i + 1) / len(filtered))
        
        if momentum_data:
            df = pd.DataFrame(momentum_data)
            df = df.sort_values('Momentum %', ascending=False)
            
            # Топ %
            top_n = max(3, int(len(df) * top_percent / 100))
            df_top = df.head(top_n)
            
            # Метрики
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Прошли фильтр", len(filtered))
            c2.metric("Для анализа", len(df))
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
            
            st.markdown(f"<small>Обновлено: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</small>", unsafe_allow_html=True)
            
            # Скачать CSV
            csv = df_top.to_csv(index=False)
            st.download_button("📥 Скачать CSV", csv, "momentum_stocks.csv")
        else:
            st.warning("Не удалось рассчитать моментум")

else:
    st.info("👈 Настройте фильтры слева и нажмите 'Применить фильтры'")
