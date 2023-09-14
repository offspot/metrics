from dataclasses import dataclass
from typing import cast

# from desert import schema
from marshmallow_dataclass import class_schema as schema
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


@dataclass
class ContentPopularityValue:
    content: str
    count: int
    percentage: float


class ContentPopularity(Kpi):
    """A KPI which computes contents popularity

    Value is the list of all contents, sorted by nb of visits of home url/page of each
     content
    """

    unique_id = 2001

    def compute_value_from_indicators(
        self,
        agg_kind: AggKind,  # noqa: ARG002
        start_ts: int,
        stop_ts: int,
        session: Session,
    ) -> list[ContentPopularityValue]:
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
                func.sum(IndicatorRecord.value).label("content_count"),
            )
            .join(IndicatorRecord)
            .join(IndicatorPeriod)
            .where(IndicatorRecord.indicator_id == ContentHomeVisit.unique_id)
            .where(IndicatorPeriod.timestamp >= start_ts)
            .where(IndicatorPeriod.timestamp <= stop_ts)
            .group_by("content")
        ).subquery("content_with_count")

        query = select(subquery.c.content_count, subquery.c.content).order_by(
            desc(subquery.c.content_count), subquery.c.content
        )

        return [
            ContentPopularityValue(
                content=record.content,
                count=record.content_count,
                percentage=round(int(str(record.content_count)) * 100 / total_count, 2),
            )
            for record in session.execute(query)
        ]

    def loads_value(self, value: str) -> list[ContentPopularityValue]:
        """Loads the KPI value from a serialized string"""
        return cast(
            list[ContentPopularityValue],
            schema(
                ContentPopularityValue
            )().loads(  # pyright: ignore[reportUnknownMemberType]
                value, many=True
            ),
        )

    def dumps_value(self, value: list[ContentPopularityValue]) -> str:
        """Dump the KPI value into a serialized string"""
        return cast(
            str,
            schema(
                ContentPopularityValue
            )().dumps(  # pyright: ignore[reportUnknownMemberType]
                value, many=True
            ),
        )


@dataclass
class ContentObjectPopularityValue:
    content: str
    item: str
    count: int
    percentage: float


class ContentObjectPopularity(Kpi):
    """A KPI which computes content objects popularity

    Value is the top 50 list of all objects (content name + object name), sorted by nb
    of visits
    """

    unique_id = 2002
    value_schema = schema(ContentObjectPopularityValue)

    def compute_value_from_indicators(
        self,
        agg_kind: AggKind,  # noqa: ARG002
        start_ts: int,
        stop_ts: int,
        session: Session,
    ) -> list[ContentObjectPopularityValue]:
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
                func.sum(IndicatorRecord.value).label("item_count"),
            )
            .join(IndicatorRecord)
            .join(IndicatorPeriod)
            .where(IndicatorRecord.indicator_id == ContentItemVisit.unique_id)
            .where(IndicatorPeriod.timestamp >= start_ts)
            .where(IndicatorPeriod.timestamp <= stop_ts)
            .group_by("content", "item")
        ).subquery("content_with_count")

        query = (
            select(subquery.c.item_count, subquery.c.content, subquery.c.item)
            .order_by(desc(subquery.c.item_count), subquery.c.content, subquery.c.item)
            .limit(50)
        )

        return [
            ContentObjectPopularityValue(
                content=record.content,
                item=record.item,
                count=record.item_count,
                percentage=round(int(str(record.item_count)) * 100 / total_count, 2),
            )
            for record in session.execute(query)
        ]

    def loads_value(self, value: str) -> list[ContentObjectPopularityValue]:
        """Loads the KPI value from a serialized string"""
        return cast(
            list[ContentObjectPopularityValue],
            schema(
                ContentObjectPopularityValue
            )().loads(  # pyright: ignore[reportUnknownMemberType]
                value, many=True
            ),
        )

    def dumps_value(self, value: list[ContentObjectPopularityValue]) -> str:
        """Dump the KPI value into a serialized string"""
        return cast(
            str,
            schema(
                ContentObjectPopularityValue
            )().dumps(  # pyright: ignore[reportUnknownMemberType]
                value, many=True
            ),
        )
