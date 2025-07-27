## Setup

#### Install dependencies
```
brew install python3 poetry
```

#### Secrets
##### 1. Google AI 
https://aistudio.google.com/apikey
Add the `GOOGLE_GENAI_API_KEY` var in the `.env` file at the project root.

##### 2. Google Drive
[IAM and admin, Service accounts, Keys](https://console.cloud.google.com/iam-admin/serviceaccounts/details/113244814507907976994;edit=true/keys?inv=1&invt=AbzKDA&project=api-project-168147909795)
Add key, JSON, download it, name `gcp-secret.json` and place at the project root.
[Apis and Services](https://console.cloud.google.com/apis/credentials?inv=1&invt=Ab35cQ&project=api-project-168147909795)
Create credentials, OAuth Client ID, Desktop app, download it, name `client-secret.json` and place at the project root.
"Oauth consent screen", Audience, Test users, add your email

#### Build project
```bash
poetry install --no-root
playwright install
```

#### Google Sheets dependencies
- A folder shared with the service account. New sheets will be automatically created in there.
  - `config.google_dir` holds the folder id.
- Template sheets:
  - `config.google_template_acoes` holds the acoes-br template file id
  - `config.google_template_fiis` holds the fiis-br template file id


#### Running from CLI (no IDE)
To avoid conflicts between project lib and system libs
```
python3 -m venv .venv
source .venv/bin/activate
```

## References

#### AI Services
- https://aistudio.google.com/usage

#### Cloud services
- https://dashboard.render.com/cron/new
- https://replit.com/ #free trial

#### Proxy lists
https://github.com/proxifly/free-proxy-list # socks proxies work
https://httpbin.org/ip # url to test a proxy
https://proxyscrape.com/free-proxy-list # most are broken
https://free-proxy-list.net/ # most are broken
