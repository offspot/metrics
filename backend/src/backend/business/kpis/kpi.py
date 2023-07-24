import abc

from sqlalchemy.orm import Session

from ..agg_kind import AggKind


class Kpi(abc.ABC):
    """A generic KPI interface"""

    unique_id = 2000  # this ID is unique to each kind of kpi

    @abc.abstractmethod
    def get_value(
        self, agg_kind: AggKind, start_ts: int, stop_ts: int, session: Session
    ) -> str:
        """For a kind of aggregation (daily, weekly, ...) and a given period, return
        the KPI value."""
        ...  # pragma: nocover
