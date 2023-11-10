from typing import Any

from sqlalchemy.orm import Session

from offspot_metrics_backend.business.agg_kind import AggKind
from offspot_metrics_backend.business.kpis.total_usage import (
    TotalUsage,
    TotalUsageItem,
    TotalUsageValue,
)

CONTENT_USAGE_DURATION_VALUE_AS_OBJECT_1 = TotalUsageValue(
    items=[
        TotalUsageItem(package="value2", minutes_activity=30),
        TotalUsageItem(package="value1", minutes_activity=20),
    ],
    total_minutes_activity=40,
)

CONTENT_USAGE_DURATION_VALUE_AS_OBJECT_2 = TotalUsageValue(
    items=[
        TotalUsageItem(package="value10", minutes_activity=30),
        TotalUsageItem(package="value12", minutes_activity=30),
        TotalUsageItem(package="value2", minutes_activity=30),
        TotalUsageItem(package="value4", minutes_activity=30),
        TotalUsageItem(package="value6", minutes_activity=30),
        TotalUsageItem(package="value8", minutes_activity=30),
        TotalUsageItem(package="value1", minutes_activity=20),
        TotalUsageItem(package="value11", minutes_activity=20),
        TotalUsageItem(package="value3", minutes_activity=20),
        TotalUsageItem(package="value5", minutes_activity=20),
    ],
    total_minutes_activity=40,
)

CONTENT_USAGE_DURATION_VALUE_AS_OBJECT_3 = TotalUsageValue(
    items=[
        TotalUsageItem(package="value2", minutes_activity=60),
        TotalUsageItem(package="value1", minutes_activity=40),
        TotalUsageItem(package="value10", minutes_activity=30),
        TotalUsageItem(package="value12", minutes_activity=30),
        TotalUsageItem(package="value4", minutes_activity=30),
        TotalUsageItem(package="value6", minutes_activity=30),
        TotalUsageItem(package="value8", minutes_activity=30),
        TotalUsageItem(package="value11", minutes_activity=20),
        TotalUsageItem(package="value3", minutes_activity=20),
        TotalUsageItem(package="value5", minutes_activity=20),
    ],
    total_minutes_activity=80,
)

CONTENT_USAGE_DURATION_AS_DICT: dict[str, Any] = {
    "items": [
        {"package": "value2", "minutes_activity": 30},
        {"package": "value1", "minutes_activity": 20},
    ],
    "total_minutes_activity": 40,
}


def test_total_usage_compute_1(dbsession: Session, kpi_dataset: None):  # noqa: ARG001
    kpi = TotalUsage()
    value = kpi.compute_value_from_indicators(
        agg_kind=AggKind.DAY, start_ts=1, stop_ts=1, session=dbsession
    )
    assert value == CONTENT_USAGE_DURATION_VALUE_AS_OBJECT_1
    assert TotalUsageValue.model_dump(value) == CONTENT_USAGE_DURATION_AS_DICT


def test_total_usage_compute_2(dbsession: Session, kpi_dataset: None):  # noqa: ARG001
    kpi = TotalUsage()
    value = kpi.compute_value_from_indicators(
        agg_kind=AggKind.DAY, start_ts=2, stop_ts=2, session=dbsession
    )
    assert value == CONTENT_USAGE_DURATION_VALUE_AS_OBJECT_2


def test_total_usage_compute_3(dbsession: Session, kpi_dataset: None):  # noqa: ARG001
    kpi = TotalUsage()
    value = kpi.compute_value_from_indicators(
        agg_kind=AggKind.DAY, start_ts=1, stop_ts=2, session=dbsession
    )
    assert value == CONTENT_USAGE_DURATION_VALUE_AS_OBJECT_3
