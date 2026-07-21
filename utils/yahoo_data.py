import yfinance as yf
import pandas as pd
import sqlite3
import time
import argparse
from datetime import date, timedelta


def get_tickers_from_db(db_path, prefix="YAHOO:"):
    conn = sqlite3.connect(db_path)
    query = """SELECT ticker from stock_desc WHERE ticker like 'YAHOO%'"""
    df = pd.read_sql_query(query, conn)
    conn.close()

    col = "ticker"
    df = df.dropna(subset=[col])
    df = df[df[col].astype(str).str.startswith(prefix)]
    tickers = df[col].astype(str).str.replace(prefix, "", regex=False).tolist()
    return list(set(tickers))


def get_target_day():
    return (date.today() - timedelta(days=1)).isoformat()


def check_if_up_to_date(conn, tickers, target_day, prefix="YAHOO:"):
    if not tickers:
        return True
    full_tickers = [prefix + t for t in tickers]
    q = f"""
        SELECT DISTINCT ticker FROM stock_prices
        WHERE day = ? AND ticker IN ({','.join('?' * len(full_tickers))})
    """
    existing = pd.read_sql_query(q, conn, params=[target_day] + full_tickers)["ticker"].tolist()
    missing = set(full_tickers) - set(existing)
    return len(missing) == 0


def get_yf_history(tickers, last_year_end="2025-12-31", buffer_days=10, end_date=None, batch_size=100, sleep_s=1):
    unique_tickers = list(set(filter(None, tickers)))
    if not unique_tickers:
        return pd.DataFrame(columns=["ticker", "day", "close_price"])

    if end_date is None:
        end_date = (date.today() - timedelta(days=1)).isoformat()

    fetch_start = (pd.Timestamp(last_year_end) - pd.Timedelta(days=buffer_days)).strftime("%Y-%m-%d")

    batches = [unique_tickers[i:i + batch_size] for i in range(0, len(unique_tickers), batch_size)]
    all_rows = []
    failed_tickers = []

    for idx, batch in enumerate(batches):
        try:
            data = yf.download(
                tickers=batch,
                start=fetch_start,
                end=(pd.Timestamp(end_date) + pd.Timedelta(days=1)).strftime("%Y-%m-%d"),
                interval="1d",
                progress=False,
                auto_adjust=True,
                timeout=30,
                threads=True,
            )
        except Exception as e:
            print(f"Błąd pobierania batcha {idx}: {e}")
            failed_tickers.extend(batch)
            continue

        if data is None or data.empty:
            failed_tickers.extend(batch)
            if idx < len(batches) - 1:
                time.sleep(sleep_s)
            continue

        close = data["Close"]
        if isinstance(close, pd.Series):
            close = close.to_frame(name=batch[0])
        close = close.sort_index()

        fetched_tickers = [t for t in close.columns if close[t].notna().any()]
        missing_in_batch = [t for t in batch if t not in fetched_tickers]
        failed_tickers.extend(missing_in_batch)

        long_df = close[fetched_tickers].reset_index().melt(
            id_vars=close.index.name or "Date",
            var_name="ticker", value_name="close_price"
        )
        long_df = long_df.rename(columns={long_df.columns[0]: "day"})
        long_df = long_df.dropna(subset=["close_price"])
        long_df["day"] = long_df["day"].astype(str)
        all_rows.append(long_df)

        if idx < len(batches) - 1:
            time.sleep(sleep_s)

    if all_rows:
        result = pd.concat(all_rows, ignore_index=True)
    else:
        result = pd.DataFrame(columns=["ticker", "day", "close_price"])

    if failed_tickers:
        visible_range = pd.date_range(start=last_year_end, end=end_date, freq="D")
        placeholder = pd.DataFrame([
            {"ticker": t, "day": d.strftime("%Y-%m-%d"), "close_price": None}
            for t in set(failed_tickers) for d in visible_range
        ])
        result = pd.concat([result, placeholder], ignore_index=True)

    result["ticker"] = "YAHOO:" + result["ticker"].astype(str)

    CUTOFF_DATE = pd.Timestamp("2026-04-01")

    for tk, adj in [("YAHOO:CRI.WA", 220), ("YAHOO:SNT.WA", 44)]:
        mask = (result["ticker"] == tk) & (pd.to_datetime(result["day"]) >= CUTOFF_DATE)
        result.loc[mask, "close_price"] = result.loc[mask, "close_price"] + adj

    return result[["ticker", "day", "close_price"]]


def fill_all_calendar_days(hist_df, last_year_end="2025-12-31", end_date=None):
    if end_date is None:
        end_date = (date.today() - timedelta(days=1)).isoformat()

    df = hist_df.copy()
    df["day_dt"] = pd.to_datetime(df["day"])

    filled_frames = []
    for ticker, g in df.groupby("ticker"):
        g = g.sort_values("day_dt").set_index("day_dt")
        full_range = pd.date_range(start=g.index.min(), end=end_date, freq="D")
        g_full = g.reindex(full_range)
        g_full["close_price"] = g_full["close_price"].ffill()
        g_full["ticker"] = ticker
        g_full = g_full.reset_index().rename(columns={"index": "day_dt"})
        filled_frames.append(g_full)

    out = pd.concat(filled_frames, ignore_index=True)
    out["day"] = out["day_dt"].dt.strftime("%Y-%m-%d")
    return out[["ticker", "day", "close_price", "day_dt"]]


def compute_ytd(hist_df_full, last_year_end="2025-12-31"):
    df = hist_df_full.copy()
    cutoff = pd.Timestamp(last_year_end)

    def ytd_for_group(g):
        g = g.sort_values("day_dt")
        base_rows = g[g["day_dt"] <= cutoff]
        base = base_rows.iloc[-1]["close_price"] if not base_rows.empty else None
        g = g.copy()
        if base is None or pd.isna(base):
            g["ytd_change"] = None
        else:
            g["ytd_change"] = ((g["close_price"] - base) / base * 100).round(2)
        return g

    out = df.groupby("ticker", group_keys=False).apply(ytd_for_group, include_groups=False)
    out["ticker"] = df["ticker"]
    out = out[out["day_dt"] >= cutoff]
    return out[["ticker", "day", "close_price", "ytd_change"]]


def save_to_stock_prices(conn, result_df, replace_existing=True):
    if replace_existing:
        tickers = tuple(result_df["ticker"].unique())
        conn.execute(f"DELETE FROM stock_prices WHERE ticker IN ({','.join('?'*len(tickers))})", tickers)
    result_df = result_df.where(pd.notnull(result_df), None)
    rows = list(result_df.itertuples(index=False, name=None))
    conn.executemany("""
        INSERT INTO stock_prices (ticker, day, close_price, ytd_change)
        VALUES (?, ?, ?, ?)
    """, rows)
    conn.commit()


def run_all(db_path, last_year_end):
    """Przeładowuje CAŁĄ historię od last_year_end do wczoraj dla wszystkich tickerów."""
    tickers = get_tickers_from_db(db_path)
    if not tickers:
        print("Nie znaleziono tickerów z przedrostkiem YAHOO:")
        return

    conn = sqlite3.connect(db_path)
    hist = get_yf_history(tickers, last_year_end=last_year_end)

    if hist.empty:
        print("Brak danych z yfinance.")
        conn.close()
        return

    hist_filled = fill_all_calendar_days(hist, last_year_end=last_year_end)
    result = compute_ytd(hist_filled, last_year_end=last_year_end)
    save_to_stock_prices(conn, result)
    conn.close()
    print(f"Przeładowano całą historię dla {len(tickers)} tickerów.")


def run_daily(db_path, last_year_end):
    """Sprawdza, czy jest wpis za wczoraj; jeśli nie, dociąga i dopisuje dane."""
    conn = sqlite3.connect(db_path)
    tickers = get_tickers_from_db(db_path)
    target_day = get_target_day()

    if check_if_up_to_date(conn, tickers, target_day):
        print(f"Dane za {target_day} już są w tabeli — pomijam.")
        conn.close()
        return

    print(f"Dociągam dane za {target_day}.")
    hist = get_yf_history(tickers, last_year_end=last_year_end)

    if hist.empty:
        print("Brak danych z yfinance.")
        conn.close()
        return

    hist_filled = fill_all_calendar_days(hist, last_year_end=last_year_end)
    result = compute_ytd(hist_filled, last_year_end=last_year_end)
    save_to_stock_prices(conn, result)
    conn.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["all", "daily"],
                         help="all = pełny reload historii, daily = sprawdzenie/dopisanie ostatniego dnia")
    parser.add_argument("--db", default="/home/debian/smalczyk-stock/data/bazarek.db")
    parser.add_argument("--last-year-end", default="2025-12-31")
    args = parser.parse_args()

    if args.mode == "all":
        run_all(args.db, args.last_year_end)
    else:
        run_daily(args.db, args.last_year_end)


if __name__ == "__main__":
    main()