FROM python:3.14-rc-slim

WORKDIR /app

RUN sed -i 's/deb.debian.org/mirror.yandex.ru/g' /etc/apt/sources.list.d/debian.sources

ENV PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple
ENV PIP_TRUSTED_HOST=pypi.tuna.tsinghua.edu.cn
ENV PIP_DEFAULT_TIMEOUT=100

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir --default-timeout=100 setuptools wheel

COPY . .

RUN pip install --no-cache-dir --default-timeout=100 .

EXPOSE 8003

CMD ["sh", "-c", "sleep 20 && alembic -c src/alembic.ini revision --autogenerate -m 'auto' && alembic -c src/alembic.ini upgrade head && uvicorn src.main:app --host 0.0.0.0 --port 8003"]