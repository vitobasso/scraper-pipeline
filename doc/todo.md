# Bug

### b3_listagem depends on statusinvest

### forecast wrong sometimes

# Data

# User Experience

### live update the frontend via websocket

### when importing b3, add all tickers (ask confirmation)

### import b3 automatically

# Server Health

### auto-clean proxy list files

### retry each pipeline with exponential backoff

queue non-displayed pipelines but prioritize the ones being displayed

# Dev Experience

### AI review on keys

### unit tests
- normalization
- validation

### CI/CD
- docker-compose
- GitHub Actions

# Performance

### simplywall: bulk scrape "[browse all stocks](https://simplywall.st/stocks/br)" even though it's not all tickers

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

