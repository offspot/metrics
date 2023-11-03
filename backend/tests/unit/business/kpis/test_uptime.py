from sqlalchemy.orm import Session

from offspot_metrics_backend.business.agg_kind import AggKind
from offspot_metrics_backend.business.kpis.uptime import (
    Uptime,
    UptimeValue,
)

OFFSPOT_USAGE_DURATION_VALUE_AS_OBJECT_1 = UptimeValue(nb_minutes_on=57)
OFFSPOT_USAGE_DURATION_VALUE_AS_OBJECT_2 = UptimeValue(nb_minutes_on=100)
OFFSPOT_USAGE_DURATION_VALUE_AS_OBJECT_3 = UptimeValue(nb_minutes_on=100)
OFFSPOT_USAGE_DURATION_VALUE_AS_OBJECT_4 = UptimeValue(nb_minutes_on=111)

OFFSPOT_USAGE_DURATION_AS_DICT_1 = {"nb_minutes_on": 57}


def test_uptime_compute(dbsession: Session, kpi_dataset: None):  # noqa: ARG001
    kpi = Uptime()
    value = kpi.compute_value_from_indicators(
        agg_kind=AggKind.DAY, start_ts=1, stop_ts=1, session=dbsession
    )
    assert value == OFFSPOT_USAGE_DURATION_VALUE_AS_OBJECT_1
    assert UptimeValue.model_dump(value) == OFFSPOT_USAGE_DURATION_AS_DICT_1

    value = kpi.compute_value_from_indicators(
        agg_kind=AggKind.DAY, start_ts=1, stop_ts=2, session=dbsession
    )
    assert value == OFFSPOT_USAGE_DURATION_VALUE_AS_OBJECT_2

    value = kpi.compute_value_from_indicators(
        agg_kind=AggKind.DAY, start_ts=1, stop_ts=3, session=dbsession
    )
    assert value == OFFSPOT_USAGE_DURATION_VALUE_AS_OBJECT_3

    value = kpi.compute_value_from_indicators(
        agg_kind=AggKind.DAY, start_ts=1, stop_ts=4, session=dbsession
    )
    assert value == OFFSPOT_USAGE_DURATION_VALUE_AS_OBJECT_4
