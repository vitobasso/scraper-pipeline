## Setup

#### Install dependencies
```
brew install python3 poetry
```

#### Build project
```bash
poetry install --no-root
playwright install
```

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
