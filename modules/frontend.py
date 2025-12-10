import streamlit as st
import base64
from pathlib import Path


class Frontend:
    def __init__(self) -> None:
        self.page = st.empty()

    def waiting_screen(self):
        def img_to_bytes(img_path):
            img_bytes = Path(img_path).read_bytes()
            encoded = base64.b64encode(img_bytes).decode()
            return encoded

        def img_to_html(img_path):
            return """
            <div style="
                height:80vh;
                display:flex;
                flex-direction:column;
                justify-content:center;
                align-items:center;
                text-align:center;
            ">
            <img src="data:image/png;base64,{src}" class="img-fluid" style="width:124px; margin-bottom:10px;" />
            <div style="font-size:36px; font-weight:800; letter-spacing:4px;">
                ZASYSANIE DANYCH
            </div>
            </div>
            """.format(
                src=img_to_bytes(img_path)
            )

        self.page.markdown(img_to_html("data/delord.gif"), unsafe_allow_html=True)

    @staticmethod
    def df_styler(benchmark=None, color_column=None, percent_column=None):
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

    def run_frontend(self, user_ranking, prices, sp500_benchmark):
        self.page.empty()
        st.set_page_config(page_title="Ranking giełdowy", layout="wide")
        st.title("📈 Ranking Giełdowy - Paweł Delord Szabla 2025*")
        st.markdown("**Witaj w rankingu inwestycyjnym!**")
        st.markdown(
            "<span style='font-size: 18px; color: red;'>#bajka #zabawa #gra</span>",
            unsafe_allow_html=True,
        )
        st.subheader("SP500 Benchmark")
        styler = Frontend.df_styler(percent_column=["Zmiana procentowa"])
        st.dataframe(styler(sp500_benchmark), hide_index=True, width="content")
        styler = Frontend.df_styler(
            benchmark=sp500_benchmark.at[0, "Zmiana procentowa"],
            color_column="Średnia",
            percent_column=[
                "Wynik spółka 1",
                "Wynik spółka 2",
                "Wynik spółka 3",
                "Średnia",
            ],
        )
        st.subheader("👥 Wybory Użytkowników")
        st.dataframe(styler(user_ranking), width="stretch")
        st.subheader("💰 Kursy Początkowe Spółek")
        styler = Frontend.df_styler(percent_column=["Zmiana procentowa"])
        st.dataframe(styler(prices), width="stretch")
        st.markdown(
            "<span style='font-size: 10px; color: gray;'>*Materiały i informacje przedstawione na niniejszej stronie internetowej zamieszczone są jedynie w celu informacyjnym. Nie stanowią one porady inwestycyjnej, nawet jeśli wyraźnie wskazują na spółkę lub papier wartościowy. Niniejsze informacje nie stanowią oferty inwestycyjnej, rekomendacji inwestycyjnej czy oferty świadczenia jakiejkolwiek usługi.</span>",
            unsafe_allow_html=True,
        )
