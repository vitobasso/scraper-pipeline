## Setup

#### Install dependencies in the OS
```
brew install python3
```

#### Create virtual environment
To avoid conflicts between project lib and system libs
```
python3 -m venv .venv
source .venv/bin/activate
```

#### Install dependencies within the virtual environment
```bash
python3 -m pip install playwright
playwright install
pip install google-generativeai
pip install python-dotenv
```

## References

#### AI Services
- https://aistudio.google.com/usage

#### Cloud services
- https://dashboard.render.com/cron/new
- https://replit.com/ #free trial