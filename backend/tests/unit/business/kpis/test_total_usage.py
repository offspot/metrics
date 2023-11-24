from typing import Any

import pytest
from sqlalchemy.orm import Session

from offspot_metrics_backend.business.agg_kind import AggKind
from offspot_metrics_backend.business.kpis.total_usage import (
    TotalUsage,
    TotalUsageItem,
    TotalUsageValue,
)


@pytest.fixture
def content_usage_duration_value_as_object_1() -> TotalUsageValue:
    return TotalUsageValue(
        items=[
            TotalUsageItem(package="value2", minutes_activity=30),
            TotalUsageItem(package="value1", minutes_activity=20),
        ],
        total_minutes_activity=40,
    )


@pytest.fixture
def content_usage_duration_value_as_object_2() -> TotalUsageValue:
    return TotalUsageValue(
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


@pytest.fixture
def content_usage_duration_value_as_object_3() -> TotalUsageValue:
    return TotalUsageValue(
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


@pytest.fixture
def content_usage_duration_value_as_dict() -> dict[str, Any]:
    return {
        "items": [
            {"package": "value2", "minutes_activity": 30},
            {"package": "value1", "minutes_activity": 20},
        ],
        "total_minutes_activity": 40,
    }


def test_total_usage_compute_1(
    content_usage_duration_value_as_object_1: TotalUsageValue,
    content_usage_duration_value_as_dict: dict[str, Any],
    dbsession: Session,
    kpi_dataset: None,  # noqa: ARG001
):
    kpi = TotalUsage()
    value = kpi.compute_value_from_indicators(
        agg_kind=AggKind.DAY, start_ts=1, stop_ts=1, session=dbsession
    )
    assert value == content_usage_duration_value_as_object_1
    assert TotalUsageValue.model_dump(value) == content_usage_duration_value_as_dict


def test_total_usage_compute_2(
    content_usage_duration_value_as_object_2: TotalUsageValue,
    dbsession: Session,
    kpi_dataset: None,  # noqa: ARG001
):
    kpi = TotalUsage()
    value = kpi.compute_value_from_indicators(
        agg_kind=AggKind.DAY, start_ts=2, stop_ts=2, session=dbsession
    )
    assert value == content_usage_duration_value_as_object_2


def test_total_usage_compute_3(
    content_usage_duration_value_as_object_3: TotalUsageValue,
    dbsession: Session,
    kpi_dataset: None,  # noqa: ARG001
):
    kpi = TotalUsage()
    value = kpi.compute_value_from_indicators(
        agg_kind=AggKind.DAY, start_ts=1, stop_ts=2, session=dbsession
    )
    assert value == content_usage_duration_value_as_object_3
