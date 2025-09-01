CREATE TABLE tickers (
    ticker TEXT PRIMARY KEY NOT NULL,
    asset_class CHECK(asset_class IN ('stock_br','reit_br')) NOT NULL,
    last_requested DATETIME NOT NULL
);