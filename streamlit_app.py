import pandas as pd
import streamlit as st
import json
import yfinance as yf
from datetime import date, datetime

def load_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return pd.json_normalize(data)

@st.cache_data
def prepare_static_data():
    users_df = load_json('users_picks.json')
    tickers_df = load_json('tickers.json')
    prices_df = load_json('prices_start.json')
    return users_df, tickers_df, prices_df

@st.cache_data(ttl=86400)
def yf_yesterday_close(ticker):
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="5d")
        if hist.empty:
            return None
        
        return round(float(hist['Close'].iloc[-1]), 2)
    
    except Exception:
        print("Nie dziala yf SAD")
        return None
    
@st.cache_data(ttl=86400)  
def yf_close_all(tickers):
    prices = {}
    for ticker in tickers:
        prices[ticker] = yf_yesterday_close(ticker)
    return prices
    

@st.cache_data(ttl=86400)
def stooq_yesterday_close(ticker):
    """Pojedynczy ticker z Stooq"""
    url = f"https://stooq.pl/q/d/l/?s={ticker}"
    try:
        df = pd.read_csv(url)
        last_date = datetime.strptime(df['Data'].iloc[-1], '%Y-%m-%d').date()
        return df['Zamkniecie'].iloc[-1] if not df.empty and (date.today() - last_date).days < 30 else None
    except:
        print(f"Nie dziala stooq dla {ticker} SAD")
        return None

@st.cache_data(ttl=86400)
def stooq_close_all(tickers):
    prices = {}
    for ticker in tickers:
        prices[ticker] = stooq_yesterday_close(ticker)
    return prices

users_df, tickers_df, prices_df = prepare_static_data()

current_prices_stooq = pd.DataFrame(stooq_close_all(tickers_df[tickers_df['source'] == 'STOOQ']['ticker']).items(), columns=['ticker', 'price_now'])
current_prices_yf = pd.DataFrame(yf_close_all(tickers_df[tickers_df['source'] == 'YF']['ticker']).items(), columns=['ticker', 'price_now'])



all_prices = prices_df.merge(tickers_df, on='ticker').merge(pd.concat([current_prices_yf, current_prices_stooq]), on='ticker', how='left')[['ticker', 'name', 'price', 'price_now']]
all_prices = all_prices.fillna(0)
all_prices = all_prices.rename(columns={"price": "2025-01-02", "price_now": "yesterday"})
all_prices['diff'] = round(100*(all_prices['yesterday'] - all_prices['2025-01-02'])/(all_prices['2025-01-02'] + 1e-6), 2)


name_to_diff = dict(zip(all_prices['name'], all_prices['diff']))
users_df['Wynik spółka 1'] = users_df['Stock1'].map(name_to_diff)
users_df['Wynik spółka 2'] = users_df['Stock2'].map(name_to_diff)
users_df['Wynik spółka 3'] = users_df['Stock3'].map(name_to_diff)
users_df['Średnia'] = round((users_df['Wynik spółka 1'] + users_df['Wynik spółka 2'] + users_df['Wynik spółka 3']) / 3, 2)

users_df = users_df.rename(columns={"Username": "Użytkownik", "Stock1": "Spółka 1", "Stock2": "Spółka 2", "Stock3": "Spółka 3"})
all_prices = all_prices.rename(columns={"name": "Spółka", "yesterday": "Wczoraj", "diff": "Różnica"})[['Spółka', '2025-01-02', 'Wczoraj', 'Różnica']]
https://github.com/AdamBankz/kick-viewbot
# === APLIKACJA ===
st.set_page_config(
    page_title="Ranking giełdowy",
    layout="wide"
)
st.title("📈 Ranking Giełdowy - Paweł Delord Szabla*")
st.markdown("**Witaj w rankingu inwestycyjnym!**")
st.markdown(
    "<span style='font-size: 18px; color: red;'>#bajka #zabawa #gra</span>",
    unsafe_allow_html=True,
)
st.subheader("👥 Wybory Użytkowników")
st.dataframe(users_df, width='stretch')
st.subheader("💰 Ceny Początkowe Spółek")
st.dataframe(all_prices, width='stretch')
st.markdown(
    "<span style='font-size: 10px; color: gray;'>*Materiały i informacje przedstawione na niniejszej stronie internetowej zamieszczone są jedynie w celu informacyjnym. Nie stanowią one porady inwestycyjnej, nawet jeśli wyraźnie wskazują na spółkę lub papier wartościowy. Niniejsze informacje nie stanowią oferty inwestycyjnej, rekomendacji inwestycyjnej czy oferty świadczenia jakiejkolwiek usługi.</span>",
    unsafe_allow_html=True,
)