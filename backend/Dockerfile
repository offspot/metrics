FROM python:3.11-slim-bookworm
LABEL org.opencontainers.image.source https://github.com/offspot/metrics

# Specifying a workdir which is not "/"" is mandatory for proper uvicorn watchfiles
# operation (used mostly only in dev, but changing the workdir does not harm production)
WORKDIR "/home"

# Install necessary packages (only pip so far)
RUN python -m pip install --no-cache-dir -U \
      pip

# Choose right architecture
# COPY --from=docker.elastic.co/beats/filebeat-oss:8.8.1-arm64 /usr/share/filebeat /usr/share/filebeat
COPY --from=docker.elastic.co/beats/filebeat-oss:8.8.1 /usr/share/filebeat /usr/share/filebeat
COPY filebeat.yml /usr/share/filebeat/filebeat.yml
RUN chmod go-w /usr/share/filebeat/filebeat.yml

# to set to your clients' origins
ENV ALLOWED_ORIGINS http://localhost:8003|http://127.0.0.1:8003
ENV DATABASE_URL sqlite+pysqlite:////data/database.db

# Copy code + associated artifacts
COPY src /src/src
COPY pyproject.toml *.md /src/

# Install project (including dependencies) + cleanup afterwards
RUN pip install --no-cache-dir /src \
 && rm -rf /src

EXPOSE 80

CMD ["uvicorn", "offspot_metrics_backend.entrypoint:app", "--host", "0.0.0.0", "--port", "80"]
