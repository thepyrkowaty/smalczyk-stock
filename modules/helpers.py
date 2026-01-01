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
    def get_yf_prices(tickers):
        try:
            data = yf.download(
                tickers=tickers,
                period="5d",
                interval="1d",
                group_by="column",
                progress=False,
                auto_adjust=True,
            )

            if data is None or data.empty:
                return pd.DataFrame(columns=["ticker", "price_now"])

            close_prices = data["Close"]

            if len(close_prices) >= 2:
                result = close_prices.iloc[-2]
            else:
                result = close_prices.iloc[-1]

            result = result.round(2).reset_index()
            result.columns = ["ticker", "price_now"]
            return result

        except Exception as e:
            # Logujemy błąd, ale nie pozwalamy aplikacji "wywalić się"
            st.warning(
                f"Nie udało się pobrać danych z Yahoo Finance, spróbuj za jakiś czas: {e}"
            )
            return pd.DataFrame(columns=["ticker", "price_now"])


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
