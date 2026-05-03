import pandas as pd
from modules.helpers import (
    DataLoader,
    YahooData,
    NewConnect,
    Static2025Data,
    NickelData,
)
from modules.backend import Backend
from modules.frontend import Frontend

import streamlit as st

frontend = Frontend()
frontend.waiting_screen()
ranking_2025, sp500_2025 = Static2025Data.get_2025_data()

df, start_prices = DataLoader().prepare_static_data()

all_t = pd.Series(df.filter(like="Ticker").values.flatten()).dropna().unique()

yahoo_tickers = [t.split(":")[1] for t in all_t if t.startswith("YAHOO:")]
bankier_tickers = [t.split(":")[1] for t in all_t if t.startswith("BANKIER:")]
nc_tickers = [t.split(":")[1] for t in all_t if t.startswith("NC:")]

yf_ytd = YahooData.get_yf_ytd(yahoo_tickers)
nc_ytd = NewConnect.get_nc_ytd(nc_tickers)
nickel_ytd = NickelData.get_nickel_ytd()

all_ytd = pd.concat([yf_ytd, nc_ytd, nickel_ytd]).fillna(0)
sp500_ytd = YahooData.get_yf_ytd(["^GSPC"])
backend = Backend(all_ytd, df, sp500_ytd)
ranking_2026, sp500_2026 = backend.get_ranking()
frontend.run_frontend(ranking_2025, sp500_2025, ranking_2026, sp500_2026)
