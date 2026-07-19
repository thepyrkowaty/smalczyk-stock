import streamlit as st
import pandas as pd
import base64
from pathlib import Path

COLUMNS = [
    "Miejsce",
    "Użytkownik",
    "Spółka Polska",
    "Wynik Polska",
    "Spółka Usa",
    "Wynik Usa",
    "Spółka Świat",
    "Wynik Świat",
    "Surowiec",
    "Wynik Surowiec",
    "Krypto",
    "Wynik Krypto",
    "Średnia Spółki",
    "Średnia Ważona",
    "Czy Usa",
    "Czy Świat",
    "Ticker Usa",
    "Ticker Świat",
    "Czy Streamer",
]

PERCENT_COLS = [
    "Wynik Polska",
    "Wynik Usa",
    "Wynik Świat",
    "Wynik Surowiec",
    "Wynik Krypto",
    "Średnia Ważona",
    "Średnia Spółki",
]

COLUMN_CONFIG = {
    "Użytkownik": st.column_config.TextColumn("Użytkownik", width="large"),
    "Spółka Polska": st.column_config.TextColumn("Spółka Polska", width="medium"),
    "Spółka Świat": st.column_config.TextColumn("Spółka Świat", width="medium"),
    "Surowiec": st.column_config.TextColumn("Surowiec", width="medium"),
    "Krypto": st.column_config.TextColumn("Krypto"),
    **{
        c: None
        for c in ["Czy Usa", "Czy Świat", "Ticker Usa", "Ticker Świat", "Czy Streamer"]
    },
}

DISCLAIMER_CAPTION = (
    "<span style='font-size: 10px; color: gray;'>"
    "Materiały i informacje przedstawione na niniejszej stronie internetowej "
    "zamieszczone są jedynie w celu informacyjnym. Nie stanowią one porady "
    "inwestycyjnej, nawet jeśli wyraźnie wskazują na spółkę lub papier wartościowy. "
    "Niniejsze informacje nie stanowią oferty inwestycyjnej, rekomendacji "
    "inwestycyjnej czy oferty świadczenia jakiejkolwiek usługi."
    "</span>"
)

BAJKA_ZABAWA_GRA = (
    "<span style='font-size: 20px; color: red;'>**#bajka #zabawa #gra**</span>"
)

DISABLE_TOOLBOX = """
<style>
    [data-testid="stElementToolbar"] {display: none !important;}
</style>
"""

MENU_RANKING_2026 = "Ranking 2026"
MENU_RANKING_2025 = "Ranking 2025"
MENU_DISCLAIMER = "Disclaimer"

class Styler:

    @staticmethod
    def styler_2025(benchmark=None, color_column=None, percent_column=None):
        def apply(df):
            styled = df.style
            if percent_column is not None:
                styled = styled.format(
                    {c: "{:.2f}%" for c in percent_column}, precision=2
                )

            if benchmark is not None and color_column is not None:

                def color(val):
                    if val >= benchmark:
                        return "background-color: OliveDrab; color: black; font-weight: bold"
                    else:
                        return "background-color: red; color: black; font-weight: bold"

                styled = styled.map(color, subset=[color_column])

            return styled

        return apply

    @staticmethod
    def styler_2026(row, sp500_df, day):
        style = pd.Series("", index=row.index)
        benchmark = sp500_df.loc[sp500_df["day"] == day, "ytd_change"].iloc[-1]
        if row.get("Czy Streamer", 0) == 1 and "Użytkownik" in style.index:
            style["Użytkownik"] = "background-color: yellow; color: black;"

        for market in ["Usa", "Świat"]:
            czy_col = f"Czy {market}"
            spolka_col = f"Spółka {market}"
            wynik_col = f"Wynik {market}"

            if czy_col in row.index and row[czy_col] == 0:
                s = "background-color: #FFF0F0; color: #884444;"
                if spolka_col in style.index:
                    style[spolka_col] = s
                if wynik_col in style.index:
                    style[wynik_col] = s

        def get_color(val):
            if pd.isna(val):
                return ""
            if benchmark is None or pd.isna(benchmark):
                return "lightgray"
            if val < 0:
                return "red"
            if val < benchmark:
                return "orange"
            return "OliveDrab"

        for col in ["Średnia Ważona", "Średnia Spółki"]:
            if col in row.index:
                color = get_color(row[col])
                if color:
                    style[col] = (
                        f"background-color: {color}; color: black; font-weight: bold;"
                    )

        return style


class FrontendHelpers:

    @staticmethod
    def img_to_bytes(img_path):
        img_bytes = Path(img_path).read_bytes()
        encoded = base64.b64encode(img_bytes).decode()
        return encoded

    @staticmethod
    def img_to_html(img_path, message, height="80vh"):
        src = FrontendHelpers.img_to_bytes(img_path)
        return f"""
        <div style="height:{height}; display:flex; flex-direction:column; 
                    justify-content:center; align-items:center; text-align:center;">
            <img src="data:image/png;base64,{src}" style="width:124px; margin-bottom:10px;" />
            <div style="font-size:36px; font-weight:800; letter-spacing:4px;">
                {message}
            </div>
        </div>
        """
