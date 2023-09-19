import abc
from typing import Any

from sqlalchemy.orm import Session

from offspot_metrics_backend.business.agg_kind import AggKind


class Kpi(abc.ABC):
    """A generic KPI interface"""

    unique_id = 2000  # this ID is unique to each kind of kpi

    @abc.abstractmethod
    def compute_value_from_indicators(
        self, agg_kind: AggKind, start_ts: int, stop_ts: int, session: Session
    ) -> Any:
        """For a kind of aggregation (daily, weekly, ...) and a given period, compute
        the KPI value based on indicators present in DB."""
        ...  # pragma: no cover
