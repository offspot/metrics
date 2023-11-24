from typing import Any

import pytest
from sqlalchemy.orm import Session

from offspot_metrics_backend.business.agg_kind import AggKind
from offspot_metrics_backend.business.kpis.popularity import (
    PackagePopularity,
    PackagePopularityItem,
    PackagePopularityValue,
    PopularPages,
    PopularPagesItem,
    PopularPagesValue,
)


@pytest.fixture
def content_popularity_values_as_object() -> PackagePopularityValue:
    return PackagePopularityValue(
        items=[
            PackagePopularityItem(package="value1", visits=18),
            PackagePopularityItem(package="value2", visits=14),
        ],
        total_visits=32,
    )


@pytest.fixture
def content_popularity_values_as_dict() -> dict[str, Any]:
    return {
        "items": [
            {"package": "value1", "visits": 18},
            {"package": "value2", "visits": 14},
        ],
        "total_visits": 32,
    }


@pytest.fixture
def content_object_popularity_values_as_object() -> PopularPagesValue:
    return PopularPagesValue(
        items=[
            PopularPagesItem(package="value1", item="value2", visits=22),
            PopularPagesItem(package="value1", item="value3", visits=8),
        ],
        total_visits=30,
    )


@pytest.fixture
def content_object_popularity_values_as_dict() -> dict[str, Any]:
    return {
        "items": [
            {"package": "value1", "item": "value2", "visits": 22},
            {"package": "value1", "item": "value3", "visits": 8},
        ],
        "total_visits": 30,
    }


def test_content_popularity_compute(
    content_popularity_values_as_object: PackagePopularityValue,
    content_popularity_values_as_dict: dict[str, Any],
    dbsession: Session,
    kpi_dataset: None,  # noqa: ARG001
):
    kpi = PackagePopularity()
    value = kpi.compute_value_from_indicators(
        agg_kind=AggKind.DAY, start_ts=2, stop_ts=3, session=dbsession
    )
    assert value == content_popularity_values_as_object
    assert PackagePopularityValue.model_dump(value) == content_popularity_values_as_dict


def test_content_object_popularity_compute(
    content_object_popularity_values_as_object: PackagePopularityValue,
    content_object_popularity_values_as_dict: dict[str, Any],
    dbsession: Session,
    kpi_dataset: None,  # noqa: ARG001
):
    kpi = PopularPages()
    value = kpi.compute_value_from_indicators(
        agg_kind=AggKind.DAY, start_ts=2, stop_ts=3, session=dbsession
    )
    assert value == content_object_popularity_values_as_object
    assert (
        PopularPagesValue.model_dump(value) == content_object_popularity_values_as_dict
    )
