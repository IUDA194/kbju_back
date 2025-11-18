FROM python:3.12-slim-bookworm

ENV DEBIAN_FRONTEND=noninteractive

# ⬇️ добавили build-essential и libpq-dev для psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Установка uv
ADD https://astral.sh/uv/install.sh /uv-installer.sh
RUN sh /uv-installer.sh && rm /uv-installer.sh
ENV PATH="/root/.local/bin/:$PATH"

ENV PYTHONPATH=/app

WORKDIR /app
COPY . .

# Ставим зависимости (включая psycopg2)
RUN uv sync --frozen

# Миграции + сервер
CMD ["sh", "-c", "uv run alembic upgrade head && uv run uvicorn main:app --host 0.0.0.0 --port 8000 --reload"]

