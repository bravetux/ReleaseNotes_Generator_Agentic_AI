# ── Stage: pull uv binary ─────────────────────────────────────────────────────
FROM ghcr.io/astral-sh/uv:latest AS uv

# ── Base image ────────────────────────────────────────────────────────────────
FROM python:3.12-slim

# Copy uv binary from official image
COPY --from=uv /uv /bin/uv

# ── Non-root user ─────────────────────────────────────────────────────────────
RUN groupadd --gid 1000 appuser && \
    useradd --uid 1000 --gid appuser --shell /bin/bash --create-home appuser

# ── Working directory ─────────────────────────────────────────────────────────
WORKDIR /app

# ── Environment ───────────────────────────────────────────────────────────────
ENV PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1

# ── Install dependencies ──────────────────────────────────────────────────────
COPY pyproject.toml uv.lock* ./
RUN uv sync --frozen --no-dev 2>/dev/null || uv sync --no-dev

# ── Application source ────────────────────────────────────────────────────────
COPY src/ ./src/
COPY app.py main.py ./

# ── Data directory ────────────────────────────────────────────────────────────
RUN mkdir -p /app/data /app/.sessions && chown -R appuser:appuser /app

# ── Runtime user ──────────────────────────────────────────────────────────────
USER appuser

# ── Port ──────────────────────────────────────────────────────────────────────
EXPOSE 8501

# ── Health check ──────────────────────────────────────────────────────────────
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD python -c \
      "import urllib.request; urllib.request.urlopen('http://localhost:8501/_stcore/health')" \
    || exit 1

# ── Entrypoint ────────────────────────────────────────────────────────────────
ENTRYPOINT ["/app/.venv/bin/streamlit", "run", "app.py", \
            "--server.address", "0.0.0.0", \
            "--server.port", "8501", \
            "--server.headless", "true", \
            "--server.fileWatcherType", "none"]
