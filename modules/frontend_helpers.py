import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def prepare_ranking_all(ranking_all: pd.DataFrame) -> pd.DataFrame:
    df = ranking_all.copy()
    df["Dzień"] = pd.to_datetime(df["Dzień"]).dt.date
    df = df.sort_values(["Użytkownik", "Dzień"])

    df["_sort"] = df["Miejsce"]
    df["_prev"] = df.groupby("Użytkownik")["_sort"].shift(1)
    df["_delta"] = df["_prev"] - df["_sort"]

    df["Miejsce"] = df.apply(
        lambda r: (
            str(int(r["_sort"])) if pd.isna(r["_delta"])
            else f'{int(r["_sort"])} (=)' if r["_delta"] == 0
            else f'{int(r["_sort"])} ({r["_delta"]:+.0f})'
        ),
        axis=1
    )
    return df


def get_available_days(ranking_all: pd.DataFrame) -> list:
    return sorted(ranking_all["Dzień"].dropna().unique(), reverse=True)


def get_day_ranking(ranking_all: pd.DataFrame, selected_day) -> pd.DataFrame:
    return (
        ranking_all[ranking_all["Dzień"] == selected_day]
        .sort_values("_sort")
        .drop(columns=["Dzień", "_sort", "_prev", "_delta"], errors="ignore")
    )


def get_available_users(ranking_all: pd.DataFrame) -> list:
    return sorted(ranking_all["Użytkownik"].dropna().unique())


def get_streamers(ranking_all: pd.DataFrame) -> list:
    return (
        ranking_all.loc[ranking_all["Czy Streamer"] == 1, "Użytkownik"]
        .dropna()
        .unique()
        .tolist()
    )


def get_chart_df(ranking_all: pd.DataFrame, selected_users: list[str]) -> pd.DataFrame:
    if not selected_users:
        return pd.DataFrame()

    return (
        ranking_all[ranking_all["Użytkownik"].isin(selected_users)]
        .sort_values(["Użytkownik", "Dzień"])
        .copy()
    )


def build_user_comparison_chart(df_chart: pd.DataFrame, sp500_all: pd.DataFrame) -> go.Figure:
    if not df_chart.empty:
        fig = px.line(
            df_chart,
            x="Dzień",
            y="Średnia Ważona",
            color="Użytkownik",
            title="Wyniki użytkowników w czasie"
        )

        fig.update_traces(
            mode="lines",
            line=dict(width=1.8),
            opacity=0.55,
            hovertemplate="Użytkownik: %{fullData.name}<br>Wynik: %{y:.2f}<extra></extra>",
            selector=lambda t: t.name != "S&P 500"
        )
    else:
        fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=sp500_all["day"],
            y=sp500_all["ytd_change"],
            mode="lines",
            name="S&P 500",
            line=dict(color="black", width=3, dash="dash"),
            hovertemplate="S&P 500: %{y:.2f}<extra></extra>"
        )
    )

    fig.update_layout(
        showlegend=True,
        xaxis_title="Dzień",
        yaxis_title="Średnia Ważona",
        hovermode="closest",
        autosize=True,
        height=520,
        margin=dict(l=10, r=10, t=40, b=10),
        plot_bgcolor="white",
        paper_bgcolor="white",
        legend=dict(
            title="",
            orientation="v",
            y=0.5,
            yanchor="middle",
            x=1.01,
            xanchor="left"
        )
    )

    fig.update_xaxes(showgrid=True, gridcolor="rgba(0,0,0,0.06)")
    fig.update_yaxes(showgrid=True, gridcolor="rgba(0,0,0,0.06)")

    return fig