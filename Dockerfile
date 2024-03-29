FROM node:20-alpine as metrics_ui

WORKDIR /src
COPY frontend /src
RUN yarn install --frozen-lockfile
RUN VITE_BACKEND_ROOT_API="./api/v1" yarn build

FROM python:3.12-alpine
LABEL org.opencontainers.image.source https://github.com/offspot/metrics

# Specifying a workdir which is not "/"" is mandatory for proper uvicorn watchfiles
# operation (used mostly only in dev, but changing the workdir does not harm production)
WORKDIR "/home"

# Install necessary packages (only pip so far)
RUN python -m pip install --no-cache-dir -U \
      pip

# to set to your clients' origins
ENV ALLOWED_ORIGINS http://localhost:8003|http://127.0.0.1:8003
ENV DATABASE_URL sqlite+pysqlite:////data/database.db
ENV LOGWATCHER_DATA_FOLDER /data/logwatcher

COPY backend/pyproject.toml backend/README.md /src/
COPY backend/src/offspot_metrics_backend/__about__.py /src/src/offspot_metrics_backend/__about__.py

# Install project dependencies
RUN pip install --no-cache-dir /src

# Copy code + associated artifacts
COPY backend/src /src/src
COPY backend/*.md /src/

# Install project + cleanup afterwards
RUN pip install --no-cache-dir /src \
 && mkdir -p /data/logwatcher \
 && cd /src/src \
 && rm -rf /src

COPY --from=metrics_ui /src/dist /src/ui

EXPOSE 80

CMD ["uvicorn", "offspot_metrics_backend.entrypoint:app", "--host", "0.0.0.0", "--port", "80"]
