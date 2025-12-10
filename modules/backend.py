import pandas as pd


class Backend:
    def __init__(
        self, tickers, start_prices, current_prices, users, sp500_benchmark
    ) -> None:
        self.__tickers = tickers
        self.__start_prices = start_prices
        self.__current_prices = current_prices
        self.__users = users
        self.__sp500_benchmark = sp500_benchmark

    def __get_prices_stats(self):
        all_prices = self.__tickers.merge(self.__start_prices, on="ticker").merge(
            self.__current_prices, on="ticker", how="left"
        )[["ticker", "name", "price", "price_now"]]
        all_prices = all_prices.fillna(0)
        all_prices = all_prices.rename(
            columns={"price": "2025-01-02", "price_now": "yesterday"}
        )
        all_prices["diff"] = round(
            100
            * (all_prices["yesterday"] - all_prices["2025-01-02"])
            / (all_prices["2025-01-02"] + 1e-6),
            2,
        )
        all_prices = all_prices.rename(
            columns={
                "name": "Spółka",
                "yesterday": "Wczoraj",
                "diff": "Zmiana procentowa",
            }
        )[["Spółka", "2025-01-02", "Wczoraj", "Zmiana procentowa"]]
        return all_prices.sort_values(
            by="Zmiana procentowa", ascending=False
        ).reset_index(drop=True)

    def __get_users_stats(self, prices, users):
        name_to_diff = dict(zip(prices["Spółka"], prices["Zmiana procentowa"]))
        ranking = users.copy()
        ranking["Wynik spółka 1"] = ranking["Spółka 1"].map(name_to_diff)
        ranking["Wynik spółka 2"] = ranking["Spółka 2"].map(name_to_diff)
        ranking["Wynik spółka 3"] = ranking["Spółka 3"].map(name_to_diff)
        ranking["Średnia"] = round(
            (
                ranking["Wynik spółka 1"]
                + ranking["Wynik spółka 2"]
                + ranking["Wynik spółka 3"]
            )
            / 3,
            2,
        )
        ranking = ranking.sort_values(by="Średnia", ascending=False).reset_index(
            drop=True
        )
        ranking.index += 1
        return ranking

    def __get_sp500_benchmark_stats(self):
        df = self.__sp500_benchmark.copy()
        df["2025-01-02"] = 5868.54
        df = df.rename(columns={"price_now": "Wczoraj"})
        df["Zmiana procentowa"] = round(
            100 * (df["Wczoraj"] - df["2025-01-02"]) / (df["2025-01-02"] + 1e-6), 2
        )
        return df[["2025-01-02", "Wczoraj", "Zmiana procentowa"]]

    def get_prices_and_ranking(self):
        prices = self.__get_prices_stats()
        ranking = self.__get_users_stats(prices, self.__users)
        sp500_benchmark = self.__get_sp500_benchmark_stats()
        return prices, ranking, sp500_benchmark
