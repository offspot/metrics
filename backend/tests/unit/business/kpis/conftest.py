from collections.abc import Generator
from dataclasses import dataclass
from datetime import datetime

import pytest
from sqlalchemy.orm import Session
from tests.unit.conftest import DummyKpi

from offspot_metrics_backend.business.indicators.indicator import Indicator
from offspot_metrics_backend.business.indicators.package import (
    PackageHomeVisit,
)
from offspot_metrics_backend.business.indicators.shared_files import (
    SharedFilesOperations,
)
from offspot_metrics_backend.business.indicators.total_usage import (
    TotalUsageByPackage,
    TotalUsageOverall,
)
from offspot_metrics_backend.business.indicators.uptime import Uptime
from offspot_metrics_backend.business.inputs.shared_files import (
    SharedFilesOperationKind,
)
from offspot_metrics_backend.business.kpis.kpi import Kpi
from offspot_metrics_backend.business.kpis.processor import Processor
from offspot_metrics_backend.business.period import Period
from offspot_metrics_backend.db.models import (
    IndicatorDimension,
    IndicatorPeriod,
    IndicatorRecord,
)

type ProcessorGenerator = Generator[Processor, None, None]
type KpiGenerator = Generator[Kpi, None, None]
type DatetimeGenerator = Generator[datetime, None, None]
type NoneGenerator = Generator[None, None, None]


@pytest.fixture()
def processor(init_datetime: datetime, dbsession: Session) -> ProcessorGenerator:
    processor = Processor()
    processor.process_tick(tick_period=Period(init_datetime), session=dbsession)
    yield processor


@pytest.fixture()
def dummy_kpi() -> KpiGenerator:
    yield DummyKpi()


@dataclass
class DataRecord:
    indicator: type[Indicator]
    value: int
    dimension_value0: str | None = None
    dimension_value1: str | None = None
    dimension_value2: str | None = None

    @property
    def dimension_key(self) -> tuple[str | None, str | None, str | None]:
        return (
            self.dimension_value0,
            self.dimension_value1,
            self.dimension_value2,
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
                    indicator=PackageHomeVisit, value=10, dimension_value0="value1"
                ),
                DataRecord(
                    indicator=SharedFilesOperations,
                    value=33,
                    dimension_value0=SharedFilesOperationKind.FILE_CREATED,
                ),
                DataRecord(
                    indicator=Uptime,
                    value=57,
                ),
                DataRecord(
                    indicator=TotalUsageOverall,
                    value=40,
                ),
                DataRecord(
                    indicator=TotalUsageByPackage, value=20, dimension_value0="value1"
                ),
                DataRecord(
                    indicator=TotalUsageByPackage, value=30, dimension_value0="value2"
                ),
            ],
        ),
        Data(
            period_ts=2,
            records=[
                DataRecord(
                    indicator=PackageHomeVisit, value=14, dimension_value0="value1"
                ),
                DataRecord(
                    indicator=PackageHomeVisit, value=14, dimension_value0="value2"
                ),
                DataRecord(
                    indicator=SharedFilesOperations,
                    value=11,
                    dimension_value0=SharedFilesOperationKind.FILE_DELETED,
                ),
                DataRecord(
                    indicator=Uptime,
                    value=43,
                ),
                DataRecord(
                    indicator=TotalUsageOverall,
                    value=40,
                ),
                DataRecord(
                    indicator=TotalUsageByPackage, value=20, dimension_value0="value1"
                ),
                DataRecord(
                    indicator=TotalUsageByPackage, value=30, dimension_value0="value2"
                ),
                DataRecord(
                    indicator=TotalUsageByPackage, value=20, dimension_value0="value3"
                ),
                DataRecord(
                    indicator=TotalUsageByPackage, value=30, dimension_value0="value4"
                ),
                DataRecord(
                    indicator=TotalUsageByPackage, value=20, dimension_value0="value5"
                ),
                DataRecord(
                    indicator=TotalUsageByPackage, value=30, dimension_value0="value6"
                ),
                DataRecord(
                    indicator=TotalUsageByPackage, value=20, dimension_value0="value7"
                ),
                DataRecord(
                    indicator=TotalUsageByPackage, value=30, dimension_value0="value8"
                ),
                DataRecord(
                    indicator=TotalUsageByPackage, value=20, dimension_value0="value9"
                ),
                DataRecord(
                    indicator=TotalUsageByPackage, value=30, dimension_value0="value10"
                ),
                DataRecord(
                    indicator=TotalUsageByPackage, value=20, dimension_value0="value11"
                ),
                DataRecord(
                    indicator=TotalUsageByPackage, value=30, dimension_value0="value12"
                ),
            ],
        ),
        Data(
            period_ts=3,
            records=[
                DataRecord(
                    indicator=PackageHomeVisit, value=4, dimension_value0="value1"
                ),
            ],
        ),
        Data(
            period_ts=4,
            records=[
                DataRecord(
                    indicator=PackageHomeVisit, value=40, dimension_value0="value1"
                ),
                DataRecord(
                    indicator=SharedFilesOperations,
                    value=16,
                    dimension_value0=SharedFilesOperationKind.FILE_CREATED,
                ),
                DataRecord(
                    indicator=SharedFilesOperations,
                    value=14,
                    dimension_value0=SharedFilesOperationKind.FILE_DELETED,
                ),
                DataRecord(
                    indicator=Uptime,
                    value=11,
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
