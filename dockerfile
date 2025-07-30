FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN pip install poetry

COPY pyproject.toml poetry.lock ./
COPY src/ ./src/
COPY data/ ./data/
COPY dbschema.sql ./

RUN poetry config virtualenvs.create false

RUN poetry install --no-root

ENV PYTHONPATH=/app

ENTRYPOINT ["poetry", "run", "python", "-m", "src.main"]