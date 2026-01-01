import pandas as pd
import streamlit as st
from modules.helpers import DataLoader, YahooData, StooqData
from modules.backend import Backend
from modules.frontend import Frontend

frontend = Frontend()

frontend.waiting_screen()

# users_df, tickers_df, start_prices_df = DataLoader().prepare_static_data()
# stooq_current_prices = StooqData.get_stooq_prices(
#     tickers_df[tickers_df["source"] == "STOOQ"]["ticker"].values.tolist()
# )
# yf_current_prices = YahooData.get_yf_prices(
#     tickers_df[tickers_df["source"] == "YF"]["ticker"].values.tolist()
# )
# sp500_benchmark_current_price = YahooData.get_yf_prices(["^GSPC"])

# backend = Backend(
#     tickers_df,
#     start_prices_df,
#     pd.concat([stooq_current_prices, yf_current_prices]),
#     users_df,
#     sp500_benchmark_current_price,
# )

# prices, ranking, sp500_benchmark = backend.get_prices_and_ranking()

ranking = pd.read_csv(r"data\2025\2025.csv")
sp500_benchmark = pd.read_csv(r"data\2025\sp500.csv")


frontend.run_frontend(ranking, sp500_benchmark)
