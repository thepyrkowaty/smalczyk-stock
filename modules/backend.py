import pandas as pd


class Backend:
    def __init__(self, tickers, start_prices, current_prices, users) -> None:
        self.__tickers = tickers
        self.__start_prices = start_prices
        self.__current_prices = current_prices
        self.__users = users

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
            columns={"name": "Spółka", "yesterday": "Wczoraj", "diff": "Różnica"}
        )[["Spółka", "2025-01-02", "Wczoraj", "Różnica"]]
        return all_prices

    def __get_users_stats(self, prices, users):
        name_to_diff = dict(zip(prices["Spółka"], prices["Różnica"]))
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
        return ranking

    def get_prices_and_ranking(self):
        prices = self.__get_prices_stats()
        ranking = self.__get_users_stats(prices, self.__users)
        return prices, ranking
