Metrics
=======

[![Code Quality Status](https://github.com/offspot/metrics/workflows/QA/badge.svg?query=branch%3Amain)](https://github.com/offspot/metrics/actions/workflows/QA.yml?query=branch%3Amain)
[![Tests Status](https://github.com/offspot/metrics/workflows/Tests/badge.svg?query=branch%3Amain)](https://github.com/offspot/metrics/actions/workflows/Tests.yml?query=branch%3Amain)
[![CodeFactor](https://www.codefactor.io/repository/github/offspot/metrics/badge)](https://www.codefactor.io/repository/github/offspot/metrics)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![codecov](https://codecov.io/gh/offspot/metrics/branch/main/graph/badge.svg)](https://codecov.io/gh/offspot/metrics)

The `metrics` subsystem of Kiwix `offspot` is responsible to transform raw data (e.g. web server logs) available on the `offspot` into business-oriented KPIs displayed on web dashboards.

![Home dashboard](home_dashboard.png)

The whole system is runing locally on the `offspot`. Dashboards are hence only presenting local `offspot` data.

At some point in the future, the system is meant to centralize data in a Cloud for aggregating multiple offspots. An intermediate data format is hence present, between raw data and KPIs.

## Glossary

There is a [glossary](glossary.md) of business terms that are used in the `metrics` subsystem.

## Documentation

We have documentation about the [data architecture](architecture_data.md), the [technical architecture](architecture_technical.md) and the [software architecture](architecture_software.md).

There are also details about the [database structure](database.md) and the [processing logic](processing.md).

## Contributing

For the Python backend, see [backend/README.md](backend/README.md) and [backend/CONTRIBUTING.md](backend/CONTRIBUTING.md).

## Acknowledgements 

Development of this tool was made possible through a grant from the [Hirschmann Stiftung](https://www.hirschmann-stiftung.ch/).

![Hirschmann Stiftung Logo](metrics\logo_hirschmann_stiftung.jpg)