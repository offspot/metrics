FROM python:3.11-slim

WORKDIR /work
RUN pip install --no-cache-dir --upgrade pip toml invoke
COPY pyproject.toml README.md tasks.py /work/
RUN invoke install-deps --package qa
CMD ["sleep", "Infinity"]