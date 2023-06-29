from dataclasses import dataclass
from typing import List

from fastapi import APIRouter
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
