from dataclasses import dataclass
from typing import List

from fastapi import APIRouter
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import dbsession
from ..db.models import KpiValue

router = APIRouter(
    prefix="/aggregations",
    tags=["all"],
)


@dataclass
class Aggregation:
    kind: str
    value: str


@router.get(
    "",
    status_code=200,
    responses={
        200: {
            "description": "Returns the list of available aggregations",
        },
    },
)
async def aggregations() -> List[Aggregation]:
    return aggregations_inner()


@dbsession
def aggregations_inner(session: Session) -> List[Aggregation]:
    query = select(KpiValue.agg_kind, KpiValue.agg_value).distinct()

    return list(
        map(
            lambda x: Aggregation(kind=x.agg_kind, value=x.agg_value),
            session.execute(query),
        )
    )
