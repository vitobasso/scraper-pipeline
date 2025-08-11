## Setup

### Install dependencies

#### MacOS
```
brew install python3 poetry
poetry config virtualenvs.in-project true
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
poetry config virtualenvs.in-project true
poetry install --no-root

playwright install-deps
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

#### Scraper

To avoid conflicts between project lib and system libs

```
source .venv/bin/activate
PYTHONPATH=. python3 src/main.py
```

#### Rest API
```
source .venv/bin/activate
uvicorn src.api.api:app --host 0.0.0.0 --port 8000
```

## Prod Setup

### Domain Name setup

In order for the frontent (which uses https) to accept the backend call, it needs to be https.
Enabling https requires a certificate and domain name.
We need nginx to handle https before redirecting to uvicorn on https.
```aiignore
sudo apt install nginx certbot python3-certbot-nginx
sudo certbot --nginx -d monitor-de-acoes.duckdns.org
# Certificate is saved at: /etc/letsencrypt/live/monitor-de-acoes.duckdns.org/fullchain.pem
# Key is saved at:         /etc/letsencrypt/live/monitor-de-acoes.duckdns.org/privkey.pem
# Successfully deployed certificate for monitor-de-acoes.duckdns.org to /etc/nginx/sites-enabled/default
# This certificate expires on 2025-11-09.
sudo tee /etc/nginx/sites-enabled/monitor-de-acoes.duckdns.org.conf > /dev/null <<'EOF'
server {
    listen 80;
    server_name monitor-de-acoes.duckdns.org;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name monitor-de-acoes.duckdns.org;

    ssl_certificate /etc/letsencrypt/live/monitor-de-acoes.duckdns.org/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/monitor-de-acoes.duckdns.org/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:8000;  # your uvicorn app port
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
EOF
# Clear any conflicting conf at /etc/nginx/sites-enabled/default.conf (certbot adds some lines to match our domain name)

sudo systemctl restart nginx
uvicorn src.api.api:app --host 127.0.0.1 --port 8000
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

### Domain name
https://www.duckdns.org/ # reserved: monitor-de-acoes.duckdns.org -> 34.42.227.37
https://freedns.afraid.org/ # get subdomains from random people's domains