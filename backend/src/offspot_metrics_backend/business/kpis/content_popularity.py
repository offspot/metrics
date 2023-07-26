from json import dumps

from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session

from offspot_metrics_backend.business.agg_kind import AggKind
from offspot_metrics_backend.business.indicators.content_visit import (
    ContentHomeVisit,
    ContentObjectVisit,
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
        self, agg_kind: AggKind, start_ts: int, stop_ts: int, session: Session
    ) -> str:
        """For a kind of aggregation (daily, weekly, ...) and a given period, return
        the KPI value."""

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

        query = select(subquery.c.content).order_by(
            desc(subquery.c.count), subquery.c.content
        )

        return dumps(list(session.execute(query).scalars()))


class ContentObjectPopularity(Kpi):
    """A KPI which computes content objects popularity

    Value is the top 50 list of all objects (content name + object name), sorted by nb
    of visits
    """

    unique_id = 2002

    def get_value(
        self, agg_kind: AggKind, start_ts: int, stop_ts: int, session: Session
    ) -> str:
        """For a kind of aggregation (daily, weekly, ...) and a given period, return
        the KPI value."""

        subquery = (
            select(
                IndicatorDimension.value0.label("content"),
                IndicatorDimension.value1.label("object"),
                func.sum(IndicatorRecord.value).label("count"),
            )
            .join(IndicatorRecord)
            .join(IndicatorPeriod)
            .where(IndicatorRecord.indicator_id == ContentObjectVisit.unique_id)
            .where(IndicatorPeriod.timestamp >= start_ts)
            .where(IndicatorPeriod.timestamp <= stop_ts)
            .group_by("content", "object")
        ).subquery("content_with_count")

        query = (
            select(subquery.c.content, subquery.c.object)
            .order_by(desc(subquery.c.count), subquery.c.content, subquery.c.object)
            .limit(50)
        )

        return dumps(
            [
                {
                    "content": record.content,
                    "object": record.object,
                }
                for record in session.execute(query)
            ]
        )
