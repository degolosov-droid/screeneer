# Momentum Scanner - Простая версия для запуска
# Требуется только Python (без сложной установки)

import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

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
</style>
""", unsafe_allow_html=True)

# Список акций
TICKERS = [
    "AAPL", "MSFT", "AMZN", "NVDA", "GOOGL", "META", "BRK-B", "UNH", "XOM", "JNJ",
    "JPM", "V", "PG", "MA", "HD", "CVX", "MRK", "ABBV", "PEP", "KO",
    "COST", "AVGO", "WMT", "MCD", "CSCO", "ACN", "LIN", "TMO", "ABT", "DHR",
    "VZ", "ADBE", "NEE", "TXN", "PM", "UPS", "RTX", "LOW", "SPGI", "ELV",
    "HON", "COP", "AMGN", "BA", "CAT", "GS", "BLK", "INTU", "ISRG", "AXP",
    "TSLA", "AMD", "NFLX", "INTC", "QCOM", "SBUX", "AMAT", "MU", "MRVL", "PYPL"
]

PERIODS = {"1 неделя": "5d", "1 месяц": "1mo", "3 месяца": "3mo", "6 месяцев": "6mo"}

# Заголовок
st.title("📊 Momentum Scanner")
st.markdown("### Топ акций по моментуму по стратегии Кэлломэги")

# Выбор периода
period_name = st.selectbox("Выберите период:", list(PERIODS.keys()))
period = PERIODS[period_name]

if st.button("🔄 Обновить данные"):
    st.rerun()

st.markdown("---")

# Загрузка данных
with st.spinner("Загрузка данных..."):
    data = []
    for ticker in TICKERS:
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            hist = stock.history(period=period)
            
            if hist.empty:
                continue
            
            price = hist['Close'].iloc[-1]
            if price < 5:
                continue
            
            volume = info.get('volume', 0) if info else 0
            if volume < 100000:
                continue
            
            # Моментум
            if len(hist) >= 5:
                past = hist['Close'].iloc[0]
                momentum = ((price / past) - 1) * 100
            else:
                momentum = 0
            
            # Изменение за день
            if len(hist) >= 2:
                prev = hist['Close'].iloc[-2]
                day_chg = ((price / prev) - 1) * 100
            else:
                day_chg = 0
            
            data.append({
                'Ticker': ticker,
                'Name': info.get('longName', info.get('shortName', ticker)) if info else ticker,
                'Price': price,
                'Momentum': momentum,
                'Day %': day_chg,
                'Volume': volume
            })
        except:
            continue

if not data:
    st.error("Ошибка загрузки данных")
    st.stop()

# DataFrame
df = pd.DataFrame(data)
df = df.sort_values('Momentum', ascending=False)

# Топ 5%
top_n = max(3, int(len(df) * 0.05))
df_top = df.head(top_n)

# Метрики
c1, c2, c3 = st.columns(3)
c1.metric("Топ акций", f"{len(df_top)}")
c2.metric("Ср. моментум", f"{df_top['Momentum'].mean():.1f}%")
c3.metric("Макс. моментум", f"{df_top['Momentum'].max():.1f}%")

st.markdown("---")

# Таблица
st.markdown(f"### 🏆 Топ {len(df_top)} акций ({period_name})")

for i, row in df_top.iterrows():
    m_color = "green" if row['Momentum'] > 0 else "red"
    d_color = "green" if row['Day %'] > 0 else "red"
    
    st.markdown(f"""
    <div style="background:white; padding:15px; margin:10px 0; border-radius:10px; display:flex; justify-content:space-between; align-items:center;">
        <div>
            <b style="font-size:18px;">{row['Ticker']}</b>
            <span style="color:gray; margin-left:10px;">{row['Name'][:30]}</span>
        </div>
        <div style="text-align:right;">
            <div style="font-size:18px;">${row['Price']:.2f}</div>
            <div style="color:{m_color}; font-weight:bold;">М: {'+' if row['Momentum']>0 else ''}{row['Momentum']:.1f}%</div>
            <div style="color:{d_color};">Д: {'+' if row['Day %']>0 else ''}{row['Day %']:.1f}%</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown(f"<small>Обновлено: {datetime.now().strftime('%H:%M:%S')}</small>", unsafe_allow_html=True)
