# Data

### valor justo?
- Valor de Graham (intrínseco): sqrt( 22.5 x LPA x VPA )

# User Experience

### validate tickers

### normalize investidor10 "R$ 1234.0 Bilhoes"

### live update the frontend via websocket

### when importing b3, add all tickers (ask confirmation)

### import b3 automatically

# Server Health

### auto-clean proxy list files

### retry each pipeline with exponential backoff

queue non-displayed pipelines but prioritize the ones being displayed

# Dev Experience

### CI/CD
- docker-compose
- GitHub Actions

# Performance

### parallelize between pipelines

### optimize LLM usage

1. Use smaller llm for simpler extractions

2. Check alternative response candidates

3. Measure token usage

```python
response.usage_metadata.prompt_token_count
response.usage_metadata.candidates_token_count
response.usage_metadata.cached_content_token_count
response.usage_metadata.total_token_count
response.candidates[0].citation_metadata
response.candidates[0].grounding_metadata
```

### prioritize scraping cols that are currently displayed

# Linting

### Use consistent logging instead of print (review by Windsurf)

### Logger improvements (review by Windsurf)

- Logger has no level/formatter; messages may propagate to root logger and be duplicated.
- Recommend: set level, formatter with timestamps, encoding='utf-8', and logger.propagate = False.
    - Set level to logging.ERROR (or configurable).
    - Add formatter with timestamp; set propagate = False.
    - Use FileHandler(..., encoding="utf-8").

```python
def _create_logger(ticker: str, pipeline: str):
    name = f"{ticker}-{pipeline}"
    path = errors_log(pipeline, ticker)
    path.parent.mkdir(parents=True, exist_ok=True)
    handler = logging.FileHandler(path, encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(message)s"))  # timestamp already in message
    logger = logging.getLogger(name)
    logger.setLevel(logging.ERROR)
    logger.propagate = False
    logger.addHandler(handler)
    return logger
```
