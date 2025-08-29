# syntax=docker/dockerfile:1.7

# -------- Base stage (shared runtime deps, no browsers) --------
FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# System deps (build essentials for pillow/openpyxl/etc.; ca-certificates; curl for health/debug)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential \
       curl \
       ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python deps (runtime only). We install directly from pyproject's poetry deps set below.
# Using a constraints file avoids extra metadata resolution cost during build cache misses.
COPY pyproject.toml ./

# Extract runtime deps from poetry sections and install them via pip
# Note: Keep this list aligned with [tool.poetry.dependencies] in pyproject.toml
RUN --mount=type=cache,target=/root/.cache/pip \
    python - <<'PY'
from pathlib import Path
import tomllib

p = tomllib.loads(Path('pyproject.toml').read_text())
# Poetry section names may vary; handle both tool.poetry.dependencies and legacy project.dependencies
deps = p.get('tool', {}).get('poetry', {}).get('dependencies', {})
if not deps:
    raise SystemExit('No [tool.poetry.dependencies] found in pyproject.toml')
# Remove python itself from deps if present
deps.pop('python', None)
# Convert to pip install line
with open('requirements.txt', 'w') as f:
    for name, spec in deps.items():
        if isinstance(spec, str):
            f.write(f"{name}{spec}\n")
        elif isinstance(spec, dict) and 'version' in spec:
            f.write(f"{name}{spec['version']}\n")
        else:
            # Fallback, attempt name as-is
            f.write(f"{name}\n")
print('Generated requirements.txt with', len(deps), 'deps')
PY

RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt

# Copy source (kept late for better caching when only code changes)
COPY src ./src

# Set a default output dir (can be overridden by env)
ENV CONFIG_OUTPUT_ROOT=/app/output
RUN mkdir -p /app/output

# -------- API stage (smallest possible image) --------
FROM base AS api
# Expose port for uvicorn
EXPOSE 8000
# Healthcheck (simple TCP connect)
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s CMD python -c "import socket; s=socket.create_connection(('127.0.0.1',8000),2); s.close()" || exit 1
# Default command (can be overridden by compose)
CMD ["python", "-m", "uvicorn", "src.api.api:app", "--host", "0.0.0.0", "--port", "8000"]

# -------- Scraper stage (adds Playwright browser runtime) --------
FROM base AS scraper

# Install Playwright browsers only (Playwright Python is already installed in base via requirements.txt)
# Use playwright CLI to install only Chromium to keep image small
RUN --mount=type=cache,target=/root/.cache/ms-playwright \
    python -m playwright install --with-deps chromium \
    && rm -rf /var/lib/apt/lists/*

# Default command (long-running scraper loop)
CMD ["python", "-u", "-m", "src.scraper.scraper"]
