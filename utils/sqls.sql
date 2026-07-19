CREATE VIEW stock_latest_ytd AS
WITH latest_price AS (
    SELECT
        ticker,
        ytd_change,
        ROW_NUMBER() OVER (
            PARTITION BY ticker
            ORDER BY day DESC
        ) AS rn
    FROM (
        SELECT ticker, ytd_change, day FROM stock_prices
        UNION ALL
        SELECT ticker, ytd_change, day FROM stock_prices_other
    ) AS all_prices
)
SELECT
    ticker,
    ytd_change
FROM latest_price
WHERE rn = 1;

CREATE VIEW current_ranking AS
WITH user_picks AS (
    SELECT
        u.user,
        u.pl_ticker,
        COALESCE(u.us_ticker, 'BRAK') us_ticker,
        u.is_us,
        COALESCE(u.world_ticker, 'BRAK') world_ticker,
        u.is_world,
        u.commodity_ticker,
        u.crypto_ticker,
        u.is_streamer
    FROM users u
),
latest_ytd AS(
    SELECT t1.ticker, name, ytd_change 
    FROM stock_latest_ytd t1
    LEFT JOIN stock_desc t2
    ON t1.ticker = t2.ticker order by t1.ticker desc
),
joined AS (
    SELECT 
        u.user,
        pl.name pl_name,
        pl.ytd_change pl_ytd,
        COALESCE(us.name, 'BRAK') us_name,
        CASE
            WHEN u.is_us THEN us.ytd_change
            ELSE 0
        END AS us_ytd,
        COALESCE(world.name, 'BRAK') world_name,
        CASE
            WHEN u.is_world THEN world.ytd_change
            ELSE 0
        END AS world_ytd,
        commodity.name commodity_name,
        COALESCE(commodity.ytd_change, 0) commodity_ytd,
        crypto.name crypto_name,
        crypto.ytd_change crypto_ytd,
        is_streamer,
        is_us,
        is_world
    FROM user_picks u
    LEFT JOIN latest_ytd pl
    ON pl.ticker = u.pl_ticker
    LEFT JOIN latest_ytd us
    ON us.ticker = u.us_ticker
    LEFT JOIN latest_ytd world
    ON world.ticker = u.world_ticker
    LEFT JOIN latest_ytd commodity
    ON commodity.ticker = u.commodity_ticker
    LEFT JOIN latest_ytd crypto
    ON crypto.ticker = u.crypto_ticker
), 
ranking AS (
    SELECT 
        *, 
        ROUND((COALESCE(pl_ytd, 0) + COALESCE(us_ytd, 0) + COALESCE(world_ytd, 0)) / 3.0, 2) AS avg_comp,
        ROUND((COALESCE(pl_ytd, 0) * 0.25 + COALESCE(us_ytd, 0) * 0.25 + COALESCE(world_ytd, 0) * 0.25 + COALESCE(commodity_ytd, 0) * 0.15 + COALESCE(crypto_ytd, 0) * 0.10) / 5.0, 2) AS avg
    FROM joined
) 
SELECT 
    ROW_NUMBER() OVER (ORDER BY avg DESC) as "Miejsce",
    user AS "Użytkownik",
    pl_name AS "Spółka Polska",
    pl_ytd AS "Wynik Polska",
    us_name AS "Spółka Usa",
    us_ytd AS "Wynik Usa",
    world_name AS "Spółka Świat",
    world_ytd AS "Wynik Świat",
    commodity_name AS "Surowiec",
    commodity_ytd AS "Wynik Surowiec",
    crypto_name AS "Krypto",
    crypto_ytd AS "Wynik Krypto",
    avg_comp AS "Średnia Spółki",
    avg AS "Średnia Ważona",
    is_us AS "Czy Usa",
    is_world AS "Czy Świat",
    is_streamer AS "Czy Streamer"
FROM ranking;

CREATE VIEW ranking AS
WITH user_picks AS (
    SELECT
        u.user,
        u.pl_ticker,
        COALESCE(u.us_ticker, 'BRAK') AS us_ticker,
        u.is_us,
        COALESCE(u.world_ticker, 'BRAK') AS world_ticker,
        u.is_world,
        u.commodity_ticker,
        u.crypto_ticker,
        u.is_streamer
    FROM users u
),
all_prices AS (
    SELECT
        ticker,
        ytd_change,
        date(day) AS day
    FROM stock_prices
    UNION ALL
    SELECT
        ticker,
        ytd_change,
        date(day) AS day
    FROM stock_prices_other
),
calendar_days AS (
    SELECT DISTINCT day
    FROM all_prices
    WHERE day >= '2026-01-02'
),
prices_ranked AS (
    SELECT
        d.day AS ranking_day,
        p.ticker,
        p.ytd_change,
        p.day AS price_day,
        ROW_NUMBER() OVER (
            PARTITION BY d.day, p.ticker
            ORDER BY p.day DESC
        ) AS rn
    FROM calendar_days d
    JOIN all_prices p
      ON p.day <= d.day
),

latest_ytd AS (
    SELECT
        pr.ranking_day,
        pr.ticker,
        sd.name,
        pr.ytd_change
    FROM prices_ranked pr
    LEFT JOIN stock_desc sd
      ON pr.ticker = sd.ticker
    WHERE pr.rn = 1
),

joined AS (
    SELECT
        d.day AS ranking_day,
        u.user,
        pl.name AS pl_name,
        pl.ytd_change AS pl_ytd,
        COALESCE(us.name, 'BRAK') AS us_name,
        CASE
            WHEN u.is_us THEN COALESCE(us.ytd_change, 0)
            ELSE 0
        END AS us_ytd,
        COALESCE(world.name, 'BRAK') AS world_name,
        CASE
            WHEN u.is_world THEN COALESCE(world.ytd_change, 0)
            ELSE 0
        END AS world_ytd,
        commodity.name AS commodity_name,
        COALESCE(commodity.ytd_change, 0) AS commodity_ytd,
        crypto.name AS crypto_name,
        COALESCE(crypto.ytd_change, 0) AS crypto_ytd,
        u.is_streamer,
        u.is_us,
        u.is_world
    FROM calendar_days d
    CROSS JOIN user_picks u
    LEFT JOIN latest_ytd pl
        ON pl.ranking_day = d.day
       AND pl.ticker = u.pl_ticker
    LEFT JOIN latest_ytd us
        ON us.ranking_day = d.day
       AND us.ticker = u.us_ticker
    LEFT JOIN latest_ytd world
        ON world.ranking_day = d.day
       AND world.ticker = u.world_ticker
    LEFT JOIN latest_ytd commodity
        ON commodity.ranking_day = d.day
       AND commodity.ticker = u.commodity_ticker
    LEFT JOIN latest_ytd crypto
        ON crypto.ranking_day = d.day
       AND crypto.ticker = u.crypto_ticker
),

ranking AS (
    SELECT
        *,
        ROUND(
            (COALESCE(pl_ytd, 0) + COALESCE(us_ytd, 0) + COALESCE(world_ytd, 0)) / 3.0,
            2
        ) AS avg_comp,
        ROUND(
            (
                COALESCE(pl_ytd, 0) * 0.25 +
                COALESCE(us_ytd, 0) * 0.25 +
                COALESCE(world_ytd, 0) * 0.25 +
                COALESCE(commodity_ytd, 0) * 0.15 +
                COALESCE(crypto_ytd, 0) * 0.10
            ) / 5.0,
            2
        ) AS avg
    FROM joined
)

SELECT
    ranking_day AS "Dzień",
    ROW_NUMBER() OVER (
        PARTITION BY ranking_day
        ORDER BY avg DESC, user
    ) AS "Miejsce",
    user AS "Użytkownik",
    pl_name AS "Spółka Polska",
    pl_ytd AS "Wynik Polska",
    us_name AS "Spółka Usa",
    us_ytd AS "Wynik Usa",
    world_name AS "Spółka Świat",
    world_ytd AS "Wynik Świat",
    commodity_name AS "Surowiec",
    commodity_ytd AS "Wynik Surowiec",
    crypto_name AS "Krypto",
    crypto_ytd AS "Wynik Krypto",
    avg_comp AS "Średnia Spółki",
    avg AS "Średnia Ważona",
    is_us AS "Czy Usa",
    is_world AS "Czy Świat",
    is_streamer AS "Czy Streamer"
FROM ranking
ORDER BY ranking_day, "Miejsce";