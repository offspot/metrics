from typing import Any

import pytest
from sqlalchemy.orm import Session

from offspot_metrics_backend.business.agg_kind import AggKind
from offspot_metrics_backend.business.kpis.uptime import (
    Uptime,
    UptimeValue,
)


@pytest.fixture
def offspot_usage_duration_value_as_object_1() -> UptimeValue:
    return UptimeValue(nb_minutes_on=57)


@pytest.fixture
def offspot_usage_duration_value_as_object_2() -> UptimeValue:
    return UptimeValue(nb_minutes_on=100)


@pytest.fixture
def offspot_usage_duration_value_as_object_3() -> UptimeValue:
    return UptimeValue(nb_minutes_on=111)


@pytest.fixture
def offspot_usage_duration_as_dict_1() -> dict[str, Any]:
    return {"nb_minutes_on": 57}


def test_uptime_compute_1(
    offspot_usage_duration_value_as_object_1: UptimeValue,
    offspot_usage_duration_as_dict_1: dict[str, Any],
    dbsession: Session,
    kpi_dataset: None,  # noqa: ARG001
):
    kpi = Uptime()
    value = kpi.compute_value_from_indicators(
        agg_kind=AggKind.DAY, start_ts=1, stop_ts=1, session=dbsession
    )
    assert value == offspot_usage_duration_value_as_object_1
    assert UptimeValue.model_dump(value) == offspot_usage_duration_as_dict_1


def test_uptime_compute_2(
    offspot_usage_duration_value_as_object_2: UptimeValue,
    dbsession: Session,
    kpi_dataset: None,  # noqa: ARG001
):
    kpi = Uptime()
    value = kpi.compute_value_from_indicators(
        agg_kind=AggKind.DAY, start_ts=1, stop_ts=2, session=dbsession
    )
    assert value == offspot_usage_duration_value_as_object_2


def test_uptime_compute_3(
    offspot_usage_duration_value_as_object_2: UptimeValue,
    dbsession: Session,
    kpi_dataset: None,  # noqa: ARG001
):
    kpi = Uptime()
    value = kpi.compute_value_from_indicators(
        agg_kind=AggKind.DAY, start_ts=1, stop_ts=3, session=dbsession
    )
    assert value == offspot_usage_duration_value_as_object_2


def test_uptime_compute_4(
    offspot_usage_duration_value_as_object_3: UptimeValue,
    dbsession: Session,
    kpi_dataset: None,  # noqa: ARG001
):
    kpi = Uptime()
    value = kpi.compute_value_from_indicators(
        agg_kind=AggKind.DAY, start_ts=1, stop_ts=4, session=dbsession
    )
    assert value == offspot_usage_duration_value_as_object_3
