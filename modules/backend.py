import pandas as pd
import numpy as np


class Backend:
    def __init__(self, sp500_benchmark, start_prices, current_prices, ranking) -> None:
        self.__sp500_benchmark = sp500_benchmark
        self.__start_prices = start_prices
        self.__current_prices = current_prices
        self.__ranking = ranking
        self.__stats = pd.merge(
            self.__start_prices, self.__current_prices, how="left", on="ticker"
        )[["name", "ticker", "start_price", "price_now"]]
        self.__stats["diff"] = round(
            100
            * (self.__stats["price_now"] - self.__stats["start_price"])
            / (self.__stats["start_price"] + 1e-20),
            2,
        )
        self.__ticker_map = self.__stats.set_index("ticker")["diff"].to_dict()
        self.__name_map = self.__stats.set_index("name")["diff"].to_dict()
        self.__values_to_fill = {
            "Wynik Świat": 0,
            "Wynik Surowiec": 0,
            "Wynik Krypto": 0,
            "Wynik Polska": 0,
            "Wynik Usa": 0,
            "Surowiec": "BRAK",
            "Krypto": "BRAK",
            "Spółka Świat": "BRAK",
            "Spółka Usa": "BRAK",
        }

    def __get_sp500_benchmark_stats(self):
        df = self.__sp500_benchmark.copy()
        df["2025-12-31"] = 6845.5
        df = df.rename(columns={"price_now": "Wczoraj"})
        df["Wynik"] = round(
            100 * (df["Wczoraj"] - df["2025-12-31"]) / (df["2025-12-31"] + 1e-6), 2
        )
        return df[["2025-12-31", "Wczoraj", "Wynik"]]

    def get_ranking(self):
        self.__ranking["Wynik Świat"] = self.__ranking["Ticker Świat"].map(
            self.__ticker_map
        )
        self.__ranking["Wynik Usa"] = self.__ranking["Ticker Usa"].map(
            self.__ticker_map
        )
        self.__ranking["Wynik Surowiec"] = self.__ranking["Surowiec"].map(
            self.__name_map
        )
        self.__ranking["Wynik Krypto"] = self.__ranking["Krypto"].map(self.__name_map)
        self.__ranking["Wynik Polska"] = self.__ranking["Spółka Polska"].map(
            self.__name_map
        )
        self.__ranking["Wynik Usa"] = np.where(
            self.__ranking["Czy Usa"] == 0, 0, self.__ranking["Wynik Usa"]
        )
        self.__ranking["Wynik Świat"] = np.where(
            self.__ranking["Czy Świat"] == 0, 0, self.__ranking["Wynik Świat"]
        )
        self.__ranking["Średnia"] = (
            self.__ranking["Wynik Polska"] * 0.25
            + self.__ranking["Wynik Świat"] * 0.25
            + self.__ranking["Wynik Usa"] * 0.25
            + self.__ranking["Wynik Surowiec"] * 0.15
            + self.__ranking["Wynik Krypto"] * 0.10
        )

        return (
            self.__ranking.fillna(self.__values_to_fill)
            .sort_values(by="Średnia", ascending=False)
            .reset_index(drop=True)
        )

    def get_prices_and_ranking(self):
        sp500_benchmark = self.__get_sp500_benchmark_stats()
        return sp500_benchmark
