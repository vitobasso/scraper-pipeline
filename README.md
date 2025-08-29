## Local Setup

### Install dependencies

#### MacOS

```
brew install --cask docker
docker compose -f infra/docker-compose.yml build
```

#### Debian (GCP VM)

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

### Running from CLI (no IDE)

#### Migrate DB

Run once to setup `output/.../db.sqlite`

```
python3 -m src.migrate_db
```

#### Scraper and Rest API

```
docker compose -f infra/docker-compose.yml up -d
```

#### Linting

```
ruff check --fix .
ruff format .
```

## References

### AI Services

- https://aistudio.google.com/usage

### Proxy lists

https://github.com/proxifly/free-proxy-list # socks proxies work
https://httpbin.org/ip # url to test a proxy
https://proxyscrape.com/free-proxy-list # most are broken
https://free-proxy-list.net/ # most are broken
