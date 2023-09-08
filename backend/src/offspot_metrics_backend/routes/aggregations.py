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
    """One aggregation value with its kind"""

    kind: str
    value: str


@dataclass
class Aggregations:
    """A list of aggregation values

    This is mandatory to not return a list as top Json object since it is not
    recommended for security reasons in Javascript"""

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
            Aggregation(kind=record.agg_kind, value=record.agg_value)
            for record in session.execute(query)
        ]
    )
