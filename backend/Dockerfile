FROM python:3.11-slim
LABEL org.opencontainers.image.source https://github.com/offspot/metrics

# to set to your clients' origins
ENV ALLOWED_ORIGINS http://localhost
ENV DATABASE_URL sqlite+pysqlite:///local.db

WORKDIR /app
RUN pip install --no-cache-dir --upgrade pip invoke
COPY pyproject.toml README.md tasks.py /app/
RUN invoke install-deps --package runtime

COPY src/ /app/src

CMD ["invoke", "serve", "--args", "--host 0.0.0.0 --port 80"]