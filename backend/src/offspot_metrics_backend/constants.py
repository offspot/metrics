import os
import pathlib

src_dir = pathlib.Path(__file__).parent.resolve()


class BackendConf:
    """Shared backend configuration"""

    database_url: str = os.getenv(
        "DATABASE_URL", f"sqlite+pysqlite:////{src_dir}/dev.db"
    )
    allowed_origins: list[str] = os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost|http://localhost:8000|http://localhost:8080",  # dev fallback
    ).split("|")

    package_conf_file_location = os.getenv("PACKAGE_CONF_FILE", "/conf/packages.yml")

    # Boolean stoping background processing of logs + indicators / kpis update / cleanup
    # Useful mostly for local development purpose when we do not want to generate new
    # events regularly and hence do not want to cleanup DB from simulation results
    # The environment variable must hence be explicitely set to True (case-insensitive)
    # all other values will enable the processing.
    processing_disabled = os.getenv("PROCESSING_DISABLED", "False").lower() == "true"

    filebeat_process_location = "/usr/share/filebeat/filebeat"

    filebeat_present = pathlib.Path(filebeat_process_location).exists()
