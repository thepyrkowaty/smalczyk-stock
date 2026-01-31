import streamlit as st
import pandas as pd
import base64
from pathlib import Path

COLUMNS = [
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
    def styler_2026(row, benchmark):
        style = pd.Series("", index=row.index)

        # 1. Streamer
        if row["Czy Streamer"] == 1:
            style["Użytkownik"] = "background-color: yellow; color: black;"

        # 2. Nieaktywne rynki
        for market in ["Usa", "Świat"]:
            if row[f"Czy {market}"] == 0:
                s = "background-color: #FFF0F0; color: #884444;"
                style[f"Spółka {market}"] = style[f"Wynik {market}"] = s

        # 3. Wyniki
        def get_color(val):
            if val < 0:
                return "red"
            if val < benchmark:
                return "orange"
            return "OliveDrab"

        for col in ["Średnia Ważona", "Średnia Spółki"]:
            style[col] = (
                f"background-color: {get_color(row[col])}; color: black; font-weight: bold"
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
