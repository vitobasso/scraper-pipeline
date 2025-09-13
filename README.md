### Overview

Modular web scraping pipeline for collecting and processing data. Currently used for Brazilian stock market data.

🌐 [Web Frontend](https://monitor-de-acoes.vercel.app) | [Source](https://github.com/vitobasso/stocks-dashboard-web)

### Tech Stack

- **Backend**: Python, Playwright, Google GenerativeAI
- **API**: FastAPI + Uvicorn
- **Storage**: SQLite + files
- **Package Manager**: UV

### Features

- **Modular Pipeline System**:
  - Task-based pipeline for each data source
  - Automatic retries and dependency handling
  - Scheduled execution
  - Data validation and normalization

- **Data Extraction**:
  - Screenshot analysis via LLM
  - HTML parsing
  - File downloads (CSV, XLS, etc.)
  - Backend API call interception
  - Direct API calls

- **Proxy Support**:
  - Automatic rotation
  - Failure handling

### Implemented Pipelines

- Yahoo Finance
- TradingView
- SimplyWall.st
- StatusInvest
- Investidor10
- Fundamentus
- B3

### Quick Start

See [local-setup.md](doc/local-setup.md).
