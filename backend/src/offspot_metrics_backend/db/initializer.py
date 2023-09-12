import logging
import os
from pathlib import Path

from alembic import config
from alembic.command import upgrade

logger = logging.getLogger(__name__)


class Initializer:
    @staticmethod
    def upgrade_db_schema(src_dir: Path):
        """Checks if Alembic schema has been applied to the DB"""
        logger.info(f"Upgrading database schema with config in {src_dir}")
        os.chdir(src_dir)
        cfg = config.Config("alembic.ini")
        upgrade(config=cfg, revision="head")
