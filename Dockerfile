FROM python:3.14-rc-slim

WORKDIR /app

RUN sed -i 's/deb.debian.org/mirror.yandex.ru/g' /etc/apt/sources.list.d/debian.sources

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

COPY . .

RUN pip install --no-cache-dir .

EXPOSE 8000

CMD ["sh", "-c", "sleep 20 && alembic -c src/alembic.ini revision --autogenerate -m 'auto' && alembic -c src/alembic.ini upgrade head && uvicorn src.main:app --host 0.0.0.0 --port 8000"]