CREATE TABLE scrapes (
    ticker TEXT PRIMARY KEY NOT NULL,
    asset_class CHECK(asset_class IN ('stock_br','reit_br')) NOT NULL,
    pipeline TEXT NOT NULL,
    last_scraped DATETIME NOT NULL
);