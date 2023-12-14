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
