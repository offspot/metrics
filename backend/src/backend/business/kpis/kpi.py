import abc

from sqlalchemy.orm import Session


class Kpi(abc.ABC):
    """A generic KPI interface"""

    unique_id = 0  # this ID is unique to each kind of kpi

    @abc.abstractmethod
    def get_value(
        self, kind: str, start_ts: int, stop_ts: int, session: Session
    ) -> str:
        """For a kind of aggregation (daily, weekly, ...) and a given period, return
        the KPI value."""
        ...  # pragma: nocover
