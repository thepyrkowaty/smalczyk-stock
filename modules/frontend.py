import streamlit as st
import pandas as pd
from modules.frontend_shit import Styler, FrontendHelpers, COLUMN_CONFIG, COLUMNS
from modules.llm import get_market_analysis


class Frontend:
    def __init__(self) -> None:
        st.set_page_config(page_title="Ranking giełdowy", layout="wide")

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

    def __render_ai_section(self, leader_row):
        st.subheader(f"👥 Analiza spółek lidera - {leader_row['Użytkownik']}")
        st.caption("Poniższe informacje wygenerowała darmowa wersja Gemini...")

        mapping = [
            ("Polska", "Spółka Polska"),
            ("USA", "Spółka Usa"),
            ("Świat", "Spółka Świat"),
        ]
        cols = st.columns(3)

        for i, (label, col_name) in enumerate(mapping):
            ticker = leader_row[col_name]
            with cols[i]:
                st.write(f"**{label}:** {ticker}")
                st.info(get_market_analysis(ticker))

    def __render_2025(self, df, sp500):
        st.title("📈 Ranking Giełdowy - 2025 - Wyniki końcowe")
        st.markdown(self.__bajka_zabawa_gra, unsafe_allow_html=True)

        st.subheader("SP500 Benchmark")
        st.dataframe(
            Styler.styler_2025(percent_column=["Zmiana procentowa"])(sp500),
            hide_index=True,
        )

        st.subheader("👥 Wybory Użytkowników")
        bench_2025 = sp500.at[0, "Zmiana procentowa"]
        styler_2025 = Styler.styler_2025(
            benchmark=bench_2025,
            color_column="Średnia",
            percent_column=[
                "Wynik spółka 1",
                "Wynik spółka 2",
                "Wynik spółka 3",
                "Średnia",
            ],
        )
        st.dataframe(styler_2025(df), width="stretch", height="auto")
        st.markdown(self.__disclaimer_caption, unsafe_allow_html=True)

    def __render_2026(self, df, sp500):
        st.title("📈 Ranking Giełdowy - Paweł Delord Szabla 2026")
        st.markdown(self.__bajka_zabawa_gra, unsafe_allow_html=True)

        st.subheader("SP500 Benchmark")
        bench_val = sp500["Wynik"].iloc[0]
        st.dataframe(
            Styler.styler_2025(percent_column=["Wynik"])(sp500),
            hide_index=True,
            width="content",
            column_config={"Wynik": "Zmiana Procentowa"},
        )

        st.subheader("👥 Wybory Użytkowników")
        cols_to_show = [c for c in COLUMNS if c in df.columns]
        df_display = df[cols_to_show].copy()

        df_display.index = range(1, len(df_display) + 1)
        df_display.index = pd.Index(df_display.index, name="Miejsce")

        styled_df = df_display.style.apply(
            Styler.styler_2026, axis=1, benchmark=bench_val
        ).format(
            {c: "{:.2f}%" for c in df_display.select_dtypes("number").columns},
            precision=2,
        )

        st.dataframe(styled_df, height="auto", column_config=COLUMN_CONFIG)

        self.__render_ai_section(df.iloc[0])

        st.markdown(self.__disable_toolbox, unsafe_allow_html=True)
        st.markdown(self.__disclaimer_caption, unsafe_allow_html=True)

    def run_frontend(self, ranking_2025, sp500_2025, ranking_2026, sp500_2026):
        self.page.empty()
        tab1, tab2, tab3 = st.tabs(["Disclaimer", "Ranking 2026", "Ranking 2025"])

        with tab1:
            st.markdown(self.__disclaimer, unsafe_allow_html=True)

        with tab2:
            self.__render_2026(ranking_2026, sp500_2026)

        with tab3:
            self.__render_2025(ranking_2025, sp500_2025)
