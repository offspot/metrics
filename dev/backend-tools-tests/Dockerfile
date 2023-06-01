FROM python:3.11-slim

WORKDIR /work
RUN pip install --no-cache-dir --upgrade pip setuptools==67.8.0 toml==0.10.2 invoke
COPY pyproject.toml README.md setup.cfg setup.py tasks.py /work/
RUN invoke install-deps --package test
