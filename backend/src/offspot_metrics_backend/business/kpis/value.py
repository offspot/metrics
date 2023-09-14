from dataclasses import dataclass
from typing import Any


@dataclass
class Value:
    """A dataclass to hold KPI value for a given aggregation value"""

    agg_value: str
    kpi_value: Any
