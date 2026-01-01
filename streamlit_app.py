import pandas as pd
import streamlit as st
from modules.helpers import DataLoader, YahooData, StooqData, Static2025Data
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

ranking, sp500_benchmark = Static2025Data.get_2025_data()

frontend.run_frontend(ranking, sp500_benchmark)
