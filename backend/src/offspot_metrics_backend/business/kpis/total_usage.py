from pydantic import BaseModel
from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session

from offspot_metrics_backend.business.agg_kind import AggKind
from offspot_metrics_backend.business.indicators.total_usage import (
    TotalUsageByPackage,
    TotalUsageOverall,
)
from offspot_metrics_backend.business.kpis.kpi import Kpi
from offspot_metrics_backend.db.models import (
    IndicatorDimension,
    IndicatorPeriod,
    IndicatorRecord,
    KpiValue,
)


class TotalUsageItem(BaseModel):
    package: str
    minutes_activity: int


class TotalUsageValue(BaseModel, KpiValue):
    items: list[TotalUsageItem]
    total_minutes_activity: int


class TotalUsage(Kpi):
    """A KPI which measures the usage (in minutes) of a given package + total value

    Value is:
     - the total minutes of activity (all packages, note this is different from the
     sum of individual value)
     - the top 10 list of all packages, sorted by nb of minutes of activity
    """

    unique_id = 2003

    # the KPI will hold only the top packages
    top_count = 10

    def compute_value_from_indicators(
        self,
        agg_kind: AggKind,  # noqa: ARG002
        start_ts: int,
        stop_ts: int,
        session: Session,
    ) -> TotalUsageValue:
        """For a kind of aggregation (daily, weekly, ...) and a given period, return
        the KPI value."""

        total_usage = session.execute(
            select(
                func.sum(IndicatorRecord.value).label("count"),
            )
            .join(IndicatorPeriod)
            .where(IndicatorRecord.indicator_id == TotalUsageOverall.unique_id)
            .where(IndicatorPeriod.timestamp >= start_ts)
            .where(IndicatorPeriod.timestamp <= stop_ts)
        ).scalar_one()

        subquery = (
            select(
                IndicatorDimension.value0.label("package"),
                func.sum(IndicatorRecord.value).label("usage"),
            )
            .join(IndicatorRecord)
            .join(IndicatorPeriod)
            .where(IndicatorRecord.indicator_id == TotalUsageByPackage.unique_id)
            .where(IndicatorPeriod.timestamp >= start_ts)
            .where(IndicatorPeriod.timestamp <= stop_ts)
            .group_by("package")
        ).subquery("package_with_usage")

        query = (
            select(subquery.c.usage, subquery.c.package)
            .order_by(desc(subquery.c.usage), subquery.c.package)
            .limit(TotalUsage.top_count)
        )

        return TotalUsageValue(
            total_minutes_activity=total_usage,
            items=[
                TotalUsageItem(package=record.package, minutes_activity=record.usage)
                for record in session.execute(query)
            ],
        )
