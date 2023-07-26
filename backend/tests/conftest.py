from typing import Any, Generator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from offspot_metrics_backend.constants import BackendConf
from offspot_metrics_backend.db.initializer import Initializer


def pytest_sessionstart(session: Any) -> None:
    """
    Called after the Session object has been created and
    before performing collection and entering the run test loop.
    """
    Initializer.ensure_schema_is_up_to_date(src_dir="src")


@pytest.fixture
def dbsession() -> Generator[Session, None, None]:
    with Session(create_engine(url=BackendConf.database_url, echo=False)) as session:
        session.begin()
        yield session
        session.rollback()
