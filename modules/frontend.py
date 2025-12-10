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
    def benchmark_styler(benchmark, column):
        def color(val):
            if val >= benchmark:
                return "background-color: OliveDrab; color: black; font-weight: bold"
            else:
                return "background-color: red; color: black; font-weight: bold"
        def apply(df):
            colored = df.style.map(color, subset=[column])
            formatted = colored.format(precision=2)
            return formatted
        
        return apply
        

    def run_frontend(self, user_ranking, prices, sp500_benchmark):
        self.page.empty()
        st.set_page_config(page_title="Ranking giełdowy", layout="wide")
        st.title("📈 Ranking Giełdowy - Paweł Delord Szabla*")
        st.markdown("**Witaj w rankingu inwestycyjnym!**")
        st.markdown(
            "<span style='font-size: 18px; color: red;'>#bajka #zabawa #gra</span>",
            unsafe_allow_html=True,
        )
        st.subheader("SP500 Benchmark")
        st.dataframe(sp500_benchmark, hide_index=True, width='content')
        styler = Frontend.benchmark_styler(sp500_benchmark.at[0, 'Zmiana procentowa'], 'Średnia')
        st.subheader("👥 Wybory Użytkowników")
        st.dataframe(styler(user_ranking), width="stretch")
        # st.dataframe(user_ranking.style.applymap(color_val, subset=["Średnia"]), width="stretch")
        st.subheader("💰 Ceny Początkowe Spółek")
        st.dataframe(prices, width="stretch")
        st.markdown(
            "<span style='font-size: 10px; color: gray;'>*Materiały i informacje przedstawione na niniejszej stronie internetowej zamieszczone są jedynie w celu informacyjnym. Nie stanowią one porady inwestycyjnej, nawet jeśli wyraźnie wskazują na spółkę lub papier wartościowy. Niniejsze informacje nie stanowią oferty inwestycyjnej, rekomendacji inwestycyjnej czy oferty świadczenia jakiejkolwiek usługi.</span>",
            unsafe_allow_html=True,
        )
