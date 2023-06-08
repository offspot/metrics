from typing import Any

from backend.db.initializer import Initializer


def pytest_sessionstart(session: Any) -> None:
    """
    Called after the Session object has been created and
    before performing collection and entering the run test loop.
    """
    Initializer.check_if_schema_is_up_to_date()
