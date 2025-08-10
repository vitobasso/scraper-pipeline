## Setup

### Install dependencies

#### MacOS
```
brew install python3 poetry
poetry install --no-root
playwright install
```

#### Debian
```
sudo apt update
sudo apt install git
git clone git@github.com:vitobasso/stocks-scraper.git
cd stocks-scraper

curl -sSL https://install.python-poetry.org | python3 -
source ~/.profile
poetry install --no-root

playwright install
```


### Secrets

#### Google AI

To call Gemini LLM Api and extract data from screenshots.  
[Api Keys](https://aistudio.google.com/apikey),
Add the `GOOGLE_GENAI_API_KEY` var in the `.env` file at the project root.

### Input files
- ticker-list
  - `acoes-br.csv`: one column of tickers, e.g. "bbas3"
  - `acoes-br-setores.csv`: (optional) one column of sectors, e.g. "Financeiro". Used to order rows in the spreadsheet. 
  - `fiis-br`: one column of tickers, e.g. "alzr11"
- statusinvest
  - `carteira-patrimonio-export.xls`: downloaded from https://statusinvest.com.br/carteira/patrimonio
- simplywall
  - `urls.csv`: ticker on column 1, url on column 2

### Running from CLI (no IDE)

To avoid conflicts between project lib and system libs

```
python3 -m venv .venv
source .venv/bin/activate
PYTHONPATH=. python3 src/main.py
```

## References

### AI Services

- https://aistudio.google.com/usage

### Cloud services

- https://dashboard.render.com/cron/new
- https://replit.com/ #free trial

### Proxy lists

https://github.com/proxifly/free-proxy-list # socks proxies work
https://httpbin.org/ip # url to test a proxy
https://proxyscrape.com/free-proxy-list # most are broken
https://free-proxy-list.net/ # most are broken
