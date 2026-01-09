import pandas as pd
from modules.helpers import DataLoader, YahooData, StooqData, Static2025Data
from modules.backend import Backend
from modules.frontend import Frontend

frontend = Frontend()
frontend.waiting_screen()
ranking_2025, sp500_2025 = Static2025Data.get_2025_data()

df, start_prices = DataLoader().prepare_static_data()

yahoo_tickers = (
    start_prices[start_prices["source"] == "YAHOO"]["ticker"].unique().tolist()
)
stooq_tickers = (
    start_prices[start_prices["source"] == "STOOQ"]["ticker"].unique().tolist()
)

yf_current_prices = YahooData.get_yf_prices(yahoo_tickers)
stooq_current_prices = StooqData.get_stooq_prices(stooq_tickers)
all_prices = pd.concat([yf_current_prices, stooq_current_prices]).fillna(0)

sp500_benchmark_current_price = YahooData.get_yf_prices(["^GSPC"])

backend = Backend(sp500_benchmark_current_price, start_prices, all_prices, df)

sp500_2026 = backend.get_prices_and_ranking()
ranking_2026 = backend.get_ranking()

frontend.run_frontend(ranking_2025, sp500_2025, ranking_2026, sp500_2026)
