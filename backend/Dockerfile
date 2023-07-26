FROM python:3.11-slim-bookworm
LABEL org.opencontainers.image.source https://github.com/offspot/metrics

# Install necessary packages
RUN python -m pip install --no-cache-dir -U \
      pip \
      invoke

# to set to your clients' origins
ENV ALLOWED_ORIGINS http://localhost
ENV DATABASE_URL sqlite+pysqlite:///local.db

# Copy code + associated artifacts
COPY src /src/src
COPY pyproject.toml *.md /src/

# Install + cleanup
RUN pip install --no-cache-dir /src \
 && rm -rf /src

# TODO: fix this
CMD ["invoke", "serve", "--args", "--host 0.0.0.0 --port 80"]