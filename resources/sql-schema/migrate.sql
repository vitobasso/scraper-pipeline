CREATE TABLE tickers2 (
    ticker TEXT PRIMARY KEY NOT NULL,
    asset_class CHECK(asset_class IN ('stock_br','reit_br')) NOT NULL,
    last_requested DATETIME NOT NULL
);

INSERT INTO tickers2 (ticker, asset_class, last_requested)
SELECT ticker,
       CASE asset_class
            WHEN 'acoes' THEN 'stock_br'
            WHEN 'fiis' THEN 'reit_br'
       END,
       last_requested
FROM tickers;

DROP TABLE tickers;
ALTER TABLE tickers2 RENAME TO tickers;