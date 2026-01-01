import streamlit as st
import base64
from pathlib import Path


class Frontend:
    def __init__(self) -> None:
        self.page = st.empty()

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

    def run_frontend(self, user_ranking, sp500_benchmark):
        self.page.empty()
        tab1, tab2 = st.tabs(["Ranking 2025", "Ranking 2026"])

        with tab1:
            st.set_page_config(page_title="Ranking giełdowy", layout="wide")
            st.title(
                "📈 Ranking Giełdowy - Paweł Delord Szabla 2025 - oficjalne wyniki bo koniec roku*"
            )
            st.markdown(
                "<span style='font-size: 20px; color: red;'>**#bajka #zabawa #gra**</span>",
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
            st.dataframe(styler(user_ranking), width="stretch", height=560)
            st.markdown(
                "<span style='font-size: 10px; color: gray;'>*Materiały i informacje przedstawione na niniejszej stronie internetowej zamieszczone są jedynie w celu informacyjnym. Nie stanowią one porady inwestycyjnej, nawet jeśli wyraźnie wskazują na spółkę lub papier wartościowy. Niniejsze informacje nie stanowią oferty inwestycyjnej, rekomendacji inwestycyjnej czy oferty świadczenia jakiejkolwiek usługi.</span>",
                unsafe_allow_html=True,
            )
        with tab2:
            st.title(
                "Pomóż mi w moim projekcie edukacyjnym i wypełnij ankietę w forms dostępną na Discord @delordione w przypiętej wiadomości lub na czacie na Kicku."
            )
            st.markdown(
                "<span style='font-size: 20px; color: red;'>**#bajka #zabawa #gra**</span>",
                unsafe_allow_html=True,
            )
            st.markdown(
                "<span style='font-size: 20px; color: green;'>**ŻYCZE ZDRÓWKA I DUŻO SZCZĘŚCIA W 2026 ROKU**</span>",
                unsafe_allow_html=True,
            )
            st.markdown(
                Frontend.img_to_html("data/love.gif", "BUZIAKI", "20vh"),
                unsafe_allow_html=True,
            )

            disclaimer = """
                ***NOTYFIKACJA ORAZ ZASTRZEŻENIA PRAWNE***
                
                NINIEJSZA PLATFORMA MA CHARAKTER WYŁĄCZNIE EDUKACYJNY, DYDAKTYCZNY ORAZ NAUKOWO-BADAWCZY. 
                Wszelkie treści, dane, wykresy, analizy oraz kody źródłowe prezentowane w obrębie niniejszej witryny zostały wygenerowane i udostępnione w jednym, nadrzędnym celu: nauki obsługi struktur danych, testowania algorytmów przetwarzania informacji oraz doskonalenia umiejętności programistycznych w zakresie tworzenia nowoczesnych interfejsów webowych. 
                
                **To nie jest porada inwestycyjna:** Żadna informacja, słowo, liczba, kropka czy przecinek znajdujący się na tej stronie nie stanowi, nie zastępuje i nie może być interpretowany jako rekomendacja inwestycyjna, porada finansowa, oferta kupna lub sprzedaży jakichkolwiek instrumentów finansowych w rozumieniu Rozporządzenia Parlamentu Europejskiego i Rady (UE) nr 596/2014 oraz innych właściwych przepisów prawa finansowego. 
                
                **Prezentacja faktów historycznych:** Serwis służy wyłącznie do wizualizacji realnych, historycznych zmian kursów spółek giełdowych. Prezentujemy surowe fakty rynkowe, które miały miejsce w przeszłości. Pamiętaj: wyniki osiągnięte w przeszłości nie stanowią żadnej gwarancji ani obietnicy zysków w przyszłości. 
                
                **Brak odpowiedzialności:** Twórcy witryny nie ponoszą żadnej odpowiedzialności (cywilnej, karnej ani moralnej) za jakiekolwiek decyzje finansowe, straty, szkody (bezpośrednie lub wtórne) wynikające z interpretacji danych zawartych w serwisie. Inwestowanie na rynkach kapitałowych wiąże się z wysokim ryzykiem utraty całości kapitału. 
                
                **Charakter symulacyjny:** Elementy interaktywne są formą ćwiczenia z zakresu Data Science i Frontend Developmentu. Wykorzystanie ich do jakichkolwiek celów komercyjnych lub spekulacyjnych odbywa się na wyłączną odpowiedzialność użytkownika. 
                
                **Pamiętaj o własnym rozumie:** Zanim podejmiesz jakąkolwiek decyzję finansową, skonsultuj się z licencjonowanym doradcą inwestycyjnym. My tutaj tylko uczymy się, jak sprawić, żeby wykres wyglądał ładnie w Pythonie i HTML-u. 

                ---
                *KORZYSTAJĄC Z TEJ STRONY, POTWIERDZASZ, ŻE ROZUMIESZ POWYŻSZE ZASTRZEŻENIA I AKCEPTUJESZ FAKT, ŻE JEST TO PLAC ZABAW DLA PROGRAMISTY, A NIE TERMINAL BLOOMBERGA.*
            """

            st.caption(disclaimer)

            st.caption(
                "Same picki tutaj pojawią się najpewniej dopiero po zakończeniu zbierania, potem będę musiał poczyścić dane śmieszków co wyzywają Pawła od smalczyków i rzeczników Tuska i odpalimy."
            )
