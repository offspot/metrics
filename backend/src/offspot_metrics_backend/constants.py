import os
import pathlib

src_dir = pathlib.Path(__file__).parent.resolve()


class BackendConf:
    database_url: str = os.getenv(
        "DATABASE_URL", f"sqlite+pysqlite:////{src_dir}/dev.db"
    )
    allowed_origins: list[str] = os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost|http://localhost:8000|http://localhost:8080",  # dev fallback
    ).split("|")
