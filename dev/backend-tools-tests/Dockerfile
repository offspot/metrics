FROM python:3.11-slim-bookworm

WORKDIR /src

# install hatch for dev purposes + upgrade pip
RUN python -m pip install --no-cache-dir --upgrade hatch \
 && hatch shell \
 && python -m pip install -U pip

# copy project dependencies
COPY pyproject.toml *.md tasks.py /src/
COPY src/backend/__about__.py /src/src/backend/__about__.py

# start hatch context
RUN cd /src \
 && hatch shell

# install project dependencies
RUN python -m pip install ".[dev]"

# copy project files
COPY src /src/src
COPY tests /src/tests

CMD ["sleep", "Infinity"]