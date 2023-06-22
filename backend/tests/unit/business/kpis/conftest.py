from datetime import datetime
from typing import Generator, TypeAlias

import pytest
from sqlalchemy.orm import Session

from backend.business.kpis.kpi import Kpi
from backend.business.kpis.processor import Processor
from backend.business.period import Period

ProcessorGenerator: TypeAlias = Generator[Processor, None, None]
KpiGenerator: TypeAlias = Generator[Kpi, None, None]
DatetimeGenerator: TypeAlias = Generator[datetime, None, None]


@pytest.fixture()
def processor(init_datetime: datetime) -> ProcessorGenerator:
    yield Processor(Period(init_datetime))


class DummyKpi(Kpi):
    """A dummy KPI which is not using indicators at all to simplify testing"""

    unique_id = -1  # this ID is unique to each kind of kpi

    def get_value(
        self, kind: str, start_ts: int, stop_ts: int, session: Session
    ) -> str:
        """For a kind of aggregation (daily, weekly, ...) and a given period, return
        the KPI value."""
        return f"{kind} - {start_ts} - {stop_ts}"


@pytest.fixture()
def dummy_kpi() -> KpiGenerator:
    yield DummyKpi()
