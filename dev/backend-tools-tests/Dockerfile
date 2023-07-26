FROM python:3.11-slim-bookworm

WORKDIR /src

# install hatch
RUN python -m pip install --no-cache-dir --upgrade hatch

# copy project dependencies (including early __about__.py since it is needed to create hatch shell)
COPY pyproject.toml *.md tasks.py /src/
COPY src/offspot_metrics_backend/__about__.py /src/src/offspot_metrics_backend/__about__.py

# start hatch context
RUN cd /src \
 && hatch shell

# upgrade pip + install project dependencies
RUN python -m pip install --no-cache-dir -U pip \
 && python -m pip install --no-cache-dir ".[dev]"

# copy project files
COPY src /src/src
COPY tests /src/tests

CMD ["sleep", "Infinity"]
