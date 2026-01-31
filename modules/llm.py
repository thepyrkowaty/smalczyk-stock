import streamlit as st
from google import genai
from google.genai import types

# client = genai.Client(api_key=st.secrets["API_KEY"])
client = genai.Client(api_key="Xdd")


@st.cache_data(ttl=28800)
def get_market_analysis(company):
    try:
        search_tool = types.Tool(google_search=types.GoogleSearch())

        prompt = f"""
            Działaj jako profesjonalny analityk giełdowy. Korzystając z funkcji Google Search, przeanalizuj spółkę {company}.
            Twoja odpowiedź MUSI ściśle przestrzegać poniższej struktury formatowania Markdown:

            **Model biznesowy {company}:**
            [Tutaj wstaw dwa precyzyjne zdania o modelu biznesowym i głównych źródłach przychodów]

            **Wydarzenia wpływające na zmienność kursu w ostatnich 7 dniach:**
            [Tutaj wstaw trzy zwięzłe zdania o konkretnych wydarzeniach, liczbach (zmiany %, kursy) i datach z ostatniego tygodnia. Jeśli brak ważnych newsów, wyraźnie to zaznacz, podając ostatnią znaną cenę akcji lub rekomendację]

            Zasady: Unikaj ogólników typu 'spółka cieszy się zainteresowaniem'. Skup się wyłącznie na twardych danych i faktach.
    """

        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=prompt,
            config=types.GenerateContentConfig(tools=[search_tool], temperature=0.2),
        )
        if response.text:
            return response.text
        else:
            return "Nie udało się wygenerować analizy. Spróbuj ponownie później."
    except:
        return "⚠️ Chwilowy brak danych analitycznych dla tej spółki."
