from pydantic.dataclasses import dataclass

from offspot_metrics_backend.db.models import KpiValue


@dataclass
class Value:
    """A dataclass to hold KPI value for a given aggregation value"""

    agg_value: str
    kpi_value: KpiValue
