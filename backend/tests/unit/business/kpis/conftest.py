from collections.abc import Generator
from dataclasses import dataclass
from datetime import datetime
from typing import TypeAlias

import pytest
from sqlalchemy.orm import Session

from offspot_metrics_backend.business.agg_kind import AggKind
from offspot_metrics_backend.business.indicators.content_visit import (
    ContentHomeVisit,
    ContentItemVisit,
)
from offspot_metrics_backend.business.indicators.indicator import Indicator
from offspot_metrics_backend.business.kpis.kpi import Kpi
from offspot_metrics_backend.business.kpis.processor import Processor
from offspot_metrics_backend.business.period import Period
from offspot_metrics_backend.db.models import (
    IndicatorDimension,
    IndicatorPeriod,
    IndicatorRecord,
)

ProcessorGenerator: TypeAlias = Generator[Processor, None, None]
KpiGenerator: TypeAlias = Generator[Kpi, None, None]
DatetimeGenerator: TypeAlias = Generator[datetime, None, None]
NoneGenerator: TypeAlias = Generator[None, None, None]


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


@dataclass
class DataRecord:
    indicator: type[Indicator]
    value: int
    dimension_value0: str | None
    dimension_value1: str | None = None
    dimension_value2: str | None = None

    @property
    def dimension_key(self):
        return (
            f"{self.dimension_value0}¶{self.dimension_value1}¶{self.dimension_value2}"
        )


@dataclass
class Data:
    period_ts: int
    records: list[DataRecord]


@pytest.fixture()
def kpi_dataset(dbsession: Session) -> NoneGenerator:
    datas: list[Data] = [
        Data(
            period_ts=1,
            records=[
                DataRecord(
                    indicator=ContentHomeVisit, value=10, dimension_value0="value1"
                ),
                DataRecord(
                    indicator=ContentItemVisit,
                    value=12,
                    dimension_value0="value1",
                    dimension_value1="value2",
                ),
            ],
        ),
        Data(
            period_ts=2,
            records=[
                DataRecord(
                    indicator=ContentHomeVisit, value=14, dimension_value0="value1"
                ),
                DataRecord(
                    indicator=ContentHomeVisit, value=14, dimension_value0="value2"
                ),
                DataRecord(
                    indicator=ContentItemVisit,
                    value=16,
                    dimension_value0="value1",
                    dimension_value1="value2",
                ),
            ],
        ),
        Data(
            period_ts=3,
            records=[
                DataRecord(
                    indicator=ContentHomeVisit, value=4, dimension_value0="value1"
                ),
                DataRecord(
                    indicator=ContentItemVisit,
                    value=6,
                    dimension_value0="value1",
                    dimension_value1="value2",
                ),
                DataRecord(
                    indicator=ContentItemVisit,
                    value=8,
                    dimension_value0="value1",
                    dimension_value1="value3",
                ),
            ],
        ),
        Data(
            period_ts=4,
            records=[
                DataRecord(
                    indicator=ContentHomeVisit, value=40, dimension_value0="value1"
                ),
                DataRecord(
                    indicator=ContentItemVisit,
                    value=36,
                    dimension_value0="value1",
                    dimension_value1="value4",
                ),
            ],
        ),
    ]

    dimensions = {}
    for data in datas:
        for record_data in data.records:
            if record_data.dimension_key in dimensions:
                continue
            dimension = IndicatorDimension(
                value0=record_data.dimension_value0,
                value1=record_data.dimension_value1,
                value2=record_data.dimension_value2,
            )
            dimensions[record_data.dimension_key] = dimension
            dbsession.add(dimension)

    for data in datas:
        period = IndicatorPeriod(data.period_ts)
        dbsession.add(period)
        for record_data in data.records:
            record_db = IndicatorRecord(
                indicator_id=record_data.indicator.unique_id,
                value=record_data.value,
            )
            record_db.period = period
            record_db.dimension = dimensions[record_data.dimension_key]
            dbsession.add(record_db)
    dbsession.flush()

    yield None
