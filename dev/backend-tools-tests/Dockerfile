FROM python:3.10-slim

WORKDIR /tmp
RUN pip install --no-cache-dir --upgrade pip setuptools==67.8.0 toml==0.10.2 invoke
COPY pyproject.toml README.md setup.cfg setup.py tasks.py /tmp/
RUN invoke install-deps --package test

WORKDIR /src
