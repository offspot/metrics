# Offspot Metrics Backend

This is the backend component of `metrics` which is responsible to:
- receive or retrieve input events and transform them into indicators then KPI
- serve the API for the frontend UI

## Environment variables

- Database is configured through `DATABASE_URL` with fallback to `sqlite+pysqlite:////{src_dir}/dev.db`
- Allowed origins is configured through `ALLOWED_ORIGINS` with fallback to `http://localhost|http://localhost:8000|http://localhost:8080`

See [`constants.py`](src/offspot_metrics_backend/constants.py)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).
