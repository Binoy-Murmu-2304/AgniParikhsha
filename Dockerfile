# ──────────────────────────────────────────────────────────────
# AgniPariksha 2.4 — Multi-Stage Production Docker Image
# ISRO PS #26170: AI-Driven Anomaly Detection in Component Burn-In
# ──────────────────────────────────────────────────────────────
FROM python:3.12-slim AS base

LABEL maintainer="AgniPariksha Team"
LABEL description="ISRO PS #26170 — AI-Driven Anomaly Detection in Component Burn-In & Screening"

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# ── Dependencies layer (cached) ────────────────────────────────
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── Application code ───────────────────────────────────────────
COPY . .

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash agnipariksha && \
    chown -R agnipariksha:agnipariksha /app
USER agnipariksha

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

EXPOSE 8000

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
