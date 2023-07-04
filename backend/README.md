# Offspot Metrics Backend

The backend of the `metrics` subsystem.

## Developement startup

```sh
pip install -U invoke  # only once
invoke install-deps --package dev db-upgrade serve
```

## Environment variables

- Database is configured through `DATABASE_URL` with fallback to `sqlite+pysqlite:///dev.db`
- Allowed origins (for CORS) are configured through `ALLOWED_ORIGINS`

See [`constants.py`](src/backend/constants.py) for details
