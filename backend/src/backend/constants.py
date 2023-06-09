import os
import pathlib
from dataclasses import dataclass

src_dir = pathlib.Path(__file__).parent.resolve()


@dataclass
class BackendConf:
    database_url: str = os.getenv(
        "DATABASE_URL", f"sqlite+aiosqlite:////{src_dir}/dev.db"
    )
    allowed_origins = os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost|http://localhost:8000|http://localhost:8080",  # dev fallback
    ).split("|")
