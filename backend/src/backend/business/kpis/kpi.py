import abc


class Kpi(abc.ABC):
    """A generic KPI interface"""

    unique_id = 0  # this ID is unique to each kind of kpi

    @abc.abstractmethod
    def get_value(self, kind: str, start_ts: int, stop_ts: int) -> str:
        """For a kind of aggregation (daily, weekly, ...) and a given period, return
        the KPI value."""
        ...  # pragma: nocover
