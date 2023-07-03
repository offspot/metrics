Metrics
=======

[![QA Status](https://github.com/offspot/metrics/actions/workflows/qa.yml/badge.svg?query=branch%3Amain)](https://github.com/offspot/metrics/actions/workflows/qa.yml?query=branch%3Amain)
[![CI Status](https://github.com/offspot/metrics/actions/workflows/ci.yml/badge.svg?query=branch%3Amain)](https://github.com/offspot/metrics/actions/workflows/ci.yml?query=branch%3Amain)
[![CodeFactor](https://www.codefactor.io/repository/github/offspot/metrics/badge)](https://www.codefactor.io/repository/github/offspot/metrics)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

The `metrics` subsystem of Kiwix `offspot` is responsible to transform raw data (e.g. web server logs) available on the offspot into business-oriented KPIs displayed on web dashboards. 

The whole system is runing locally on the `offspot`. Dashboards are hence only presenting local `offspot` data.

At some point in the future, the system is meant to centralize data in a Cloud for aggregating multiple offspots. An intermediate data format is hence present, between raw data and KPIs.

This subsystem is designed to be part of Kiwix `offspot` system, but you are welcome to use this standalone, report bugs and request features!

## Architecture

Architecture of the solution is documented in terms of [Data architecture](architecture_data.md), [Technical architecture](architecture_technical.md) and [Software architecture](architecture_software.md)

## Contributing

- See [instructions](dev/README.md) to easily setup a dev environment.
- Don't take assigned issues. Comment if those get staled.
- If your contribution is far from trivial, open an issue to discuss it first.
- For Python code, ensure your code is passing [black formatting](https://pypi.org/project/black/), [isort](https://pypi.org/project/isort/) and [flake8](https://pypi.org/project/flake8/) (88 chars)

