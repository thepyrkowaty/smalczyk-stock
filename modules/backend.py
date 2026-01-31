import pandas as pd


class Backend:
    WEIGHTS = {
        "Wynik Polska": 0.25,
        "Wynik Świat": 0.25,
        "Wynik Usa": 0.25,
        "Wynik Surowiec": 0.15,
        "Wynik Krypto": 0.10,
    }

    def __init__(self, sp500_benchmark, start_prices, current_prices, ranking) -> None:
        self.__sp500_benchmark = sp500_benchmark
        self.__ranking = ranking.copy()

        stats = pd.merge(start_prices, current_prices, how="left", on="ticker")[
            ["name", "ticker", "start_price", "price_now"]
        ]

        stats["diff"] = (
            ((stats["price_now"] - stats["start_price"]) / stats["start_price"] * 100)
            .round(2)
            .fillna(0)
        )

        self.__ticker_map = stats.groupby("ticker")["diff"].last()
        self.__name_map = stats.groupby("name")["diff"].last()

    def __get_sp500_benchmark_stats(self):
        df = self.__sp500_benchmark.copy()
        start_val = 6845.5
        df["2025-12-31"] = start_val
        df = df.rename(columns={"price_now": "Wczoraj"})

        df["Wynik"] = ((df["Wczoraj"] - start_val) / start_val * 100).round(2)
        return df[["2025-12-31", "Wczoraj", "Wynik"]]

    def get_ranking(self):
        rank = self.__ranking

        mappings = {
            "Wynik Świat": ("Ticker Świat", self.__ticker_map),
            "Wynik Usa": ("Ticker Usa", self.__ticker_map),
            "Wynik Surowiec": ("Surowiec", self.__name_map),
            "Wynik Krypto": ("Krypto", self.__name_map),
            "Wynik Polska": ("Spółka Polska", self.__name_map),
        }

        for col, (source, mapper) in mappings.items():
            rank[col] = rank[source].map(mapper).fillna(0)

        rank["Wynik Usa"] *= rank.get("Czy Usa", 1)
        rank["Wynik Świat"] *= rank.get("Czy Świat", 1)

        rank["Średnia Spółki"] = rank[
            ["Wynik Polska", "Wynik Świat", "Wynik Usa"]
        ].mean(axis=1)
        rank["Średnia Ważona"] = sum(
            rank[col] * weight for col, weight in self.WEIGHTS.items()
        )

        fill_values = {
            "Surowiec": "BRAK",
            "Krypto": "BRAK",
            "Spółka Świat": "BRAK",
            "Spółka Usa": "BRAK",
        }

        return (
            rank.fillna(fill_values)
            .sort_values(by="Średnia Ważona", ascending=False)
            .reset_index(drop=True)
        )

    def get_prices_and_ranking(self):
        return self.__get_sp500_benchmark_stats()
