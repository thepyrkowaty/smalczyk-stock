import pandas as pd
import streamlit as st
import json
import yfinance as yf
from datetime import date, datetime


class DataLoader:
    def __init__(self):
        pass

    @staticmethod
    def __load_json(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return pd.json_normalize(data)

    @staticmethod
    @st.cache_data
    def prepare_static_data():
        users_df = DataLoader.__load_json("data/users_picks.json").rename(
            columns={
                "Username": "Użytkownik",
                "Stock1": "Spółka 1",
                "Stock2": "Spółka 2",
                "Stock3": "Spółka 3",
            }
        )
        tickers_df = DataLoader.__load_json("data/tickers.json")
        prices_df = DataLoader.__load_json("data/prices_start.json")
        return users_df, tickers_df, prices_df


class YahooData:
    def __init__(self):
        pass

    @staticmethod
    @st.cache_data(ttl=28800)
    def __yf_yesterday_close(ticker):
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="5d")
            if hist.empty:
                return None

            return round(float(hist["Close"].iloc[-1]), 2)

        except Exception:
            raise Exception(f"Nie dziala yf dla {ticker} SAD")

    @staticmethod
    def get_yf_prices(tickers):
        return pd.DataFrame(
            {
                ticker: YahooData.__yf_yesterday_close(ticker) for ticker in tickers
            }.items(),
            columns=["ticker", "price_now"],
        )


class StooqData:
    def __init__(self):
        pass

    @staticmethod
    @st.cache_data(ttl=28800)
    def __stooq_yesterday_close(ticker):
        url = f"https://stooq.pl/q/d/l/?s={ticker}"
        try:
            df = pd.read_csv(url)
            last_date = datetime.strptime(df["Data"].iloc[-1], "%Y-%m-%d").date()
            return (
                df["Zamkniecie"].iloc[-1]
                if not df.empty and (date.today() - last_date).days < 30
                else None
            )
        except:
            raise Exception(f"Nie dziala stooq dla {ticker} SAD")

    @staticmethod
    def get_stooq_prices(tickers):
        return pd.DataFrame(
            {
                ticker: StooqData.__stooq_yesterday_close(ticker) for ticker in tickers
            }.items(),
            columns=["ticker", "price_now"],
        )
