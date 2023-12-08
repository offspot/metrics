from typing import Annotated

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import select

from offspot_metrics_backend.business.agg_kind import AggKind
from offspot_metrics_backend.db.models import KpiRecord
from offspot_metrics_backend.routes import DbSession
from offspot_metrics_backend.routes.schemas import KpiValueById

router = APIRouter(
    prefix="/kpis",
    tags=["all"],
)


@router.get(
    "/{kpi_id}/values",
    responses={
        200: {
            "description": "Returns the kpi values for a given aggregation",
        },
        404: {"description": "KPI not found"},
    },
)
async def kpi_values(
    kpi_id: str,
    agg_kind: Annotated[str, Query(pattern=AggKind.pattern())],
    agg_value: Annotated[str, Query()],
    session: DbSession,
) -> KpiValueById:
    query = (
        select(KpiRecord.kpi_id, KpiRecord.kpi_value)
        .where(KpiRecord.kpi_id == kpi_id)
        .where(KpiRecord.agg_value == agg_value)
        .where(KpiRecord.agg_kind == agg_kind)
    )

    item = session.execute(query).first()
    if not item:
        raise HTTPException(
            status_code=404,
            detail="KPI not found",
        )

    return KpiValueById(kpi_id=item.kpi_id, value=item.kpi_value)
