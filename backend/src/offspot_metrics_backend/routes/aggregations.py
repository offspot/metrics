from typing import Annotated

from fastapi import APIRouter, Path
from sqlalchemy import select

from offspot_metrics_backend.business.agg_kind import AggKind
from offspot_metrics_backend.db.models import KpiRecord
from offspot_metrics_backend.routes import DbSession
from offspot_metrics_backend.routes.schemas import (
    Aggregation,
    Aggregations,
    AggregationsByKind,
    KpiValue,
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

    return AggregationsByKind(
        agg_kind=AggKind(agg_kind),
        aggregations=[
            AggregationsByKind.AggregationWithKpis(
                agg_value=agg_value,
                kpis=sorted(
                    [
                        KpiValue(kpi_id=record.kpi_id, value=record.kpi_value)
                        for record in records
                        if record.agg_value == agg_value
                    ],
                    key=lambda kpi: kpi.kpi_id,
                ),
            )
            for agg_value in agg_values
        ],
    )
