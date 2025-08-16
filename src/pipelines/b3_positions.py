import json
from collections import defaultdict

import pandas as pd
import requests
from playwright.sync_api import sync_playwright


# TODO

def main():
    cpf = "00000000000"
    senha = "SUA_SENHA_AQUI"

    token = get_b3_token(cpf, senha)
    positions = get_positions(token)
    print(json.dumps(positions, indent=2))


def get_b3_token(cpf, senha):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # headless=True pode quebrar captcha/MFA
        page = browser.new_page()

        # Acessa o portal, que redireciona para gov.br
        page.goto("https://investidor.b3.com.br/")

        # Preenche CPF e senha (exemplo simplificado)
        page.fill('input[name="cpf"]', cpf)
        page.fill('input[name="password"]', senha)
        page.click('button[type="submit"]')

        # Aqui você terá que completar MFA manualmente
        print("Complete a MFA no browser e depois pressione Enter...")
        input()

        # Depois do login, o portal faz fetch para seus endpoints internos
        # Pegamos o token de autorização dos requests do devtools
        # Exemplo: token salvo em localStorage
        token = page.evaluate("() => window.localStorage.getItem('access_token')")
        print("Access token:", token)

        browser.close()
        return token


def get_positions(token):
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }
    url = "https://investidor.b3.com.br/api/portfolio/v1/positions"  # endpoint interno
    resp = requests.get(url, headers=headers)
    data = resp.json()
    return data


def preco_medio(positions):
    # Estrutura para acumular posição
    portfolio = defaultdict(lambda: {"total_qty": 0, "total_cost": 0})

    for op in positions:
        ticker = op["ticker"]
        qty = op["quantity"]
        price = op["price"]
        if op["type"] == "buy":
            # Atualiza quantidade e custo total
            portfolio[ticker]["total_qty"] += qty
            portfolio[ticker]["total_cost"] += qty * price
        elif op["type"] == "sell":
            # Reduz quantidade e custo proporcional
            if portfolio[ticker]["total_qty"] == 0:
                continue  # vendeu mais do que tinha
            avg_price = portfolio[ticker]["total_cost"] / portfolio[ticker]["total_qty"]
            portfolio[ticker]["total_qty"] -= qty
            portfolio[ticker]["total_cost"] -= qty * avg_price

    # Calcula preço médio
    for ticker, data in portfolio.items():
        if data["total_qty"] > 0:
            avg_price = data["total_cost"] / data["total_qty"]
        else:
            avg_price = 0
        print(f"{ticker}: Qtd={data['total_qty']}, Preço médio={avg_price:.2f}")


def load_xls():
    # caminho do arquivo
    file_path = "b3-movimentacao-2025-08-16-17-40-22.xlsx"

    # carrega todas as abas
    xls = pd.ExcelFile(file_path)

    # supondo que os dados de movimentação estão na primeira aba
    df = pd.read_excel(xls, xls.sheet_names[0])

    # normaliza os nomes das colunas
    df.columns = [c.strip().lower() for c in df.columns]

    # exemplo: colunas esperadas -> 'ticker', 'quantidade', 'valor'
    # ajuste conforme o layout real da planilha
    df = df.rename(columns={
        'qtd': 'quantidade',
        'qtd.': 'quantidade',
        'qde': 'quantidade',
        'preço': 'valor',
        'preço unitário': 'valor',
        'preco': 'valor',
    })
