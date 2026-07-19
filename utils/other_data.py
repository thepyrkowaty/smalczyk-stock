"""
Loader notowan z biznesradar.pl, przebudowany na architekture identyczna
z wersja yfinance (run_all / run_daily / check_if_up_to_date / argparse).

Roznice wzgledem oryginalnego "starego" skryptu biznesradar:
- dodano check_if_up_to_date() + get_target_day() (jak w yfinance)
- dodano fill_all_calendar_days() (wypelnia weekendy/dni bez sesji)
- dodano compute_ytd() liczone wzgledem ostatniej ceny z last_year_end
  (a nie na sztywno "2025"/"2026")
- brakujace kursy (spolka nie znaleziona / brak notowan z last_year_end)
  sa wypelniane ZEREM (0.0), zamiast None/ffill -> baza YTD dla takich
  tickerow to takze 0, co daje ytd_change = 0 dla calego zakresu
- dodano argparse: mode all|daily, --db, --last-year-end
- prefix tickerow w tabeli users: "NC:" (jak w starym skrypcie)

Wymagania: pip install requests beautifulsoup4 pandas
"""

import re
import time
import argparse
import sqlite3
from datetime import date, timedelta

import requests
import pandas as pd
from bs4 import BeautifulSoup

PREFIX = "NC:"
MAX_PAGES = 30
SLEEP_BETWEEN_PAGES = 0.5
SLEEP_BETWEEN_TICKERS = 1.0

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS stock_prices_other (
    ticker text not null,
    day text not null,
    close_price real,
    ytd_change real
)
"""

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}


# ---------------------------------------------------------------------------
# Tickery z bazy
# ---------------------------------------------------------------------------

def get_tickers_from_db(db_path, prefix=PREFIX):
    conn = sqlite3.connect(db_path)
    query = """SELECT ticker from stock_desc WHERE ticker like 'NC%'"""
    df = pd.read_sql_query(query, conn)
    conn.close()

    col = "ticker"
    df = df.dropna(subset=[col])
    df = df[df[col].astype(str).str.startswith(prefix)]
    tickers = df[col].astype(str).str.replace(prefix, "", regex=False).tolist()
    return list(set(tickers))


def get_target_day():
    return (date.today() - timedelta(days=1)).isoformat()


def check_if_up_to_date(conn, tickers, target_day, prefix=PREFIX):
    if not tickers:
        return True
    full_tickers = [prefix + t for t in tickers]
    q = f"""
        SELECT DISTINCT ticker FROM stock_prices_other
        WHERE day = ? AND ticker IN ({','.join('?' * len(full_tickers))})
    """
    existing = pd.read_sql_query(q, conn, params=[target_day] + full_tickers)["ticker"].tolist()
    missing = set(full_tickers) - set(existing)
    return len(missing) == 0


# ---------------------------------------------------------------------------
# Scraping biznesradar.pl (analog get_yf_history)
# ---------------------------------------------------------------------------

def parse_table(html: str) -> list[tuple[str, float]]:
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table")
    if table is None:
        return []

    rows = []
    for tr in table.find_all("tr"):
        cells = [td.get_text(strip=True) for td in tr.find_all("td")]
        if len(cells) < 5:
            continue
        date_str, _open, _max, _min, close_str = cells[:5]

        date_match = re.match(r"(\d{2})\.(\d{2})\.(\d{4})", date_str)
        if not date_match:
            continue
        dd, mm, yyyy = date_match.groups()
        iso_date = f"{yyyy}-{mm}-{dd}"

        close_val = close_str.replace(" ", "").replace(",", ".")
        try:
            close_price = float(close_val)
        except ValueError:
            continue

        rows.append((iso_date, close_price))

    return rows


def fetch_history(ticker: str, last_year_end: str, max_pages: int = MAX_PAGES) -> list[tuple[str, float]]:
    """Pobiera notowania danego tickera, przechodzac przez kolejne strony,
    dopoki nie natrafi na sesje z roku last_year_end (lub wczesniejszego)
    albo nie skoncza sie strony / limit max_pages.
    """
    cutoff_year = pd.Timestamp(last_year_end).year
    base_url = f"https://www.biznesradar.pl/notowania-historyczne/{ticker}"
    all_rows: dict[str, float] = {}
    session = requests.Session()

    for page in range(1, max_pages + 1):
        url = base_url if page == 1 else f"{base_url},{page}"
        try:
            resp = session.get(url, headers=HEADERS, timeout=15)
        except requests.RequestException as e:
            print(f"[{ticker}] Blad polaczenia na stronie {page}: {e}")
            break

        if resp.status_code != 200:
            print(f"[{ticker}] Strona {page}: HTTP {resp.status_code}, przerywam.")
            break

        page_rows = parse_table(resp.text)
        if not page_rows:
            print(f"[{ticker}] Strona {page}: brak danych, przerywam.")
            break

        new_count = 0
        for day, price in page_rows:
            if day not in all_rows:
                all_rows[day] = price
                new_count += 1

        print(f"[{ticker}] Strona {page}: {len(page_rows)} wierszy ({new_count} nowych).")

        if new_count == 0:
            print(f"[{ticker}] Brak nowych wierszy - koniec paginacji.")
            break

        if any(int(day[:4]) <= cutoff_year for day, _ in page_rows):
            print(f"[{ticker}] Znaleziono sesje z {cutoff_year} roku - koniec pobierania.")
            break

        time.sleep(SLEEP_BETWEEN_PAGES)

    return sorted(all_rows.items(), key=lambda r: r[0])


def get_biznesradar_history(tickers, last_year_end="2025-12-31", buffer_days=10,
                             end_date=None, sleep_s=SLEEP_BETWEEN_TICKERS):
    """Zwraca DataFrame [ticker, day, close_price] (z prefixem) dla wszystkich
    tickerow, w zakresie [last_year_end - buffer_days, end_date].
    Tickery bez danych / bez notowan z last_year_end dostaja close_price = 0.0
    na caly widoczny zakres dat (zamiast None).
    """
    unique_tickers = list(set(filter(None, tickers)))
    if not unique_tickers:
        return pd.DataFrame(columns=["ticker", "day", "close_price"])

    if end_date is None:
        end_date = (date.today() - timedelta(days=1)).isoformat()

    fetch_start = pd.Timestamp(last_year_end) - pd.Timedelta(days=buffer_days)
    end_ts = pd.Timestamp(end_date)
    cutoff = pd.Timestamp(last_year_end)

    all_rows = []
    failed_tickers = []

    for idx, ticker in enumerate(unique_tickers):
        print(f"\n=== Pobieranie {ticker} ({idx + 1}/{len(unique_tickers)}) ===")
        try:
            rows = fetch_history(ticker, last_year_end)
        except Exception as e:
            print(f"[{ticker}] BLAD: {e}")
            rows = []

        ok = False
        if rows:
            df_t = pd.DataFrame(rows, columns=["day", "close_price"])
            df_t["day_dt"] = pd.to_datetime(df_t["day"])
            df_t = df_t[(df_t["day_dt"] >= fetch_start) & (df_t["day_dt"] <= end_ts)]
            df_t = df_t.dropna(subset=["close_price"])
            # wymagamy przynajmniej jednej sesji <= cutoff, by miec baze YTD
            has_base = (df_t["day_dt"] <= cutoff).any()
            if not df_t.empty and has_base:
                df_t["ticker"] = ticker
                all_rows.append(df_t[["ticker", "day", "close_price"]])
                ok = True

        if not ok:
            print(f"[{ticker}] Brak wiarygodnych danych - wypelniam zerami.")
            failed_tickers.append(ticker)

        if idx < len(unique_tickers) - 1:
            time.sleep(sleep_s)

    if all_rows:
        result = pd.concat(all_rows, ignore_index=True)
    else:
        result = pd.DataFrame(columns=["ticker", "day", "close_price"])

    if failed_tickers:
        visible_range = pd.date_range(start=last_year_end, end=end_date, freq="D")
        placeholder = pd.DataFrame([
            {"ticker": t, "day": d.strftime("%Y-%m-%d"), "close_price": 0.0}
            for t in set(failed_tickers) for d in visible_range
        ])
        result = pd.concat([result, placeholder], ignore_index=True)

    result["ticker"] = PREFIX + result["ticker"].astype(str)

    return result[["ticker", "day", "close_price"]]


# ---------------------------------------------------------------------------
# Wypelnianie dni kalendarzowych + YTD
# ---------------------------------------------------------------------------

def fill_all_calendar_days(hist_df, last_year_end="2025-12-31", end_date=None):
    """Wypelnia dni bez sesji (weekendy/swieta) ostatnia znana cena (ffill).
    Jesli na starcie zakresu nie ma zadnej ceny (np. sam placeholder 0.0),
    brakujace wartosci na poczatku sa uzupelniane zerem.
    """
    if end_date is None:
        end_date = (date.today() - timedelta(days=1)).isoformat()

    df = hist_df.copy()
    df["day_dt"] = pd.to_datetime(df["day"])

    filled_frames = []
    for ticker, g in df.groupby("ticker"):
        g = g.sort_values("day_dt").set_index("day_dt")
        full_range = pd.date_range(start=g.index.min(), end=end_date, freq="D")
        g_full = g.reindex(full_range)
        g_full["close_price"] = g_full["close_price"].ffill().fillna(0.0)
        g_full["ticker"] = ticker
        g_full = g_full.reset_index().rename(columns={"index": "day_dt"})
        filled_frames.append(g_full)

    out = pd.concat(filled_frames, ignore_index=True)
    out["day"] = out["day_dt"].dt.strftime("%Y-%m-%d")
    return out[["ticker", "day", "close_price", "day_dt"]]


def compute_ytd(hist_df_full, last_year_end="2025-12-31"):
    """Liczy ytd_change wzgledem ostatniej ceny <= last_year_end.
    Jesli bazowa cena to 0 (brak danych), ytd_change = 0.0 (zamiast None/DZ0).
    """
    df = hist_df_full.copy()
    cutoff = pd.Timestamp(last_year_end)

    def ytd_for_group(g):
        g = g.sort_values("day_dt")
        base_rows = g[g["day_dt"] <= cutoff]
        base = base_rows.iloc[-1]["close_price"] if not base_rows.empty else 0.0
        if base is None or pd.isna(base):
            base = 0.0
        g = g.copy()
        if base == 0:
            g["ytd_change"] = 0.0
        else:
            g["ytd_change"] = ((g["close_price"] - base) / base * 100).round(2)
        return g

    out = df.groupby("ticker", group_keys=False).apply(ytd_for_group, include_groups=False)
    out["ticker"] = df["ticker"]
    out = out[out["day_dt"] >= cutoff]
    return out[["ticker", "day", "close_price", "ytd_change"]]


# ---------------------------------------------------------------------------
# Zapis
# ---------------------------------------------------------------------------

def save_to_stock_prices(conn, result_df, replace_existing=True):
    if result_df.empty:
        print("Brak rekordow do zapisu.")
        return
    if replace_existing:
        tickers = tuple(result_df["ticker"].unique())
        conn.execute(f"DELETE FROM stock_prices_other WHERE ticker IN ({','.join('?'*len(tickers))})", tickers)
    result_df = result_df.fillna(0.0)
    rows = list(result_df.itertuples(index=False, name=None))
    conn.executemany("""
        INSERT INTO stock_prices_other (ticker, day, close_price, ytd_change)
        VALUES (?, ?, ?, ?)
    """, rows)
    conn.commit()


# ---------------------------------------------------------------------------
# Orkiestracja
# ---------------------------------------------------------------------------

def run_all(db_path, last_year_end):
    tickers = get_tickers_from_db(db_path)
    if not tickers:
        print(f"Nie znaleziono tickerow z przedrostkiem {PREFIX}")
        return
    

    conn = sqlite3.connect(db_path)
    conn.execute(CREATE_TABLE_SQL)
    hist = get_biznesradar_history(tickers, last_year_end=last_year_end)

    if hist.empty:
        print("Brak danych z biznesradar.pl.")
        conn.close()
        return

    hist_filled = fill_all_calendar_days(hist, last_year_end=last_year_end)
    result = compute_ytd(hist_filled, last_year_end=last_year_end)
    save_to_stock_prices(conn, result)
    conn.close()
    print(f"Przeladowano cala historie dla {len(tickers)} tickerow.")


def run_daily(db_path, last_year_end):
    conn = sqlite3.connect(db_path)
    conn.execute(CREATE_TABLE_SQL)
    tickers = get_tickers_from_db(db_path)
    target_day = get_target_day()

    if check_if_up_to_date(conn, tickers, target_day):
        print(f"Dane za {target_day} juz sa w tabeli — pomijam.")
        conn.close()
        return

    print(f"Dociagam dane za {target_day}.")
    hist = get_biznesradar_history(tickers, last_year_end=last_year_end)

    if hist.empty:
        print("Brak danych z biznesradar.pl.")
        conn.close()
        return

    hist_filled = fill_all_calendar_days(hist, last_year_end=last_year_end)
    result = compute_ytd(hist_filled, last_year_end=last_year_end)
    save_to_stock_prices(conn, result)
    conn.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["all", "daily"],
                         help="all = pelny reload historii, daily = sprawdzenie/dopisanie ostatniego dnia")
    parser.add_argument("--db", default="/home/debian/data/bazarek.db")
    parser.add_argument("--last-year-end", default="2025-12-31")
    args = parser.parse_args()

    if args.mode == "all":
        run_all(args.db, args.last_year_end)
    else:
        run_daily(args.db, args.last_year_end)


if __name__ == "__main__":
    main()
