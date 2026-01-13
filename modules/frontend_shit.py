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

COLUMN_CONFIG = {
    "Wynik Polska": st.column_config.NumberColumn(
        "Wynik Polska", width="small", format="%.2f%%"
    ),
    "Wynik Usa": st.column_config.NumberColumn(
        "Wynik Usa", width="small", format="%.2f%%"
    ),
    "Wynik Świat": st.column_config.NumberColumn(
        "Wynik Świat", width="small", format="%.2f%%"
    ),
    "Wynik Surowiec": st.column_config.NumberColumn(
        "Wynik Surowiec", width="small", format="%.2f%%"
    ),
    "Wynik Krypto": st.column_config.NumberColumn(
        "Wynik Krypto", width="small", format="%.2f%%"
    ),
    "Średnia Ważona": st.column_config.NumberColumn(
        "Średnia Ważona", width="small", format="%.2f%%"
    ),
    "Średnia Spółki": st.column_config.NumberColumn(
        "Średnia Spółki", width="small", format="%.2f%%"
    ),
    "Użytkownik": st.column_config.TextColumn("Użytkownik", width="large"),
    "Spółka Polska": st.column_config.TextColumn("Spółka Polska", width="medium"),
    "Spółka Świat": st.column_config.TextColumn("Spółka Świat", width="medium"),
    "Surowiec": st.column_config.TextColumn("Surowiec", width="medium"),
    "Krypto": st.column_config.TextColumn("Krypto"),
    "Czy Usa": None,
    "Czy Świat": None,
    "Ticker Usa": None,
    "Ticker Świat": None,
    "Czy Streamer": None,
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

        # 1. Kolorowanie Streamera
        if row["Czy Streamer"] == 1:
            style["Użytkownik"] = "background-color: yellow; color: black;"

        # 2. Ukrywanie nieaktywnych rynków (USA i Świat)
        for market in ["Usa", "Świat"]:
            if row[f"Czy {market}"] == 0:
                color_style = "background-color: #FFF0F0; color: #884444;"
                style[f"Spółka {market}"] = color_style
                style[f"Wynik {market}"] = color_style

        # 3. Logika kolorowania wyników (Średnia Ważona i Średnia Spółki)
        def get_score_style(val):
            if val < 0:
                bg = "red"
            elif val < benchmark:
                bg = "orange"
            else:
                bg = "OliveDrab"
            return f"background-color: {bg}; color: black; font-weight: bold"

        for col in ["Średnia Ważona", "Średnia Spółki"]:
            style[col] = get_score_style(row[col])

        return style


class FrontendHelpers:

    @staticmethod
    def img_to_bytes(img_path):
        img_bytes = Path(img_path).read_bytes()
        encoded = base64.b64encode(img_bytes).decode()
        return encoded

    @staticmethod
    def img_to_html(img_path, message, height="80vh"):
        return """
        <div style="
            height:{height};
            display:flex;
            flex-direction:column;
            justify-content:center;
            align-items:center;
            text-align:center;
        ">
        <img src="data:image/png;base64,{src}" class="img-fluid" style="width:124px; margin-bottom:10px;" />
        <div style="font-size:36px; font-weight:800; letter-spacing:4px;">
            {message}
        </div>
        </div>
        """.format(
            src=FrontendHelpers.img_to_bytes(img_path), message=message, height=height
        )
