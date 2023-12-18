from typing import Annotated

from dateutil.relativedelta import relativedelta
from fastapi import APIRouter, Path
from sqlalchemy import select

from offspot_metrics_backend.business.agg_kind import AggKind
from offspot_metrics_backend.business.period import Period
from offspot_metrics_backend.db.models import KpiRecord
from offspot_metrics_backend.routes import DbSession
from offspot_metrics_backend.routes.schemas import (
    Aggregation,
    Aggregations,
    AggregationsByKind,
)

router = APIRouter(
    prefix="/aggregations",
    tags=["all"],
)


@router.get(
    "",
    status_code=200,
    responses={
        200: {
            "description": "Returns the list of available aggregations",
        },
    },
)
def aggregations(
    session: DbSession,
) -> Aggregations:
    query = (
        select(KpiRecord.agg_kind, KpiRecord.agg_value)
        .order_by(KpiRecord.agg_kind)
        .order_by(KpiRecord.agg_value)
        .distinct()
    )

    return Aggregations(
        aggregations=[
            Aggregation(kind=record.agg_kind, value=record.agg_value)
            for record in session.execute(query)
        ]
    )


@router.get(
    "/{agg_kind}",
    status_code=200,
    responses={
        200: {
            "description": "Returns data for all aggregations of a given kind",
        },
    },
)
def aggregation_by_kind(
    agg_kind: Annotated[str, Path(pattern=AggKind.pattern())],
    session: DbSession,
) -> AggregationsByKind:
    query = select(KpiRecord.agg_value, KpiRecord.kpi_id, KpiRecord.kpi_value).where(
        KpiRecord.agg_kind == agg_kind
    )

    records = session.execute(query).all()

    agg_values = sorted({record.agg_value for record in records})
    kpi_ids = sorted({record.kpi_id for record in records})

    return AggregationsByKind(
        agg_kind=AggKind(agg_kind),
        values_available=agg_values,
        values_all=get_all_values(
            agg_kind=AggKind(agg_kind), values_available=agg_values
        ),
        kpis=[
            AggregationsByKind.KpiValues(
                kpi_id=kpi_id,
                values=sorted(
                    [
                        AggregationsByKind.KpiValueByAggregation(
                            agg_value=record.agg_value, kpi_value=record.kpi_value
                        )
                        for record in records
                        if record.kpi_id == kpi_id
                    ],
                    key=lambda value: value.agg_value,
                ),
            )
            for kpi_id in kpi_ids
        ],
    )


def get_all_values(agg_kind: AggKind, values_available: list[str]) -> list[str]:
    """returns all potential values for current aggregation

    This is computed based on the values available (last one, except for yearly where
    we keep all aggregations)

    This allows to create graphs more easily, not taking into account which aggregations
    might be missing due to metrics shutdown.

    All values is:
    - the last 7 days up to last value available if kind is day
    - the last 4 weeks up to last value available if kind is week
    - the last 3 months up to last value available if kind is month
    - all years from first to last value available if kind is year
    - empty if no values are available

    Example: if agg_kind is "D" and last value available is "2023-11-21", this will
    return the 7 days from "2023-11-15" up to "2023-11-21"

    """
    if len(values_available) == 0:
        return values_available
    last_day = Period.from_truncated_value(values_available[-1], agg_kind=agg_kind)
    if agg_kind == AggKind.YEAR:
        return [
            str(year)
            for year in range(int(values_available[0]), int(values_available[-1]) + 1)
        ]  # all years from first to last
    elif agg_kind == AggKind.MONTH:
        return [
            last_day.get_shifted(relativedelta(months=delta)).get_truncated_value(
                agg_kind=AggKind.MONTH
            )
            for delta in range(-2, 1)  # last 3 months
        ]
    elif agg_kind == AggKind.WEEK:
        return [
            last_day.get_shifted(relativedelta(weeks=delta)).get_truncated_value(
                agg_kind=AggKind.WEEK
            )
            for delta in range(-3, 1)  # last 4 weeks
        ]
    elif agg_kind == AggKind.DAY:  # pragma: no branch
        return [
            last_day.get_shifted(relativedelta(days=delta)).get_truncated_value(
                agg_kind=AggKind.DAY
            )
            for delta in range(-6, 1)  # last 7 days
        ]
