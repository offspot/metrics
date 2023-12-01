from typing import Any

import pytest
from sqlalchemy.orm import Session

from offspot_metrics_backend.business.agg_kind import AggKind
from offspot_metrics_backend.business.kpis.popularity import (
    PackagePopularity,
    PackagePopularityItem,
    PackagePopularityValue,
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
