FROM python:3.11-slim-bookworm

WORKDIR /src

# uprade pip
RUN python -m pip install --no-cache-dir -U pip

# copy minimal project items to install dependencies
COPY pyproject.toml README.md /src/
COPY src/offspot_metrics_backend/__about__.py /src/src/offspot_metrics_backend/__about__.py

# Install project dependencies
RUN cd /src \
 && python -m pip install --no-cache-dir ".[dev]"

# copy project files
COPY *.md tasks.py /src/
COPY src /src/src
COPY tests /src/tests

# install project
RUN pip install --no-cache-dir /src

CMD ["sleep", "Infinity"]
