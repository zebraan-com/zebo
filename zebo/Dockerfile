# syntax=docker/dockerfile:1

# Use a slim Python base image
FROM python:3.11-slim AS base

# Install curl to fetch uv (Astral's package manager)
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:${PATH}"

# Set workdir
WORKDIR /app

# Copy project files
# Copy lock and project metadata first for better caching
COPY pyproject.toml ./
COPY uv.lock ./
# Copy source code
COPY src/ ./src/

# Sync dependencies into a local .venv (no dev deps)
RUN uv sync --frozen --no-dev

# Ensure the venv is used by default
ENV VIRTUAL_ENV=/app/.venv
ENV PATH="/app/.venv/bin:${PATH}"

# Expose FastAPI port
EXPOSE 8000

# Default command: run FastAPI using uvicorn
CMD ["uv", "run", "uvicorn", "zebo.main:app", "--host", "0.0.0.0", "--port", "8000"]
