from src.api.metadata.common.labels import yahoo_chart

fundamentus = {
    "fundamentus.segmento": {"short": "Segmento", "long": "Segmento"},
    "fundamentus.cotacao": {"short": "Cot", "long": "Cotação"},
    "fundamentus.ffo_yield": {"short": "FFO", "long": "FFO Yield"},
    "fundamentus.dividend_yield": {"short": "DY", "long": "Dividend Yield"},
    "fundamentus.p_vp": {"short": "P/VP", "long": "Preço / Valor Patrimonial"},
    "fundamentus.valor_de_mercado": {"short": "VM", "long": "Valor de Mercado (Bilhões)"},
    "fundamentus.liquidez": {"short": "LMD", "long": "Liquidez Média Diária (Milhões)"},
    "fundamentus.qtd_de_imoveis": {"short": "Imov", "long": "Quantidade de Imóveis"},
    "fundamentus.preco_do_m2": {"short": "Pm2", "long": "Preço do m2 (Milhares)"},
    "fundamentus.aluguel_por_m2": {"short": "Am2", "long": "Aluguel por m2"},
    "fundamentus.cap_rate": {"short": "CR", "long": "Cap Rate"},
    "fundamentus.vacancia_media": {"short": "Vac", "long": "Vacância Média"},
}

all = yahoo_chart | fundamentus
