from sqlalchemy.orm import Session

from offspot_metrics_backend.business.agg_kind import AggKind
from offspot_metrics_backend.business.kpis.content_popularity import (
    ContentObjectPopularity,
    ContentPopularity,
)


def test_content_popularity(dbsession: Session, kpi_dataset: None):  # noqa: ARG001
    kpi = ContentPopularity()
    assert kpi.get_value(
        agg_kind=AggKind.DAY, start_ts=2, stop_ts=3, session=dbsession
    ) == (
        '[{"content": "value1", "count": 18, "percentage": 56.25}, {"content": '
        '"value2", "count": 14, "percentage": 43.75}]'
    )


def test_content_object_popularity(
    dbsession: Session, kpi_dataset: None  # noqa: ARG001
):
    kpi = ContentObjectPopularity()
    assert kpi.get_value(
        agg_kind=AggKind.DAY, start_ts=2, stop_ts=3, session=dbsession
    ) == (
        '[{"content": "value1", "item": "value2", "count": 22, "percentage": 73.33}, '
        '{"content": "value1", "item": "value3", "count": 8, "percentage": 26.67}]'
    )
