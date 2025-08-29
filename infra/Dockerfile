# syntax=docker/dockerfile:1.7

########### Dependencies builder (Poetry) ###########
FROM python:3.11-slim AS deps-builder

ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VIRTUALENVS_CREATE=false

# Build-time system deps for compiling wheels
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /w
COPY pyproject.toml poetry.lock ./

# Install Poetry and then install project deps (no dev, no project itself)
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip \
    && pip install poetry \
    && poetry install --no-root --only main --no-interaction --no-ansi


########### Base stage (shared runtime deps, no browsers) ###########
FROM python:3.11-slim AS base

ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Runtime-only OS deps (keep minimal). curl + certs for health and TLS.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       curl \
       ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy only installed Python packages and scripts from builder (no Poetry itself required at runtime)
COPY --from=deps-builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=deps-builder /usr/local/bin /usr/local/bin

# Copy source (kept late for better caching when only code changes)
COPY src ./src

# Set a default output dir (can be overridden by env)
ENV CONFIG_OUTPUT_ROOT=/app/output
RUN mkdir -p /app/output

########### API stage (smallest possible image) ###########
FROM base AS api
# Expose port for uvicorn
EXPOSE 8000
# Healthcheck (simple TCP connect)
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s CMD python -c "import socket; s=socket.create_connection(('127.0.0.1',8000),2); s.close()" || exit 1
# Default command (can be overridden by compose)
CMD ["python", "-m", "uvicorn", "src.api.api:app", "--host", "0.0.0.0", "--port", "8000"]

########### Scraper stage (adds Playwright browser runtime) ###########
FROM base AS scraper

# Install Playwright browsers only (Playwright Python is already installed in base via requirements.txt)
# Use playwright CLI to install only Chromium to keep image small
RUN --mount=type=cache,target=/root/.cache/ms-playwright \
    python -m playwright install --with-deps chromium \
    && rm -rf /var/lib/apt/lists/*

# Default command (long-running scraper loop)
CMD ["python", "-u", "-m", "src.scraper.scraper"]
