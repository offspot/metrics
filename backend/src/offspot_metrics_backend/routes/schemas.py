from typing import Any

from offspot_metrics_backend.business.agg_kind import AggKind
from offspot_metrics_backend.business.schemas import CamelModel


class KpiValueById(CamelModel):
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
    values_available: list[str]
    kpis: list["KpiValues"]

    class KpiValueByAggregation(CamelModel):
        agg_value: str
        kpi_value: Any

    class KpiValues(CamelModel):
        kpi_id: int
        values: list["AggregationsByKind.KpiValueByAggregation"]
