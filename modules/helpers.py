import pandas as pd
import streamlit as st
import json
import yfinance as yf
import glob
import requests
from datetime import date, datetime, timedelta
from bs4 import BeautifulSoup
import time
import re


class DataLoader:
    @staticmethod
    @st.cache_data
    def prepare_static_data():
        start_prices = pd.read_csv("data/2026/start_prices.csv")
        df_ranking = pd.read_csv(
            "data/2026/2026_new.csv",
            usecols=lambda col: col not in ["Czas", "Community"],
        )
        return df_ranking, start_prices


class YahooData:
    @staticmethod
    @st.cache_data(ttl=28800)
    def get_yf_ytd(tickers):
        unique_tickers = list(set(filter(None, tickers)))
        if not unique_tickers:
            return pd.DataFrame(columns=["ticker", "ytd_change"])

        batch_size = 100
        all_results = []
        start_date = "2025-12-28"
        last_year_end = "2025-12-31"

        batches = [
            unique_tickers[i : i + batch_size]
            for i in range(0, len(unique_tickers), batch_size)
        ]

        try:
            for idx, batch in enumerate(batches):
                data = yf.download(
                    tickers=batch,
                    start=start_date,
                    interval="1d",
                    progress=False,
                    auto_adjust=True,
                    timeout=30,
                    threads=True,
                )

                if data is not None and not data.empty:
                    close = data["Close"].ffill()

                    if isinstance(close, pd.Series):
                        close = close.to_frame(name=batch[0])

                    close = close.sort_index()
                    cutoff = pd.Timestamp(last_year_end)

                    p_start_list = []
                    for ticker in close.columns:
                        s = close[ticker].dropna()
                        s_2025 = s[s.index <= cutoff]
                        p_start_list.append(
                            s_2025.iloc[-1] if not s_2025.empty else pd.NA
                        )

                    p_start = pd.Series(p_start_list, index=close.columns)
                    p_now = close.iloc[-1]

                    if "CRI.WA" in p_now.index:
                        p_now.loc["CRI.WA"] = p_now.loc["CRI.WA"] + 220  # CRQ OPEN
                    if "SNT.WA" in p_now.index:
                        p_now.loc["SNT.WA"] = p_now.loc["SNT.WA"] + 44  # S2B OPEN

                    df_batch = pd.DataFrame(
                        {
                            "ticker": p_now.index,
                            "ytd_change": ((p_now - p_start) / p_start * 100)
                            .round(2)
                            .values,
                        }
                    )
                    all_results.append(df_batch)

                if idx < len(batches) - 1:
                    time.sleep(1)

            if not all_results:
                return pd.DataFrame(columns=["ticker", "ytd_change"])

            result = pd.concat(all_results, ignore_index=True)
            result["ticker"] = "YAHOO:" + result["ticker"].astype(str)

            return result.drop_duplicates(subset="ticker")

        except Exception as e:
            st.error(f"⚠️ Krytyczny błąd pobierania danych YAHOO: {e}")
            return pd.DataFrame(columns=["ticker", "ytd_change"])


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

            one_d_row = None
            ytd_row = None

            for row in soup.select("#profileSummaryCompare tr"):
                th = row.find("th")
                if not th:
                    continue

                label = th.get_text(strip=True)

                if label == "Zmiana 1d:":
                    one_d_row = row
                elif label == "Zmiana YTD:":
                    ytd_row = row

            if one_d_row is None or ytd_row is None:
                return 0.0

            one_d_tds = one_d_row.find_all("td")
            ytd_tds = ytd_row.find_all("td")

            if len(one_d_tds) < 4 or len(ytd_tds) < 2:
                return 0.0

            date_txt = one_d_tds[3].get_text(strip=True)
            date_dt = datetime.strptime(date_txt, "%d.%m.%Y").date()
            cutoff = (datetime.now() - timedelta(days=7)).date()

            if date_dt < cutoff:
                return 0.0

            q_ch_per_txt = ytd_tds[1].get_text(strip=True)
            q_ch_per_txt = (
                q_ch_per_txt.replace("(", "")
                .replace(")", "")
                .replace("%", "")
                .replace(",", ".")
                .strip()
            )

            return float(q_ch_per_txt)

        except Exception as e:
            st.error(f"⚠️ Krytyczny błąd pobierania danych NC: {e}")
            return pd.DataFrame(columns=["ticker", "ytd_change"])

    @staticmethod
    def get_nc_ytd(tickers):
        result = pd.DataFrame(
            {ticker: NewConnect.__get_NC_price(ticker) for ticker in tickers}.items(),
            columns=["ticker", "ytd_change"],
        )
        result["ticker"] = "NC:" + result["ticker"].astype(str)
        return result


class NickelData:
    @staticmethod
    @st.cache_data(ttl=28800)
    def __get_nickel_price():
        url = "https://www.bankier.pl/surowce/krotkoterminowe-stopy-zwrotu"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        try:
            response = requests.get(url, headers=headers, timeout=15)
            soup = BeautifulSoup(response.text, "html.parser")
            rows = (
                soup.find("table", class_="m-quotes-data-table")
                .find("tbody")
                .find_all("tr")
            )
            data = []

            for row in rows:
                name_tag = row.find("a", class_="a-anchor")
                name = name_tag.get_text(strip=True) if name_tag else None

                cols = row.find_all("td")
                values = [col.get_text(" ", strip=True) for col in cols]
                data.append([name] + values[1:])

            df = pd.DataFrame(
                data,
                columns=[
                    "Surowiec",
                    "Kurs",
                    "1D",
                    "1T",
                    "2T",
                    "1M",
                    "2M",
                    "3M",
                    "6M",
                    "YTD",
                    "Data",
                ],
            )

            return float(
                df[df["Surowiec"] == "Nikiel"]["YTD"]
                .iloc[0]
                .replace("%", "")
                .replace("+", "")
                .replace(",", ".")
            )
        except Exception as e:
            st.error(f"⚠️ Krytyczny błąd pobierania danych NICKEL: {e}")
            return pd.DataFrame(columns=["ticker", "ytd_change"])

    @staticmethod
    def get_nickel_ytd():
        result = pd.DataFrame(
            {"NIKIEL": NickelData.__get_nickel_price()}.items(),
            columns=["ticker", "ytd_change"],
        )
        result["ticker"] = "BANKIER:" + result["ticker"].astype(str)

        return result


class Static2025Data:
    @staticmethod
    @st.cache_data()
    def get_2025_data():
        ranking = pd.read_csv(r"data/2025/2025.csv", index_col=[0])
        sp500_benchmark = pd.read_csv(r"data/2025/sp500.csv")
        return ranking, sp500_benchmark
