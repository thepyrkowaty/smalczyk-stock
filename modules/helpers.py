import pandas as pd
import streamlit as st
import json
import yfinance as yf
import glob
import requests
from datetime import date, datetime
from bs4 import BeautifulSoup


class DataLoader:
    @staticmethod
    @st.cache_data
    def prepare_static_data():
        path = "data/2026/start_prices_*.csv"
        all_files = glob.glob(path)

        stock_dfs = [pd.read_csv(f) for f in all_files]

        df_ranking = pd.read_csv(
            "data/2026/2026.csv", usecols=lambda col: col not in ["Czas", "Community"]
        )

        combined_stocks = pd.concat(stock_dfs, ignore_index=True)
        return df_ranking, combined_stocks


class YahooData:
    @staticmethod
    @st.cache_data(ttl=28800)
    def get_yf_prices(tickers):
        unique_tickers = list(set(filter(None, tickers)))

        try:
            data = yf.download(
                tickers=unique_tickers,
                period="7d",
                interval="1d",
                progress=False,
                auto_adjust=True,
                timeout=30,
            )

            if data is None or data.empty:
                return pd.DataFrame(columns=["ticker", "price_now"])

            close_prices = data["Close"].ffill().bfill()
            last_row = close_prices.iloc[-1]

            result = last_row.reset_index()
            result.columns = ["ticker", "price_now"]

            result = result.drop_duplicates(subset="ticker")
            result["price_now"] = pd.to_numeric(
                result["price_now"], errors="coerce"
            ).round(10)

            return result

        except Exception as e:
            st.error(f"⚠️ Błąd pobierania danych: {e}")
            return pd.DataFrame(columns=["ticker", "price_now"])


class StooqData:
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
            print(f"Nie dziala stooq dla {ticker} SAD")
            return None

    @staticmethod
    def get_stooq_prices(tickers):
        return pd.DataFrame(
            {
                ticker: StooqData.__stooq_yesterday_close(ticker) for ticker in tickers
            }.items(),
            columns=["ticker", "price_now"],
        )


class NewConnect:
    @staticmethod
    @st.cache_data(ttl=28800)
    def __get_NC_price(ticker):
        url = f"https://www.biznesradar.pl/notowania/{ticker}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            price_string = soup.find("span", class_="q_ch_act").text.strip()
            price = float(price_string.replace(",", ".").replace(" ", ""))
            return price

        except Exception as e:
            print(f"Błąd dla {ticker}: {e}")
            return None

    @staticmethod
    def get_prices(tickers):
        return pd.DataFrame(
            {ticker: NewConnect.__get_NC_price(ticker) for ticker in tickers}.items(),
            columns=["ticker", "price_now"],
        )


class Static2025Data:
    @staticmethod
    @st.cache_data()
    def get_2025_data():
        ranking = pd.read_csv(r"data/2025/2025.csv", index_col=[0])
        sp500_benchmark = pd.read_csv(r"data/2025/sp500.csv")
        return ranking, sp500_benchmark
