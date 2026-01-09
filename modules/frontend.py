import streamlit as st
import base64
from pathlib import Path
import pandas as pd


class Frontend:
    def __init__(self) -> None:
        self.page = st.empty()
        with open("data/disclaimer.html", "r", encoding="utf-8") as f:
            self.__disclaimer = f.read()
        self.__cols = [
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

        self.__config = {
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
            "Spółka Polska": st.column_config.TextColumn(
                "Spółka Polska", width="medium"
            ),
            "Spółka Świat": st.column_config.TextColumn("Spółka Świat", width="medium"),
            "Surowiec": st.column_config.TextColumn("Surowiec", width="medium"),
            "Krypto": st.column_config.TextColumn("Krypto"),
            # 3. UKRYTE
            "Czy Usa": None,
            "Czy Świat": None,
            "Ticker Usa": None,
            "Ticker Świat": None,
            "Czy Streamer": None,
        }

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
            src=Frontend.img_to_bytes(img_path), message=message, height=height
        )

    def waiting_screen(self):
        self.page.markdown(
            Frontend.img_to_html("data/delord.gif", "ZASYSANIE DANYCH"),
            unsafe_allow_html=True,
        )

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

        if row["Czy Streamer"] == 1:
            style["Użytkownik"] = "background-color: yellow; color: black;"

        if row["Czy Usa"] == 0:
            style["Spółka Usa"] = "background-color: #FFF0F0; color: #884444;"
            style["Wynik Usa"] = "background-color: #FFF0F0; color: #884444;"

        if row["Czy Świat"] == 0:
            style["Spółka Świat"] = "background-color: #FFF0F0; color: #884444;"
            style["Wynik Świat"] = "background-color: #FFF0F0; color: #884444;"

        if row["Średnia Ważona"] < 0:
            style["Średnia Ważona"] = (
                "background-color: red; color: black; font-weight: bold"
            )
        elif 0 <= row["Średnia Ważona"] < benchmark:
            style["Średnia Ważona"] = (
                "background-color: orange; color: black; font-weight: bold"
            )
        else:
            style["Średnia Ważona"] = (
                "background-color: OliveDrab; color: black; font-weight: bold"
            )

        if row["Średnia Spółki"] < 0:
            style["Średnia Spółki"] = (
                "background-color: red; color: black; font-weight: bold"
            )
        elif 0 <= row["Średnia Spółki"] < benchmark:
            style["Średnia Spółki"] = (
                "background-color: orange; color: black; font-weight: bold"
            )
        else:
            style["Średnia Spółki"] = (
                "background-color: OliveDrab; color: black; font-weight: bold"
            )

        return style

    def run_frontend(self, ranking_2025, sp500_2025, ranking_2026, sp500_2026):
        self.page.empty()
        tab1, tab2, tab3 = st.tabs(["Disclaimer", "Ranking 2026", "Ranking 2025"])

        with tab1:
            st.markdown(self.__disclaimer, unsafe_allow_html=True)

        with tab2:
            st.set_page_config(page_title="Ranking giełdowy", layout="wide")
            st.title("📈 Ranking Giełdowy - Paweł Delord Szabla 2026")
            st.markdown(
                "<span style='font-size: 20px; color: red;'>**#bajka #zabawa #gra**</span>",
                unsafe_allow_html=True,
            )
            st.subheader("SP500 Benchmark")
            styler = Frontend.styler_2025(percent_column=["Wynik"])
            st.dataframe(
                styler(sp500_2026),
                hide_index=True,
                width="content",
                column_config={"Wynik": "Zmiana Procentowa"},
            )
            ranking_2026 = ranking_2026[
                [c for c in self.__cols if c in ranking_2026.columns]
            ]
            styled = ranking_2026.style.apply(
                Frontend.styler_2026,
                axis=1,
                benchmark=sp500_2026["Wynik"].iloc[0],
            ).format(
                {
                    c: "{:.2f}%"
                    for c in ranking_2026.select_dtypes(include=["number"]).columns
                },
                precision=2,
            )
            st.subheader("👥 Wybory Użytkowników")
            st.dataframe(styled, height="auto", column_config=self.__config)
            st.markdown(
                """
            <style>
                [data-testid="stElementToolbar"] {display: none !important;}
            </style>
            """,
                unsafe_allow_html=True,
            )
            st.markdown(
                "<span style='font-size: 10px; color: gray;'>Materiały i informacje przedstawione na niniejszej stronie internetowej zamieszczone są jedynie w celu informacyjnym. Nie stanowią one porady inwestycyjnej, nawet jeśli wyraźnie wskazują na spółkę lub papier wartościowy. Niniejsze informacje nie stanowią oferty inwestycyjnej, rekomendacji inwestycyjnej czy oferty świadczenia jakiejkolwiek usługi.</span>",
                unsafe_allow_html=True,
            )

        with tab3:
            st.set_page_config(page_title="Ranking giełdowy", layout="wide")
            st.title(
                "📈 Ranking Giełdowy - Paweł Delord Szabla 2025 - oficjalne wyniki bo koniec roku*"
            )
            st.markdown(
                "<span style='font-size: 20px; color: red;'>**#bajka #zabawa #gra**</span>",
                unsafe_allow_html=True,
            )
            st.subheader("SP500 Benchmark")
            styler = Frontend.styler_2025(percent_column=["Zmiana procentowa"])
            st.dataframe(styler(sp500_2025), hide_index=True, width="content")
            styler = Frontend.styler_2025(
                benchmark=sp500_2025.at[0, "Zmiana procentowa"],
                color_column="Średnia",
                percent_column=[
                    "Wynik spółka 1",
                    "Wynik spółka 2",
                    "Wynik spółka 3",
                    "Średnia",
                ],
            )
            st.subheader("👥 Wybory Użytkowników")
            st.dataframe(styler(ranking_2025), width="stretch", height="auto")
            st.markdown(
                "<span style='font-size: 10px; color: gray;'>Materiały i informacje przedstawione na niniejszej stronie internetowej zamieszczone są jedynie w celu informacyjnym. Nie stanowią one porady inwestycyjnej, nawet jeśli wyraźnie wskazują na spółkę lub papier wartościowy. Niniejsze informacje nie stanowią oferty inwestycyjnej, rekomendacji inwestycyjnej czy oferty świadczenia jakiejkolwiek usługi.</span>",
                unsafe_allow_html=True,
            )
