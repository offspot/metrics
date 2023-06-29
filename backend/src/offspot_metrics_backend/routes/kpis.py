from dataclasses import dataclass
from typing import List

from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import dbsession
from ..db.models import KpiValue

router = APIRouter(
    prefix="/kpis",
    tags=["all"],
)


@dataclass
class Kpi:
    id: int
    value: str


@router.get(
    "",
    status_code=200,
    responses={
        200: {
            "description": "Returns all kpis available for a given aggregation",
        },
    },
)
async def kpis(agg_kind: str, agg_value: str) -> List[Kpi]:
    return kpis_inner(agg_kind=agg_kind, agg_value=agg_value)


@dbsession
def kpis_inner(agg_kind: str, agg_value: str, session: Session) -> List[Kpi]:
    query = (
        select(KpiValue.kpi_id, KpiValue.kpi_value)
        .where(KpiValue.agg_value == agg_value)
        .where(KpiValue.agg_kind == agg_kind)
    )

    return list(
        map(
            lambda x: Kpi(id=x.kpi_id, value=x.kpi_value),
            session.execute(query),
        )
    )


# TODO: specify the 404 response model
@router.get(
    "/{kpi_id}",
    responses={
        200: {
            "description": "Returns the kpi value for a given aggregation",
        },
        404: {"description": "KPI not found"},
    },
)
async def kpi(kpi_id: str, agg_kind: str, agg_value: str) -> Kpi | None:
    return kpi_inner(kpi_id=kpi_id, agg_kind=agg_kind, agg_value=agg_value)


@dbsession
def kpi_inner(kpi_id: str, agg_kind: str, agg_value: str, session: Session) -> Kpi:
    query = (
        select(KpiValue.kpi_id, KpiValue.kpi_value)
        .where(KpiValue.kpi_id == kpi_id)
        .where(KpiValue.agg_value == agg_value)
        .where(KpiValue.agg_kind == agg_kind)
    )

    item = session.execute(query).first()
    if not item:
        raise HTTPException(
            status_code=404,
            detail="KPI not found",
        )

    return Kpi(id=item.kpi_id, value=item.kpi_value)
