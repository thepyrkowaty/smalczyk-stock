import streamlit as st
import pandas as pd
from modules.frontend_shit import Styler, FrontendHelpers, COLUMN_CONFIG, COLUMNS
from modules.llm import get_market_analysis


class Frontend:
    def __init__(self) -> None:
        self.page = st.empty()
        with open("data/disclaimer.html", "r", encoding="utf-8") as f:
            self.__disclaimer = f.read()

        self.__disclaimer_caption = "<span style='font-size: 10px; color: gray;'>Materiały i informacje przedstawione na niniejszej stronie internetowej zamieszczone są jedynie w celu informacyjnym. Nie stanowią one porady inwestycyjnej, nawet jeśli wyraźnie wskazują na spółkę lub papier wartościowy. Niniejsze informacje nie stanowią oferty inwestycyjnej, rekomendacji inwestycyjnej czy oferty świadczenia jakiejkolwiek usługi.</span>"
        self.__bajka_zabawa_gra = (
            "<span style='font-size: 20px; color: red;'>**#bajka #zabawa #gra**</span>"
        )
        self.__disable_toolbox = """
            <style>
                [data-testid="stElementToolbar"] {display: none !important;}
            </style>
        """

    def waiting_screen(self):
        self.page.markdown(
            FrontendHelpers.img_to_html("data/delord.gif", "ZASYSANIE DANYCH"),
            unsafe_allow_html=True,
        )

    def run_frontend(self, ranking_2025, sp500_2025, ranking_2026, sp500_2026):
        self.page.empty()
        tab1, tab2, tab3 = st.tabs(["Disclaimer", "Ranking 2026", "Ranking 2025"])

        with tab1:
            st.markdown(self.__disclaimer, unsafe_allow_html=True)

        with tab2:
            st.set_page_config(page_title="Ranking giełdowy", layout="wide")
            st.title("📈 Ranking Giełdowy - Paweł Delord Szabla 2026")
            st.markdown(
                self.__bajka_zabawa_gra,
                unsafe_allow_html=True,
            )
            st.subheader("SP500 Benchmark")
            styler = Styler.styler_2025(percent_column=["Wynik"])
            st.dataframe(
                styler(sp500_2026),
                hide_index=True,
                width="content",
                column_config={"Wynik": "Zmiana Procentowa"},
            )
            ranking_2026 = ranking_2026[
                [c for c in COLUMNS if c in ranking_2026.columns]
            ]
            styled = ranking_2026.style.apply(
                Styler.styler_2026,
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
            st.dataframe(styled, height="auto", column_config=COLUMN_CONFIG)
            leader, pl, usa, world = ranking_2026.iloc[0][
                ["Użytkownik", "Spółka Polska", "Spółka Usa", "Spółka Świat"]
            ]
            st.subheader(f"👥 Analiza spółek lidera - {leader}")
            st.caption(
                "Poniższe informacje wygenerowała darmowa wersja Gemini - Nie traktuj ich jako rekomendacji ani porady inwestycyjnej bo model może gadać głupoty wyssane z palca."
            )
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write(f"**Polska:** {pl}")
                st.info(get_market_analysis(pl))
            with col2:
                st.write(f"**USA:** {usa}")
                st.info(get_market_analysis(usa))
            with col3:
                st.write(f"**Świat:** {world}")
                st.info(get_market_analysis(world))
            st.markdown(self.__disable_toolbox, unsafe_allow_html=True)
            st.markdown(self.__disclaimer_caption, unsafe_allow_html=True)

        with tab3:
            st.set_page_config(page_title="Ranking giełdowy", layout="wide")
            st.title(
                "📈 Ranking Giełdowy - Paweł Delord Szabla 2025 - oficjalne wyniki bo koniec roku*"
            )
            st.markdown(
                self.__bajka_zabawa_gra,
                unsafe_allow_html=True,
            )
            st.subheader("SP500 Benchmark")
            styler = Styler.styler_2025(percent_column=["Zmiana procentowa"])
            st.dataframe(styler(sp500_2025), hide_index=True, width="content")
            styler = Styler.styler_2025(
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
                self.__disclaimer_caption,
                unsafe_allow_html=True,
            )
