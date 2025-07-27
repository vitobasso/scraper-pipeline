## Setup

### Install dependencies

```
brew install python3 poetry
poetry install --no-root
playwright install
```


### Secrets

#### 1. Google AI

To call Gemini LLM Api and extract data from screenshots.  
[Api Keys](https://aistudio.google.com/apikey),
Add the `GOOGLE_GENAI_API_KEY` var in the `.env` file at the project root.

#### 2. Google Drive - Oauth Client ID

To create new files in a user's personal Google Drive.  
[Apis and Services, Credentials](https://console.cloud.google.com/apis/credentials?inv=1&invt=Ab35cQ&project=api-project-168147909795),
Create credentials, OAuth Client ID, Desktop app, download it, name `client-secret.json` and place at the project
root.  
[Oauth consent screen, Audience](https://console.cloud.google.com/auth/audience?inv=1&invt=Ab35cQ&project=api-project-168147909795),
Test users, add your email.

#### 3. Google Sheets - Service account

To add data to Google Sheets files.  
[IAM and admin, Service accounts, Keys](https://console.cloud.google.com/iam-admin/serviceaccounts/details/113244814507907976994;edit=true/keys?inv=1&invt=AbzKDA&project=api-project-168147909795).  
Add key, JSON, download it, name `gcp-secret.json` and place at the project root.

### Dependency on Google Sheets

A folder shared with the service account. New sheets will be automatically created in there.  
`config.google_dir` holds the folder id.

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
