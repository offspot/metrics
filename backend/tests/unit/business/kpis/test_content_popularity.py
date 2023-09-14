from sqlalchemy.orm import Session

from offspot_metrics_backend.business.agg_kind import AggKind
from offspot_metrics_backend.business.kpis.content_popularity import (
    ContentObjectPopularity,
    ContentObjectPopularityItem,
    ContentObjectPopularityValue,
    ContentPopularity,
    ContentPopularityItem,
    ContentPopularityValue,
)

CONTENT_POPULARITY_VALUES_AS_OBJECT = ContentPopularityValue.model_validate(
    [
        ContentPopularityItem(content="value1", count=18, percentage=56.25),
        ContentPopularityItem(content="value2", count=14, percentage=43.75),
    ]
)

CONTENT_POPULARITY_VALUES_AS_DICT = [
    {"content": "value1", "count": 18, "percentage": 56.25},
    {"content": "value2", "count": 14, "percentage": 43.75},
]

CONTENT_OBJECT_POPULARITY_VALUES_AS_OBJECT = (
    ContentObjectPopularityValue.model_validate(
        [
            ContentObjectPopularityItem(
                content="value1", item="value2", count=22, percentage=73.33
            ),
            ContentObjectPopularityItem(
                content="value1", item="value3", count=8, percentage=26.67
            ),
        ]
    )
)

CONTENT_OBJECT_POPULARITY_VALUES_AS_DICT = [
    {"content": "value1", "item": "value2", "count": 22, "percentage": 73.33},
    {"content": "value1", "item": "value3", "count": 8, "percentage": 26.67},
]


def test_content_popularity_compute(
    dbsession: Session, kpi_dataset: None  # noqa: ARG001
):
    kpi = ContentPopularity()
    value = kpi.compute_value_from_indicators(
        agg_kind=AggKind.DAY, start_ts=2, stop_ts=3, session=dbsession
    )
    assert value == CONTENT_POPULARITY_VALUES_AS_OBJECT
    assert ContentPopularityValue.model_dump(value) == CONTENT_POPULARITY_VALUES_AS_DICT


def test_content_object_popularity_compute(
    dbsession: Session, kpi_dataset: None  # noqa: ARG001
):
    kpi = ContentObjectPopularity()
    value = kpi.compute_value_from_indicators(
        agg_kind=AggKind.DAY, start_ts=2, stop_ts=3, session=dbsession
    )
    assert value == CONTENT_OBJECT_POPULARITY_VALUES_AS_OBJECT
    assert (
        ContentObjectPopularityValue.model_dump(value)
        == CONTENT_OBJECT_POPULARITY_VALUES_AS_DICT
    )
