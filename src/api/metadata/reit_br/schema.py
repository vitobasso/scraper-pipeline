from src.api.metadata.common.schema import yahoo_chart

fundamentus = [
    "fundamentus.segmento",
    "fundamentus.cotacao",
    "fundamentus.ffo_yield",
    "fundamentus.dividend_yield",
    "fundamentus.p_vp",
    "fundamentus.valor_de_mercado",
    "fundamentus.liquidez",
    "fundamentus.qtd_de_imoveis",
    "fundamentus.preco_do_m2",
    "fundamentus.aluguel_por_m2",
    "fundamentus.cap_rate",
    "fundamentus.vacancia_media",
]

all = yahoo_chart + fundamentus
