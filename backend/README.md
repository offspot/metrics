# Offspot Metrics Backend

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

## devel usage

```sh
pip install -U invoke  # only once
invoke install-deps --package dev db-upgrade serve
```

### Constants

- Database is configured through `$DATABASE_URL` with fallback to `sqlite+pysqlite:///dev.db`

See `constants.py`

### Guidelines

- Don't take assigned issues. Comment if those get staled.
- If your contribution is far from trivial, open an issue to discuss it first.
- Ensure your code passed [black formatting](https://pypi.org/project/black/), [isort](https://pypi.org/project/isort/) and [flake8](https://pypi.org/project/flake8/) (88 chars)