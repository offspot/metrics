from dataclasses import dataclass

from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from offspot_metrics_backend.db import dbsession
from offspot_metrics_backend.db.models import KpiValue as DbKpiValue

router = APIRouter(
    prefix="/kpis",
    tags=["all"],
)


@dataclass
class WebKpiValue:
    kpi_id: int
    value: str


@router.get(
    "/{kpi_id}/values",
    responses={
        200: {
            "description": "Returns the kpi value for a given aggregation",
        },
        404: {"description": "KPI not found"},
    },
)
async def kpi_values(kpi_id: str, agg_kind: str, agg_value: str) -> WebKpiValue:
    return kpi_values_inner(kpi_id=kpi_id, agg_kind=agg_kind, agg_value=agg_value)


@dbsession
def kpi_values_inner(
    kpi_id: str, agg_kind: str, agg_value: str, session: Session
) -> WebKpiValue:
    query = (
        select(DbKpiValue.kpi_id, DbKpiValue.kpi_value)
        .where(DbKpiValue.kpi_id == kpi_id)
        .where(DbKpiValue.agg_value == agg_value)
        .where(DbKpiValue.agg_kind == agg_kind)
    )

    item = session.execute(query).first()
    if not item:
        raise HTTPException(
            status_code=404,
            detail="KPI not found",
        )

    return WebKpiValue(kpi_id=item.kpi_id, value=item.kpi_value)
