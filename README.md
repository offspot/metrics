Metrics
=======

[![Code Quality Status](https://github.com/offspot/metrics/workflows/QA/badge.svg?query=branch%3Amain)](https://github.com/offspot/metrics/actions/workflows/QA.yml?query=branch%3Amain)
[![Tests Status](https://github.com/offspot/metrics/workflows/Tests/badge.svg?query=branch%3Amain)](https://github.com/offspot/metrics/actions/workflows/Tests.yml?query=branch%3Amain)
[![CodeFactor](https://www.codefactor.io/repository/github/offspot/metrics/badge)](https://www.codefactor.io/repository/github/offspot/metrics)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![codecov](https://codecov.io/gh/offspot/metrics/branch/main/graph/badge.svg)](https://codecov.io/gh/offspot/metrics)

The `metrics` subsystem is responsible to transform raw data (e.g. web server logs) available on the offspot into business-oriented KPIs displayed on web dashboards.

The whole system is runing locally on the offspot. Dashboards are hence only presenting local offspot data.

At some point in the future, the system is meant to centralize data in a Cloud for aggregating multiple offspots. An intermediate data format is hence present, between raw data and KPIs.

## Documentation

We have documentation about the [data architecture](architecture_data.md), the [technical architecture](architecture_technical.md) and the [software architecture](architecture_software.md).

There are also details about the [database structure](database.md) and the [processing logic](processing.md).

### Contributing

For the Python backend API, see [backend/CONTRIBUTING.md](backend/CONTRIBUTING.md)
