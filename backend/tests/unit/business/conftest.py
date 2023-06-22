from datetime import datetime
from typing import Generator, TypeAlias

import pytest

DatetimeGenerator: TypeAlias = Generator[datetime, None, None]


@pytest.fixture()
def init_datetime() -> DatetimeGenerator:
    yield datetime.fromisoformat("2023-06-08 10:08:00")


@pytest.fixture()
def previous_datetime() -> DatetimeGenerator:
    yield datetime.fromisoformat("2023-01-03 10:58:00")
