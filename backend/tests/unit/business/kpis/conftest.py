from collections.abc import Generator
from datetime import datetime
from typing import TypeAlias

import pytest
from sqlalchemy.orm import Session

from offspot_metrics_backend.business.agg_kind import AggKind
from offspot_metrics_backend.business.kpis.kpi import Kpi
from offspot_metrics_backend.business.kpis.processor import Processor
from offspot_metrics_backend.business.period import Period

ProcessorGenerator: TypeAlias = Generator[Processor, None, None]
KpiGenerator: TypeAlias = Generator[Kpi, None, None]
DatetimeGenerator: TypeAlias = Generator[datetime, None, None]


@pytest.fixture()
def processor(init_datetime: datetime) -> ProcessorGenerator:
    yield Processor(Period(init_datetime))


class DummyKpi(Kpi):
    """A dummy KPI which is not using indicators at all to simplify testing"""

    unique_id = -2001  # this ID is unique to each kind of kpi

    def get_value(
        self,
        agg_kind: AggKind,
        start_ts: int,
        stop_ts: int,
        session: Session,  # noqa: ARG002
    ) -> str:
        """For a kind of aggregation (daily, weekly, ...) and a given period, return
        the KPI value."""
        return f"{agg_kind.value} - {start_ts} - {stop_ts}"


@pytest.fixture()
def dummy_kpi() -> KpiGenerator:
    yield DummyKpi()
