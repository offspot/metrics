import subprocess
from pathlib import Path

from offspot_metrics_backend.constants import logger


class Initializer:
    @staticmethod
    def upgrade_db_schema():
        """Checks if Alembic schema has been applied to the DB"""
        src_dir = Path(__file__).parent.parent
        logger.info(f"Upgrading database schema with config in {src_dir}")
        subprocess.check_output(args=["alembic", "upgrade", "head"], cwd=src_dir)
