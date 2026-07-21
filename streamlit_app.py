import pandas as pd
from modules.helpers import (
    Static2025Data,
    XTBData,
    Database
)
from modules.frontend import Frontend
import sqlite3

import streamlit as st

frontend = Frontend()

@st.cache_data(show_spinner=False, ttl=14400)
def load_data():
    conn = sqlite3.connect(r"data/bazarek.db")

    ranking_2025, sp500_2025 = Static2025Data.get_2025_data()
    database = Database()

    ranking_2026 = database.get_ranking(conn)
    ranking_all = database.get_ranking_all(conn)
    sp500_2026 = database.get_benchmark(conn)
    sp500_all = database.get_benchmark_all(conn)
    # xtb_data = XTBData().get_xtb_data()

    conn.close()

    return ranking_2025, sp500_2025, ranking_2026, sp500_2026, ranking_all, sp500_all

if "initial_loading_done" not in st.session_state:
    frontend.waiting_screen()
    data = load_data()
    st.session_state.initial_loading_done = True
else:
    data = load_data()

ranking_2025, sp500_2025, ranking_2026, sp500_2026, ranking_all, sp500_all = data

frontend.run_frontend(
    ranking_2025, sp500_2025,
    ranking_2026,
    ranking_all, sp500_all
)