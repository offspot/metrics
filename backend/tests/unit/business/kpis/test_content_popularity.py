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

CONTENT_POPULARITY_VALUES_AS_OBJECT = PackagePopularityValue(
    items=[
        PackagePopularityItem(package="value1", visits=18),
        PackagePopularityItem(package="value2", visits=14),
    ],
    total_visits=32,
)

CONTENT_POPULARITY_VALUES_AS_DICT = {
    "items": [
        {"package": "value1", "visits": 18},
        {"package": "value2", "visits": 14},
    ],
    "total_visits": 32,
}

CONTENT_OBJECT_POPULARITY_VALUES_AS_OBJECT = PopularPagesValue(
    items=[
        PopularPagesItem(package="value1", item="value2", visits=22),
        PopularPagesItem(package="value1", item="value3", visits=8),
    ],
    total_visits=30,
)

CONTENT_OBJECT_POPULARITY_VALUES_AS_DICT = {
    "items": [
        {"package": "value1", "item": "value2", "visits": 22},
        {"package": "value1", "item": "value3", "visits": 8},
    ],
    "total_visits": 30,
}


def test_content_popularity_compute(
    dbsession: Session, kpi_dataset: None  # noqa: ARG001
):
    kpi = PackagePopularity()
    value = kpi.compute_value_from_indicators(
        agg_kind=AggKind.DAY, start_ts=2, stop_ts=3, session=dbsession
    )
    assert value == CONTENT_POPULARITY_VALUES_AS_OBJECT
    assert PackagePopularityValue.model_dump(value) == CONTENT_POPULARITY_VALUES_AS_DICT


def test_content_object_popularity_compute(
    dbsession: Session, kpi_dataset: None  # noqa: ARG001
):
    kpi = PopularPages()
    value = kpi.compute_value_from_indicators(
        agg_kind=AggKind.DAY, start_ts=2, stop_ts=3, session=dbsession
    )
    assert value == CONTENT_OBJECT_POPULARITY_VALUES_AS_OBJECT
    assert (
        PopularPagesValue.model_dump(value) == CONTENT_OBJECT_POPULARITY_VALUES_AS_DICT
    )
