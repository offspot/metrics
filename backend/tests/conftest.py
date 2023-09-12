from collections.abc import Generator
from pathlib import Path
from typing import Any

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from offspot_metrics_backend.constants import BackendConf
from offspot_metrics_backend.db.initializer import Initializer


def pytest_sessionstart(session: Any) -> None:  # noqa: ARG001
    """
    Called after the Session object has been created and
    before performing collection and entering the run test loop.
    """
    Initializer.upgrade_db_schema(src_dir=Path("src"))


@pytest.fixture
def dbsession() -> Generator[Session, None, None]:
    with Session(create_engine(url=BackendConf.database_url, echo=False)) as session:
        session.begin()
        yield session
        session.rollback()
