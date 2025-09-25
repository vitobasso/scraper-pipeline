# User Experience

### when importing b3, add all tickers (ask confirmation)

### import b3 automatically

# Server Health

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

# Best practices

### make datetimes explicitly UTC

### Use consistent logging instead of print (review by Windsurf)

