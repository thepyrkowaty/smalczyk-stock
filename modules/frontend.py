import streamlit as st
import pandas as pd
from modules.frontend_shit import *
from modules.llm import get_market_analysis
from modules.frontend_helpers import *


class Frontend:
    def __init__(self) -> None:
        st.set_page_config(page_title="Ranking giełdowy", layout="wide")

        self.page = st.empty()
        with open("data/disclaimer.html", "r", encoding="utf-8") as f:
            self.__disclaimer = f.read()

    def waiting_screen(self):
        self.page.markdown(
            FrontendHelpers.img_to_html("data/delord.gif", "ZASYSANIE DANYCH"),
            unsafe_allow_html=True,
        )
    def _check_easter_egg_date(self):
        selected_day = st.session_state.comparison_day

        if str(selected_day) == "2026-07-12" and not st.session_state.easter_egg_seen:
            st.session_state.show_easter_egg_video = True
            st.session_state.easter_egg_seen = True
    
    def _show_easter_egg_dialog(self):
        @st.dialog(
            "🎯 JAKI TO JEST KOCUR 🎯",
            width="large",
            dismissible=False,
        )
        def show_dialog():
            st.video("data/other/rataj.mp4", format="video/mp4")

            if st.button("Zamknij", use_container_width=True):
                st.session_state.show_easter_egg_video = False
                st.rerun()

        show_dialog()

    def _init_state(self):
        if "show_disclaimer_video" not in st.session_state:
            st.session_state.show_disclaimer_video = True

        if "menu" not in st.session_state:
            st.session_state.menu = "Disclaimer"

        if "show_easter_egg_video" not in st.session_state:
            st.session_state.show_easter_egg_video = False

        if "easter_egg_seen" not in st.session_state:
            st.session_state.easter_egg_seen = False

    def _set_menu(self, menu_name):
        st.session_state.menu = menu_name


    def _render_sidebar(self):
        with st.sidebar:
            st.markdown("### Menu")

            st.button(
                "📈 Ranking 2026",
                key="nav_2026",
                use_container_width=True,
                type="primary" if st.session_state.menu == "Ranking 2026" else "secondary",
                on_click=self._set_menu,
                args=("Ranking 2026",),
            )

            st.button(
                "🏆 Ranking 2025",
                key="nav_2025",
                use_container_width=True,
                type="primary" if st.session_state.menu == "Ranking 2025" else "secondary",
                on_click=self._set_menu,
                args=("Ranking 2025",),
            )

            st.button(
                "📄 Disclaimer",
                key="nav_disclaimer",
                use_container_width=True,
                type="primary" if st.session_state.menu == "Disclaimer" else "secondary",
                on_click=self._set_menu,
                args=("Disclaimer",),
            )

        return st.session_state.menu

    def _show_video_dialog(self):
        @st.dialog("Disclaimer", width="large",dismissible=False)
        def show_video_dialog():
            st.video("data/other/disclaimer.mp4", format="video/mp4")
            if st.button("Zamknij"):
                st.session_state.show_disclaimer_video = False
                st.rerun()

        show_video_dialog()

    def _render_disclaimer_page(self):
        if st.session_state.show_disclaimer_video:
            self._show_video_dialog()

        st.markdown(self.__disclaimer, unsafe_allow_html=True)

    def __render_ai_section(self, leader_row):
        st.subheader(f"👥 Analiza spółek lidera - {leader_row['Użytkownik']}")
        st.caption(
            "Poniższe informacje wygenerowała darmowa wersja Gemini - Nie traktuj ich jako rekomendacji ani porady inwestycyjnej bo model może gadać głupoty wyssane z palca."
        )

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
        st.title("Ranking Giełdowy - 2025 - Wyniki końcowe")
        st.markdown(BAJKA_ZABAWA_GRA, unsafe_allow_html=True)

        st.subheader("SP500 Benchmark")
        st.dataframe(
            Styler.styler_2025(percent_column=["ytd_change"])(sp500),
            hide_index=True,
            width="content",
            column_config={"ytd_change": "Zmiana Procentowa"},
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
        st.markdown(DISCLAIMER_CAPTION, unsafe_allow_html=True)

    def __render_ranking(self, df, sp500, day):
        st.subheader("SP500 Benchmark")
        bench_val = sp500[sp500["day"] == day]

        st.dataframe(
            Styler.styler_2025(percent_column=["ytd_change"])(bench_val),
            hide_index=True,
            width="content",
            column_config={"ytd_change": "Zmiana Procentowa"},
        )

        st.subheader("👥 Wybory Użytkowników")
        cols_to_show = [c for c in COLUMNS if c in df.columns]
        df_display = df[cols_to_show].copy()
        df_display["Miejsce"] = df_display["Miejsce"].astype(str)

        styled_df = df_display.style.apply(
            Styler.styler_2026, axis=1, sp500_df=sp500, day=day
        ).format(
            {c: "{:.2f}%" for c in df_display.select_dtypes("number").columns},
            precision=2,
        )

        st.dataframe(
            styled_df,
            height="auto",
            column_config=COLUMN_CONFIG,
            hide_index=True,
        )

    def __render_2026(self, df, sp500, day):
        st.title("Ranking Giełdowy - Paweł Delord Szabla 2026")
        st.markdown(BAJKA_ZABAWA_GRA, unsafe_allow_html=True)
        self.__render_ranking(df, sp500, day)
        self.__render_ai_section(df.iloc[0])
        st.markdown(DISABLE_TOOLBOX, unsafe_allow_html=True)
        st.markdown(DISCLAIMER_CAPTION, unsafe_allow_html=True)

    def _render_2026_comparison_tab(self, ranking_all, sp500_all):
        ranking_all_prepared = prepare_ranking_all(ranking_all)

        available_days = get_available_days(ranking_all_prepared)
        selected_day = st.selectbox(
            "Wybierz dzień",
            options=available_days,
            index=0,
            key="comparison_day",
        )

        if str(selected_day) == "2026-07-12":
            if st.session_state.last_easter_egg_day != "2026-07-12":
                st.session_state.show_easter_egg_video = True
                st.session_state.last_easter_egg_day = "2026-07-12"
        else:
            st.session_state.last_easter_egg_day = str(selected_day)

        df_day = get_day_ranking(ranking_all_prepared, selected_day)
        self.__render_ranking(df_day, sp500_all, str(selected_day))

        st.divider()

        available_users = get_available_users(ranking_all_prepared)
        streamers = get_streamers(ranking_all_prepared)

        selected_users = st.multiselect(
            "Wybierz osoby do porównania",
            options=available_users,
            default=streamers,
            max_selections=15,
        )

        df_chart = get_chart_df(ranking_all_prepared, selected_users)
        fig = build_user_comparison_chart(df_chart, sp500_all)
        st.plotly_chart(fig, width="stretch")

        if st.session_state.show_easter_egg_video:
            self._show_easter_egg_dialog()

    def run_frontend(
        self,
        ranking_2025,
        sp500_2025,
        ranking_2026,
        ranking_all,
        sp500_all,
    ):
        self.page.empty()
        self._init_state()
        menu = self._render_sidebar()

        if menu == "Disclaimer":
            self._render_disclaimer_page()

        elif menu == "Ranking 2026":
            tab1, tab2 = st.tabs(["Ranking", "Porównania"])

            with tab1:
                self.__render_2026(
                    ranking_2026,
                    sp500_all,
                    sp500_all["day"].max(),
                )

            with tab2:
                self._render_2026_comparison_tab(ranking_all, sp500_all)

        elif menu == "Ranking 2025":
            self.__render_2025(ranking_2025, sp500_2025)