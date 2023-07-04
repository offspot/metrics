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


@dataclass
class Aggregations:  # simply to not return an array as root JSON object
    aggregations: List[Aggregation]


@router.get(
    "",
    status_code=200,
    responses={
        200: {
            "description": "Returns the list of available aggregations",
        },
    },
)
async def aggregations() -> Aggregations:
    return aggregations_inner()


@dbsession
def aggregations_inner(session: Session) -> Aggregations:
    query = select(KpiValue.agg_kind, KpiValue.agg_value).distinct()

    return Aggregations(
        aggregations=list(
            map(
                lambda x: Aggregation(kind=x.agg_kind, value=x.agg_value),
                session.execute(query),
            )
        )
    )
