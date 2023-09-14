from json import dumps

from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session

from offspot_metrics_backend.business.agg_kind import AggKind
from offspot_metrics_backend.business.indicators.content_visit import (
    ContentHomeVisit,
    ContentItemVisit,
)
from offspot_metrics_backend.business.kpis.kpi import Kpi
from offspot_metrics_backend.db.models import (
    IndicatorDimension,
    IndicatorPeriod,
    IndicatorRecord,
)


class ContentPopularity(Kpi):
    """A KPI which computes contents popularity

    Value is the list of all contents, sorted by nb of visits of home url/page of each
     content
    """

    unique_id = 2001

    def get_value(
        self,
        agg_kind: AggKind,  # noqa: ARG002
        start_ts: int,
        stop_ts: int,
        session: Session,
    ) -> str:
        """For a kind of aggregation (daily, weekly, ...) and a given period, return
        the KPI value."""

        total_count = session.execute(
            select(
                func.sum(IndicatorRecord.value).label("count"),
            )
            .join(IndicatorPeriod)
            .where(IndicatorRecord.indicator_id == ContentHomeVisit.unique_id)
            .where(IndicatorPeriod.timestamp >= start_ts)
            .where(IndicatorPeriod.timestamp <= stop_ts)
        ).scalar_one()

        subquery = (
            select(
                IndicatorDimension.value0.label("content"),
                func.sum(IndicatorRecord.value).label("count"),
            )
            .join(IndicatorRecord)
            .join(IndicatorPeriod)
            .where(IndicatorRecord.indicator_id == ContentHomeVisit.unique_id)
            .where(IndicatorPeriod.timestamp >= start_ts)
            .where(IndicatorPeriod.timestamp <= stop_ts)
            .group_by("content")
        ).subquery("content_with_count")

        query = select(subquery.c.count, subquery.c.content).order_by(
            desc(subquery.c.count), subquery.c.content
        )

        return dumps(
            [
                {
                    "content": record.content,
                    "count": record.count,
                    "percentage": round(int(str(record.count)) * 100 / total_count, 2),
                }
                for record in session.execute(query)
            ]
        )


class ContentObjectPopularity(Kpi):
    """A KPI which computes content objects popularity

    Value is the top 50 list of all objects (content name + object name), sorted by nb
    of visits
    """

    unique_id = 2002

    def get_value(
        self,
        agg_kind: AggKind,  # noqa: ARG002
        start_ts: int,
        stop_ts: int,
        session: Session,
    ) -> str:
        """For a kind of aggregation (daily, weekly, ...) and a given period, return
        the KPI value."""

        total_count = session.execute(
            select(
                func.sum(IndicatorRecord.value).label("count"),
            )
            .join(IndicatorPeriod)
            .where(IndicatorRecord.indicator_id == ContentItemVisit.unique_id)
            .where(IndicatorPeriod.timestamp >= start_ts)
            .where(IndicatorPeriod.timestamp <= stop_ts)
        ).scalar_one()

        subquery = (
            select(
                IndicatorDimension.value0.label("content"),
                IndicatorDimension.value1.label("item"),
                func.sum(IndicatorRecord.value).label("count"),
            )
            .join(IndicatorRecord)
            .join(IndicatorPeriod)
            .where(IndicatorRecord.indicator_id == ContentItemVisit.unique_id)
            .where(IndicatorPeriod.timestamp >= start_ts)
            .where(IndicatorPeriod.timestamp <= stop_ts)
            .group_by("content", "item")
        ).subquery("content_with_count")

        query = (
            select(subquery.c.count, subquery.c.content, subquery.c.item)
            .order_by(desc(subquery.c.count), subquery.c.content, subquery.c.item)
            .limit(50)
        )

        return dumps(
            [
                {
                    "content": record.content,
                    "item": record.item,
                    "count": record.count,
                    "percentage": round(int(str(record.count)) * 100 / total_count, 2),
                }
                for record in session.execute(query)
            ]
        )
