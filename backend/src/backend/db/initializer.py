import logging

from alembic import config
from alembic.command import check

logger = logging.getLogger(__name__)


class Initializer:
    @staticmethod
    def check_if_schema_is_up_to_date() -> None:
        """Checks if Alembic schema has been applied to the DB"""
        logger.info("Checking database schema")
        cfg = config.Config("alembic.ini")
        check(cfg)
