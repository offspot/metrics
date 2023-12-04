from pydantic import BaseModel
from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session

from offspot_metrics_backend.business.agg_kind import AggKind
from offspot_metrics_backend.business.indicators.package import (
    PackageHomeVisit,
)
from offspot_metrics_backend.business.kpis.kpi import Kpi
from offspot_metrics_backend.db.models import (
    IndicatorDimension,
    IndicatorPeriod,
    IndicatorRecord,
    KpiValue,
)


class PackagePopularityItem(BaseModel):
    package: str
    visits: int


class PackagePopularityValue(BaseModel, KpiValue):
    items: list[PackagePopularityItem]
    total_visits: int


class PackagePopularity(Kpi):
    """A KPI which computes package popularity

    Value is the list of all packages, sorted by nb of visits of home url/page of each
     content
    """

    unique_id = 2001

    # the KPI will hold only the top packages
    top_count = 10

    def compute_value_from_indicators(
        self,
        agg_kind: AggKind,  # noqa: ARG002
        start_ts: int,
        stop_ts: int,
        session: Session,
    ) -> PackagePopularityValue:
        """For a kind of aggregation (daily, weekly, ...) and a given period, return
        the KPI value."""

        total_count = session.execute(
            select(
                func.sum(IndicatorRecord.value).label("count"),
            )
            .join(IndicatorPeriod)
            .where(IndicatorRecord.indicator_id == PackageHomeVisit.unique_id)
            .where(IndicatorPeriod.timestamp >= start_ts)
            .where(IndicatorPeriod.timestamp <= stop_ts)
        ).scalar_one()

        subquery = (
            select(
                IndicatorDimension.value0.label("package"),
                func.sum(IndicatorRecord.value).label("package_count"),
            )
            .join(IndicatorRecord)
            .join(IndicatorPeriod)
            .where(IndicatorRecord.indicator_id == PackageHomeVisit.unique_id)
            .where(IndicatorPeriod.timestamp >= start_ts)
            .where(IndicatorPeriod.timestamp <= stop_ts)
            .group_by("package")
        ).subquery("packages")

        query = (
            select(subquery.c.package_count, subquery.c.package)
            .order_by(desc(subquery.c.package_count), subquery.c.package)
            .limit(PackagePopularity.top_count)
        )

        return PackagePopularityValue(
            items=[
                PackagePopularityItem(
                    package=record.package,
                    visits=record.package_count,
                )
                for record in session.execute(query)
            ],
            total_visits=total_count or 0,
        )
