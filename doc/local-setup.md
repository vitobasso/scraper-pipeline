## Local Setup

### Install dependencies

#### MacOS

```
brew install python3 uv
uv sync
uv run playwright install chromium --with-deps
```

#### Debian (GCP VM)

```
sudo apt update
sudo apt install git
git clone git@github.com:vitobasso/stocks-scraper.git
cd stocks-scraper

curl -LsSf https://astral.sh/uv/install.sh | sh
uv sync
uv run playwright install chromium --with-deps
```

### Secrets

#### Google AI

To call Gemini LLM Api and extract data from screenshots.  
[Api Keys](https://aistudio.google.com/apikey),
Add the `GOOGLE_GENAI_API_KEY` var in the `.env` file at the project root.

### Running from CLI

#### Scraper

```
uv run -m src.scraper.scraper
```

#### Rest API

```
uv run uvicorn src.api.api:app --host 0.0.0.0 --port 8000
```

#### Enable pre-commit hooks

To auto-run linting and formatting before git push

```
git config core.hooksPath .githooks
```
