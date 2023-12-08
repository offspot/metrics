from typing import Any

from offspot_metrics_backend.business.agg_kind import AggKind
from offspot_metrics_backend.business.schemas import CamelModel


class KpiValue(CamelModel):
    """A KPI value with its ID"""

    kpi_id: int
    value: Any


class Aggregation(CamelModel):
    """One aggregation value with its kind"""

    kind: str
    value: str


class Aggregations(CamelModel):
    """A list of aggregation values

    This is mandatory to not return a list as top Json object since it is not
    recommended for security reasons in Javascript"""

    aggregations: list[Aggregation]


class AggregationsByKind(CamelModel):
    """Details about all aggregations of a given kind"""

    agg_kind: AggKind
    aggregations: list["AggregationWithKpis"]

    class AggregationWithKpis(CamelModel):
        agg_value: str
        kpis: list[KpiValue]
