FROM python:3.12-slim

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

COPY apps/engine/pyproject.toml apps/engine/uv.lock ./
RUN uv sync --frozen --no-dev

COPY apps/engine/app/ app/

EXPOSE 8000
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
