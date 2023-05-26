FROM python:3.11-slim
#LABEL org.opencontainers.image.source https://github.com/offspot/metrics

# to set to your clients' origins
ENV ALLOWED_ORIGINS http://localhost
ENV DATABASE_URL sqlite+aiosqlite:///local.db

WORKDIR /tmp
RUN pip install --no-cache-dir --upgrade pip setuptools==67.8.0 toml==0.10.2 invoke
COPY pyproject.toml README.md setup.cfg setup.py tasks.py /tmp/
RUN invoke install-deps --package runtime

COPY src/ /tmp/src
RUN python setup.py install && mv /tmp/src /src
WORKDIR /src

CMD ["uvicorn", "backend.entrypoint:app", "--host", "0.0.0.0", "--port", "80", "--reload"]