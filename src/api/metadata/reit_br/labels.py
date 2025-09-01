yahoo_chart = {
    "yahoo_chart.1mo": {"short": "1M", "long": "Último Mês"},
    "yahoo_chart.1y": {"short": "1A", "long": "Último Ano"},
    "yahoo_chart.5y": {"short": "5A", "long": "Últimos 5 Anos"},
}

fundamentus = {
    "segmento": {"short": "Segmento", "long": "Segmento"},
    "cotacao": {"short": "Cot", "long": "Cotação"},
    "ffo_yield": {"short": "FFO", "long": "FFO Yield"},
    "dividend_yield": {"short": "DY", "long": "Dividend Yield"},
    "p_vp": {"short": "P/VP", "long": "Preço / Valor Patrimonial"},
    "valor_de_mercado": {"short": "VM", "long": "Valor de Mercado"},
    "liquidez": {"short": "LMD", "long": "Liquidez Média Diária"},
    "qtd_de_imoveis": {"short": "Imov", "long": "Quantidade de Imóveis"},
    "preco_do_m2": {"short": "Pm2", "long": "Preço do m2"},
    "aluguel_por_m2": {"short": "Am2", "long": "Aluguel por m2"},
    "cap_rate": {"short": "CR", "long": "Cap Rate"},
    "vacancia_media": {"short": "VM", "long": "Vacância Média"},
}

all = yahoo_chart | fundamentus
