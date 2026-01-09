import pandas as pd
import streamlit as st
import json
import yfinance as yf
from datetime import date, datetime


class DataLoader:
    def __init__(self):
        pass

    @staticmethod
    @st.cache_data
    def prepare_static_data():
        stock_poland = pd.read_csv("data/2026/start_prices_pl.csv")
        stock_crypto = pd.read_csv("data/2026/start_prices_crypto.csv")
        stock_commodities = pd.read_csv("data/2026/start_prices_commodities.csv")
        stock_world = pd.read_csv("data/2026/start_prices_world.csv")
        stock_usa = pd.read_csv("data/2026/start_prices_usa.csv")
        df = pd.read_csv(
            "data/2026/2026.csv",
            usecols=lambda column: column not in ["Czas", "Community"],
        )

        return df, pd.concat(
            [stock_poland, stock_usa, stock_world, stock_crypto, stock_commodities]
        ).reset_index(drop=True)


class YahooData:
    def __init__(self):
        pass

    @staticmethod
    @st.cache_data(ttl=28800)
    def get_yf_prices(tickers):
        try:
            # 1. Pobieramy dane (period 7d daje zapas na polskie święta/weekendy)
            data = yf.download(
                tickers=tickers,
                period="7d",
                interval="1d",
                progress=False,
                auto_adjust=True,
                timeout=30
            )

            if data is None or data.empty:
                return pd.DataFrame(columns=["ticker", "price_now"])

            close_prices = data["Close"]
            filled_data = close_prices.ffill().bfill()

            last_row = filled_data.iloc[-1]

            if isinstance(last_row, pd.Series):
                result = last_row.reset_index()
                result.columns = ["ticker", "price_now"]
            else:
                result = pd.DataFrame(
                    {
                        "ticker": [tickers if isinstance(tickers, str) else tickers[0]],
                        "price_now": [last_row],
                    }
                )

            result["price_now"] = result["price_now"].round(10)

            return result

        except Exception as e:
            print(f"Błąd pobierania danych: {e}")
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


class Static2025Data:
    def __init__(self) -> None:
        pass

    @staticmethod
    @st.cache_data()
    def get_2025_data():
        ranking = pd.read_csv(r"data/2025/2025.csv", index_col=[0])
        sp500_benchmark = pd.read_csv(r"data/2025/sp500.csv")
        return ranking, sp500_benchmark
