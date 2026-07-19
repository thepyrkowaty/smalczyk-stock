import pandas as pd
import streamlit as st
import requests
import io

class Static2025Data:
    @staticmethod
    @st.cache_data()
    def get_2025_data():
        ranking = pd.read_csv(r"data/2025/2025.csv", index_col=[0])
        sp500_benchmark = pd.read_csv(r"data/2025/sp500.csv")
        return ranking, sp500_benchmark


class XTBData:
    @staticmethod
    @st.cache_data(ttl=86400)
    def get_xtb_data():
        url = "https://api.github.com/repos/thepyrkowaty/XTB-DATA/contents/demo.csv?ref=main"
        token = ""

        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github.v3.raw"
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            df = pd.read_csv(io.StringIO(response.text), sep=";", thousands=',')
            df = df.rename(columns={"accountid_account": "Użytkownik", "total_trades": "Liczba transakcji", "net_result": "Wartość Konta"})
            df["Stopa zwrotu"] = (df["Wartość Konta"] - 100_000)/100_000
            return df
        else:
            st.error(f"Błąd pobierania pliku: {response.status_code}")
            return 
        
class Database:
    @staticmethod
    @st.cache_data(ttl=14400)    
    def get_ranking(_conn):
        query = f"""SELECT * FROM current_ranking"""
        result = pd.read_sql_query(query, _conn)
        return result
    
    @staticmethod
    @st.cache_data(ttl=14400)
    def get_benchmark(_conn):
        query = f"""SELECT 'SP500' as Benchmark, ytd_change FROM stock_latest_ytd WHERE ticker = 'YAHOO:^GSPC'"""
        result = pd.read_sql_query(query, _conn)
        return result
    
    @staticmethod
    @st.cache_data(ttl=14400)    
    def get_benchmark_all(_conn):
        query = f"""SELECT day, ytd_change FROM stock_prices WHERE ticker = 'YAHOO:^GSPC'"""
        result = pd.read_sql_query(query, _conn)
        return result

    @staticmethod
    @st.cache_data(ttl=14400)    
    def get_ranking_all(_conn):
        query = f"""SELECT * FROM ranking"""
        result = pd.read_sql_query(query, _conn)
        return result

