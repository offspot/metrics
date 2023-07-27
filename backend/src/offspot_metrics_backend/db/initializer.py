import logging
import os
from pathlib import Path

from alembic import config
from alembic.command import check

logger = logging.getLogger(__name__)


class Initializer:
    @staticmethod
    def ensure_schema_is_up_to_date(src_dir: Path | None = None):
        """Checks if Alembic schema has been applied to the DB"""
        logger.info("Checking database schema")
        if src_dir:
            os.chdir(src_dir)
        cfg = config.Config("alembic.ini")
        check(cfg)
