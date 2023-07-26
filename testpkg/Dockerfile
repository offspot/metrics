FROM python:3.11-slim-bookworm
LABEL org.opencontainers.image.source https://github.com/offspot/metrics

# Install necessary packages
RUN python -m pip install --no-cache-dir -U \
      pip
      
# Copy code + associated artifacts
COPY src /src/src
COPY pyproject.toml *.md LICENSE /src/

CMD ["sleep", "Infinity"]