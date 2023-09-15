from dataclasses import dataclass
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import select

from offspot_metrics_backend.business.agg_kind import AggKind
from offspot_metrics_backend.db.models import KpiRecord, KpiValue as DbKpiValue
from offspot_metrics_backend.routes import DbSession

router = APIRouter(
    prefix="/kpis",
    tags=["all"],
)


@dataclass
class KpiValue:
    """A KPI value with its ID"""

    kpi_id: int
    value: DbKpiValue


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
) -> KpiValue:
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

    return KpiValue(kpi_id=item.kpi_id, value=item.kpi_value)
