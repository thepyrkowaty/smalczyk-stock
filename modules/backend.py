import pandas as pd
import numpy as np


class Backend:
    WEIGHTS = {
        "Wynik Polska": 0.25,
        "Wynik Świat": 0.25,
        "Wynik Usa": 0.25,
        "Wynik Surowiec": 0.15,
        "Wynik Krypto": 0.10,
    }

    def __init__(self, all_ytd, ranking, sp500) -> None:
        self.__ranking = ranking.copy()

        self.__ticker_map = (
            all_ytd.dropna(subset=["ticker"])
            .assign(ticker=lambda df: df["ticker"].astype(str).str.strip())
            .groupby("ticker")["ytd_change"]
            .last()
        )

        self.__sp500 = sp500.rename(
            columns={"ytd_change": "Wynik", "ticker": "Benchmark"}
        )
        self.__sp500["Benchmark"] = "SP500"

    def get_ranking(self):
        rank = self.__ranking.copy()
        rank["Wynik Polska"] = rank["Ticker Polska"].map(self.__ticker_map).fillna(0)
        rank["Wynik Świat"] = rank["Ticker Świat"].map(self.__ticker_map).fillna(0)
        rank["Wynik Usa"] = rank["Ticker Usa"].map(self.__ticker_map).fillna(0)
        rank["Wynik Surowiec"] = (
            rank["Ticker Surowiec"].map(self.__ticker_map).fillna(0)
        )
        rank["Wynik Krypto"] = rank["Ticker Krypto"].map(self.__ticker_map).fillna(0)

        rank["Wynik Usa"] *= rank.get("Czy Usa", 1)
        rank["Wynik Świat"] *= rank.get("Czy Świat", 1)

        rank["Średnia Spółki"] = rank[
            ["Wynik Polska", "Wynik Świat", "Wynik Usa"]
        ].mean(axis=1)

        rank["Średnia Ważona"] = sum(
            rank[col] * weight for col, weight in self.WEIGHTS.items()
        )

        return (
            rank.sort_values("Średnia Ważona", ascending=False).reset_index(drop=True),
            self.__sp500,
        )
