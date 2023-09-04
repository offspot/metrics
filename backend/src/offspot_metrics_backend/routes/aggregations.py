from dataclasses import dataclass

from fastapi import APIRouter
from sqlalchemy import select

from offspot_metrics_backend.db.models import KpiValue
from offspot_metrics_backend.routes import DbSession

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
    aggregations: list[Aggregation]


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
    query = select(KpiValue.agg_kind, KpiValue.agg_value).distinct()

    return Aggregations(
        aggregations=[
            Aggregation(kind=x.agg_kind, value=x.agg_value)
            for x in session.execute(query)
        ]
    )
