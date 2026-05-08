FROM python:3.14-slim AS builder

WORKDIR /app

RUN sed -i 's/deb.debian.org/mirror.yandex.ru/g' /etc/apt/sources.list.d/debian.sources

ENV PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple
ENV PIP_TRUSTED_HOST=pypi.tuna.tsinghua.edu.cn
ENV PIP_DEFAULT_TIMEOUT=100

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    build-essential \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

RUN python -m venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH"

RUN pip install --upgrade pip setuptools wheel

COPY . .

RUN pip install --no-cache-dir .

FROM python:3.14-slim

WORKDIR /app

RUN sed -i 's/deb.debian.org/mirror.yandex.ru/g' /etc/apt/sources.list.d/debian.sources

RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /opt/venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH"

COPY . .

EXPOSE 8003

CMD ["sh", "-c", "\
sleep 20 && \
echo 'Generating migrations...' && \
alembic -c src/alembic.ini revision --autogenerate -m 'auto_migration' || true && \
echo 'Applying migrations...' && \
alembic -c src/alembic.ini upgrade head && \
echo 'Starting application...' && \
uvicorn src.main:app --host 0.0.0.0 --port 8003 \
"]