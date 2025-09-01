INSERT INTO tickers (ticker, asset_class, last_requested) VALUES
('VALE3', 'stock_br', CURRENT_TIMESTAMP),
('ITUB4', 'stock_br', CURRENT_TIMESTAMP),
('PETR4', 'stock_br', CURRENT_TIMESTAMP),
('BBDC4', 'stock_br', CURRENT_TIMESTAMP),
('KNCR11', 'reit_br', CURRENT_TIMESTAMP),
('KNIP11', 'reit_br', CURRENT_TIMESTAMP),
('XPML11', 'reit_br', CURRENT_TIMESTAMP),
('HGLG11', 'reit_br', CURRENT_TIMESTAMP)
ON CONFLICT(ticker) DO NOTHING;