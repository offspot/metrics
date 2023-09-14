from sqlalchemy.orm import Session

from offspot_metrics_backend.business.agg_kind import AggKind
from offspot_metrics_backend.business.kpis.content_popularity import (
    ContentObjectPopularity,
    ContentObjectPopularityValue,
    ContentPopularity,
    ContentPopularityValue,
)

CONTENT_POPULARITY_VALUES_AS_OBJECT = [
    ContentPopularityValue(content="value1", count=18, percentage=56.25),
    ContentPopularityValue(content="value2", count=14, percentage=43.75),
]

CONTENT_POPULARITY_VALUES_AS_STRING = (
    '[{"content": "value1", "count": 18, "percentage": 56.25}, {"content": "value2", '
    '"count": 14, "percentage": 43.75}]'
)

CONTENT_OBJECT_POPULARITY_VALUES_AS_OBJECT = [
    ContentObjectPopularityValue(
        content="value1", item="value2", count=22, percentage=73.33
    ),
    ContentObjectPopularityValue(
        content="value1", item="value3", count=8, percentage=26.67
    ),
]

CONTENT_OBJECT_POPULARITY_VALUES_AS_STRING = (
    '[{"content": "value1", "item": "value2", "count": 22, "percentage": 73.33}, '
    '{"content": "value1", "item": "value3", "count": 8, "percentage": 26.67}]'
)


def test_content_popularity_compute(
    dbsession: Session, kpi_dataset: None  # noqa: ARG001
):
    kpi = ContentPopularity()
    assert (
        kpi.compute_value_from_indicators(
            agg_kind=AggKind.DAY, start_ts=2, stop_ts=3, session=dbsession
        )
        == CONTENT_POPULARITY_VALUES_AS_OBJECT
    )


def test_content_popularity_load(dbsession: Session, kpi_dataset: None):  # noqa: ARG001
    kpi = ContentPopularity()
    assert (
        kpi.loads_value(CONTENT_POPULARITY_VALUES_AS_STRING)
        == CONTENT_POPULARITY_VALUES_AS_OBJECT
    )


def test_content_popularity_dump(dbsession: Session, kpi_dataset: None):  # noqa: ARG001
    kpi = ContentPopularity()
    assert (
        kpi.dumps_value(CONTENT_POPULARITY_VALUES_AS_OBJECT)
        == CONTENT_POPULARITY_VALUES_AS_STRING
    )


def test_content_object_popularity_compute(
    dbsession: Session, kpi_dataset: None  # noqa: ARG001
):
    kpi = ContentObjectPopularity()
    assert (
        kpi.compute_value_from_indicators(
            agg_kind=AggKind.DAY, start_ts=2, stop_ts=3, session=dbsession
        )
        == CONTENT_OBJECT_POPULARITY_VALUES_AS_OBJECT
    )


def test_content_object_popularity_load():
    kpi = ContentObjectPopularity()
    assert (
        kpi.loads_value(CONTENT_OBJECT_POPULARITY_VALUES_AS_STRING)
        == CONTENT_OBJECT_POPULARITY_VALUES_AS_OBJECT
    )


def test_content_object_popularity_dump():
    kpi = ContentObjectPopularity()
    assert (
        kpi.dumps_value(CONTENT_OBJECT_POPULARITY_VALUES_AS_OBJECT)
        == CONTENT_OBJECT_POPULARITY_VALUES_AS_STRING
    )
