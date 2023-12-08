from sqlalchemy import func, select
from sqlalchemy.orm import Session

from offspot_metrics_backend.business.agg_kind import AggKind
from offspot_metrics_backend.business.indicators.uptime import Uptime as UptimeIndicator
from offspot_metrics_backend.business.kpis.kpi import Kpi
from offspot_metrics_backend.db.models import (
    IndicatorPeriod,
    IndicatorRecord,
    KpiValue,
)


class UptimeValue(KpiValue):
    nb_minutes_on: int


class Uptime(Kpi):
    """A KPI which measures the uptime (in minutes) of the offspot

    Value is a single measure for the period
    """

    unique_id = 2004

    def compute_value_from_indicators(
        self,
        agg_kind: AggKind,  # noqa: ARG002
        start_ts: int,
        stop_ts: int,
        session: Session,
    ) -> UptimeValue:
        """For a kind of aggregation (daily, weekly, ...) and a given period, return
        the KPI value."""

        uptime = session.execute(
            select(
                func.sum(IndicatorRecord.value).label("total"),
            )
            .join(IndicatorPeriod)
            .where(IndicatorRecord.indicator_id == UptimeIndicator.unique_id)
            .where(IndicatorPeriod.timestamp >= start_ts)
            .where(IndicatorPeriod.timestamp <= stop_ts)
        ).scalar_one_or_none()

        return UptimeValue(nb_minutes_on=uptime or 0)
