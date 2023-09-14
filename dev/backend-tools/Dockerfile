FROM python:3.11-slim-bookworm

WORKDIR /src

# uprade pip
RUN python -m pip install --no-cache-dir -U pip

# copy project files
COPY pyproject.toml *.md tasks.py /src/
COPY src /src/src
COPY tests /src/tests

# upgrade pip + install project dependencies
RUN cd /src \
 && python -m pip install --no-cache-dir ".[dev]"

CMD ["sleep", "Infinity"]
